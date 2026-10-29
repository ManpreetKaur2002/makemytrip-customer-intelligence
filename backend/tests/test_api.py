from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app import main as main_module
from app.core.config import settings
from app.db.base import Base
from app.db.database import get_db
from app.main import app


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> Generator[TestClient, None, None]:
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    test_session = sessionmaker(bind=test_engine, autoflush=False, autocommit=False)
    monkeypatch.setattr(main_module, "engine", test_engine)
    monkeypatch.setattr(settings, "ai_api_key", None)

    def override_get_db() -> Generator[Session, None, None]:
        db = test_session()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    test_engine.dispose()


def test_all_api_routes(client: TestClient) -> None:
    health = client.get("/health")
    assert health.status_code == 200
    assert health.json() == {"status": "ok"}

    customer_response = client.post(
        "/customers",
        json={
            "full_name": "API Test Customer",
            "email": "api-test-customer@example.com",
            "phone": "+919876543210",
        },
    )
    assert customer_response.status_code == 201
    customer = customer_response.json()
    customer_id = customer["customer_id"]
    assert client.get(f"/customers/{customer_id}").status_code == 200
    assert (
        client.get("/customers?search=API%20Test").json()[0]["customer_id"]
        == customer_id
    )
    assert (
        client.patch(
            f"/customers/{customer_id}", json={"preferred_language": "hi"}
        ).json()["preferred_language"]
        == "hi"
    )

    preference_response = client.put(
        f"/preferences/{customer_id}",
        json={
            "min_budget": 1000,
            "max_budget": 5000,
            "currency": "INR",
            "preferred_destinations": ["Goa"],
            "travel_style": "leisure",
            "dietary_preferences": ["vegetarian"],
        },
    )
    assert preference_response.status_code == 200
    assert client.get(f"/preferences/{customer_id}").json()[
        "preferred_destinations"
    ] == ["Goa"]

    booking_response = client.post(
        "/bookings",
        json={
            "customer_id": customer_id,
            "booking_reference": "MMT-API-TEST-1",
            "booking_type": "flight",
            "origin": "Delhi",
            "destination": "Goa",
            "departure_date": "2026-12-10",
            "return_date": "2026-12-15",
            "amount": 12500,
            "currency": "INR",
            "booking_status": "pending",
        },
    )
    assert booking_response.status_code == 201
    booking = booking_response.json()
    booking_id = booking["booking_id"]
    assert client.get(f"/bookings/{booking_id}").status_code == 200
    assert (
        client.get(f"/bookings?customer_id={customer_id}").json()[0]["booking_id"]
        == booking_id
    )
    assert (
        client.patch(
            f"/bookings/{booking_id}", json={"booking_status": "confirmed"}
        ).json()["booking_status"]
        == "confirmed"
    )

    case_response = client.post(
        "/support-cases",
        json={
            "customer_id": customer_id,
            "booking_id": booking_id,
            "issue_type": "booking_change",
            "description": "Need to update the return date.",
            "priority": "high",
        },
    )
    assert case_response.status_code == 201
    case_id = case_response.json()["case_id"]
    assert client.get(f"/support-cases/{case_id}").status_code == 200
    assert (
        client.get("/support-cases?status=open&priority=high").json()[0]["case_id"]
        == case_id
    )
    assert (
        client.patch(
            f"/support-cases/{case_id}",
            json={"case_status": "resolved", "resolution": "Return date updated."},
        ).json()["case_status"]
        == "resolved"
    )

    insight_response = client.post(
        "/ai-insights",
        json={
            "customer_id": customer_id,
            "insight_type": "destination_interest",
            "insight_text": "Customer is interested in beach destinations.",
            "confidence": 0.875,
            "evidence": {"message_count": 2},
        },
    )
    assert insight_response.status_code == 201
    assert (
        client.get(f"/ai-insights?customer_id={customer_id}").json()[0]["insight_id"]
        == insight_response.json()["insight_id"]
    )

    assert client.get("/chat/sessions").status_code == 401
    register_response = client.post(
        "/auth/register",
        json={
            "full_name": "Chat Test Customer",
            "email": "chat-test-customer@example.com",
            "password": "CorrectHorseBattery123!",
        },
    )
    assert register_response.status_code == 201
    chat_customer_id = register_response.json()["customer_id"]
    assert "customer_session=" in register_response.headers["set-cookie"]
    assert client.get("/auth/me").json()["customer_id"] == chat_customer_id

    session_response = client.post("/chat/sessions", json={"title": "Booking help"})
    assert session_response.status_code == 201
    session_id = session_response.json()["session_id"]
    chat_response = client.post(
        "/chat/messages",
        json={"session_id": session_id, "message": "Show my bookings"},
    )
    assert chat_response.status_code == 200
    assert "no bookings" in chat_response.json()["reply"].lower()

    history = client.get(f"/chat/sessions/{session_id}/history")
    assert history.status_code == 200
    assert [message["role"] for message in history.json()["messages"]] == [
        "user",
        "assistant",
    ]
    assert client.get("/chat/sessions").json()[0]["session_id"] == session_id
    assert client.post("/auth/logout").status_code == 204
    assert client.get("/auth/me").status_code == 401
    assert client.get("/chat/sessions").status_code == 401

    login_response = client.post(
        "/auth/login",
        json={
            "email": "chat-test-customer@example.com",
            "password": "CorrectHorseBattery123!",
        },
    )
    assert login_response.status_code == 200
    assert client.get("/auth/me").json()["customer_id"] == chat_customer_id

    summary = client.get("/dashboard/summary")
    assert summary.status_code == 200
    assert summary.json() == {
        "customers": 2,
        "bookings": 1,
        "open_cases": 0,
        "ai_insights": 1,
    }
