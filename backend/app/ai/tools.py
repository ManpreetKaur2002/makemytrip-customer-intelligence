import re
from datetime import date
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import (
    Booking,
    Customer,
    CustomerAIInsight,
    CustomerPreference,
    SupportCase,
)
from app.schemas.booking import BookingCreate
from app.schemas.support_case import SupportCaseCreate
from app.services.booking_service import create_booking
from app.services.support_service import create_support_case

TOOL_DEFINITIONS: list[dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "get_travel_profile",
            "description": "Read this customer's preferences and saved travel insights.",
            "parameters": {
                "type": "object",
                "properties": {},
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_bookings",
            "description": "List this customer's bookings and their statuses.",
            "parameters": {
                "type": "object",
                "properties": {"status": {"type": "string"}},
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_support_cases",
            "description": "List this customer's support cases.",
            "parameters": {
                "type": "object",
                "properties": {"status": {"type": "string"}},
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_booking_request",
            "description": "Record a pending demo booking only after the customer explicitly confirms a complete itinerary.",
            "parameters": {
                "type": "object",
                "properties": {
                    "booking_type": {
                        "type": "string",
                        "enum": ["flight", "hotel", "holiday", "train", "bus"],
                    },
                    "origin": {"type": ["string", "null"]},
                    "destination": {"type": "string"},
                    "departure_date": {
                        "type": "string",
                        "description": "ISO date YYYY-MM-DD.",
                    },
                    "return_date": {
                        "type": ["string", "null"],
                        "description": "ISO date YYYY-MM-DD.",
                    },
                    "amount": {"type": ["number", "null"]},
                    "currency": {"type": "string", "default": "INR"},
                },
                "required": ["booking_type", "destination", "departure_date"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_support_case",
            "description": "Open a support case when the customer asks for an issue to be tracked or escalated.",
            "parameters": {
                "type": "object",
                "properties": {
                    "issue_type": {"type": "string"},
                    "description": {"type": "string"},
                    "priority": {"type": "string", "enum": ["low", "medium", "high"]},
                    "booking_id": {"type": ["string", "null"]},
                },
                "required": ["issue_type", "description"],
                "additionalProperties": False,
            },
        },
    },
]


def _is_explicit_confirmation(message: str) -> bool:
    normalized = re.sub(r"[^a-z ]", "", message.lower()).strip()
    return normalized in {
        "yes",
        "yes please",
        "yes confirm",
        "yes confirm it",
        "confirm",
        "confirm booking",
        "confirm it",
        "go ahead",
        "proceed",
        "book it",
        "do it",
        "looks good",
        "thats right",
    }


def execute_tool(
    db: Session,
    customer_id: UUID,
    user_message: str,
    name: str,
    arguments: dict[str, Any],
) -> dict[str, Any]:
    if name == "get_travel_profile":
        preference = db.scalar(
            select(CustomerPreference).where(
                CustomerPreference.customer_id == customer_id
            )
        )
        insights = db.scalars(
            select(CustomerAIInsight)
            .where(CustomerAIInsight.customer_id == customer_id)
            .order_by(CustomerAIInsight.generated_at.desc())
            .limit(10)
        ).all()
        return {
            "preferences": {
                "min_budget": (
                    str(preference.min_budget)
                    if preference and preference.min_budget is not None
                    else None
                ),
                "max_budget": (
                    str(preference.max_budget)
                    if preference and preference.max_budget is not None
                    else None
                ),
                "currency": preference.currency if preference else None,
                "destinations": preference.preferred_destinations if preference else [],
                "hotel_category": (
                    preference.preferred_hotel_category if preference else None
                ),
                "travel_style": preference.travel_style if preference else None,
                "preferred_seat": preference.preferred_seat if preference else None,
                "dietary_preferences": (
                    preference.dietary_preferences if preference else []
                ),
            },
            "insights": [
                {
                    "type": item.insight_type,
                    "text": item.insight_text,
                    "confidence": (
                        float(item.confidence) if item.confidence is not None else None
                    ),
                }
                for item in insights
            ],
        }

    if name == "list_bookings":
        statement = select(Booking).where(Booking.customer_id == customer_id)
        if arguments.get("status"):
            statement = statement.where(Booking.booking_status == arguments["status"])
        rows = db.scalars(statement.order_by(Booking.created_at.desc()).limit(30)).all()
        return [
            {
                "booking_reference": row.booking_reference,
                "type": row.booking_type,
                "origin": row.origin,
                "destination": row.destination,
                "departure_date": (
                    row.departure_date.isoformat() if row.departure_date else None
                ),
                "return_date": row.return_date.isoformat() if row.return_date else None,
                "status": row.booking_status,
                "amount": str(row.amount) if row.amount is not None else None,
                "currency": row.currency,
            }
            for row in rows
        ]

    if name == "list_support_cases":
        statement = select(SupportCase).where(SupportCase.customer_id == customer_id)
        if arguments.get("status"):
            statement = statement.where(SupportCase.case_status == arguments["status"])
        rows = db.scalars(
            statement.order_by(SupportCase.created_at.desc()).limit(30)
        ).all()
        return [
            {
                "case_id": str(row.case_id),
                "issue_type": row.issue_type,
                "description": row.description,
                "status": row.case_status,
                "priority": row.priority,
                "resolution": row.resolution,
            }
            for row in rows
        ]

    if name == "create_booking_request":
        if not _is_explicit_confirmation(user_message):
            return {
                "status": "confirmation_required",
                "message": "Summarize the itinerary and ask for explicit customer confirmation before creating anything.",
                "itinerary": arguments,
            }
        reference = f"MMT-{date.today():%y%m%d}-{uuid4().hex[:6].upper()}"
        booking = create_booking(
            db,
            BookingCreate(
                customer_id=customer_id,
                booking_reference=reference,
                booking_type=arguments["booking_type"],
                origin=arguments.get("origin"),
                destination=arguments["destination"],
                departure_date=arguments["departure_date"],
                return_date=arguments.get("return_date"),
                amount=arguments.get("amount"),
                currency=arguments.get("currency", "INR"),
                booking_status="pending",
            ),
        )
        return {
            "status": "pending",
            "booking_reference": booking.booking_reference,
            "message": "A pending demo booking request was recorded. No supplier ticket was issued.",
        }

    if name == "create_support_case":
        booking_id = arguments.get("booking_id")
        if booking_id:
            booking = db.get(Booking, UUID(booking_id))
            if booking is None or booking.customer_id != customer_id:
                return {"error": "That booking was not found on this customer profile."}
        support_case = create_support_case(
            db,
            SupportCaseCreate(
                customer_id=customer_id,
                booking_id=UUID(booking_id) if booking_id else None,
                issue_type=arguments["issue_type"],
                description=arguments["description"],
                priority=arguments.get("priority", "medium"),
            ),
        )
        return {
            "status": "open",
            "case_id": str(support_case.case_id),
            "message": "The support case was opened.",
        }

    return {"error": f"Unknown tool: {name}"}


def local_reply(db: Session, customer: Customer, message: str) -> str:
    lowered = message.lower()
    if any(
        term in lowered
        for term in ("booking", "reservation", "trip", "flight", "hotel")
    ):
        bookings = execute_tool(db, customer.customer_id, message, "list_bookings", {})
        if bookings:
            return "Here are the bookings on your profile:\n\n" + "\n".join(
                f"- {item['type'].title()} to {item['destination'] or 'an unlisted destination'} "
                f"({item['departure_date'] or 'date not set'}, "
                f"{item['booking_reference'] or 'reference pending'}) is {item['status']}"
                for item in bookings
            )
        return "There are no bookings on your profile yet. Tell me the trip type, destination and travel dates to get started."
    if any(
        term in lowered
        for term in ("support", "case", "refund", "cancel", "issue", "problem")
    ):
        cases = execute_tool(
            db, customer.customer_id, message, "list_support_cases", {}
        )
        if cases:
            return "I found these support cases:\n\n" + "\n".join(
                f"- {item['issue_type'].replace('_', ' ').title()} · {item['status']} · {item['description'] or 'No details'}"
                for item in cases
            )
        return "There are no support cases on your profile. Describe the issue and I can help prepare one for the support team."
    if any(
        term in lowered
        for term in ("preference", "recommend", "insight", "like", "budget")
    ):
        profile = execute_tool(
            db, customer.customer_id, message, "get_travel_profile", {}
        )
        preferences = profile["preferences"]
        if (
            preferences["destinations"]
            or preferences["travel_style"]
            or profile["insights"]
        ):
            details = []
            if preferences["destinations"]:
                details.append(
                    "Saved destinations: " + ", ".join(preferences["destinations"])
                )
            if preferences["travel_style"]:
                details.append("Travel style: " + preferences["travel_style"])
            details.extend(item["text"] for item in profile["insights"][:3])
            return "Here’s the travel context saved to your profile:\n\n" + "\n".join(
                f"- {line}" for line in details
            )
        return "I don’t have travel preferences saved yet. Add your preferred destinations, budget or travel style to your profile so I can tailor suggestions."
    return (
        f"Hi {customer.full_name.split()[0]}, I can help with your bookings, travel preferences, "
        "refunds and support cases. The full AI model is not configured yet, so I’m using profile-aware local responses."
    )
