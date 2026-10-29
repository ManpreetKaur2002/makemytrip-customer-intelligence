from datetime import UTC, datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import case, select
from sqlalchemy.orm import Session

from app.ai.agent import generate_reply
from app.db.database import get_db
from app.models import ChatMessage, ChatSession, Customer
from app.security import get_current_customer
from app.schemas.chat import (
    ChatHistoryResponse,
    ChatMessageRead,
    ChatRequest,
    ChatResponse,
    ChatSessionCreate,
    ChatSessionRead,
)

router = APIRouter()


@router.get("/sessions", response_model=list[ChatSessionRead])
def list_sessions(
    db: Session = Depends(get_db),
    customer: Customer = Depends(get_current_customer),
) -> list[ChatSession]:
    return list(
        db.scalars(
            select(ChatSession)
            .where(
                ChatSession.customer_id == customer.customer_id,
                ChatSession.status == "active",
            )
            .order_by(ChatSession.updated_at.desc())
        ).all()
    )


@router.post("/sessions", response_model=ChatSessionRead, status_code=201)
def create_session(
    payload: ChatSessionCreate,
    db: Session = Depends(get_db),
    customer: Customer = Depends(get_current_customer),
) -> ChatSession:
    session = ChatSession(
        customer_id=customer.customer_id, title=payload.title or "Travel assistant"
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@router.get("/sessions/{session_id}/history", response_model=ChatHistoryResponse)
def get_history(
    session_id: UUID,
    db: Session = Depends(get_db),
    customer: Customer = Depends(get_current_customer),
) -> ChatHistoryResponse:
    session = db.get(ChatSession, session_id)
    if session is None or session.customer_id != customer.customer_id:
        raise HTTPException(status_code=404, detail="Chat session not found")
    messages = db.scalars(
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(
            ChatMessage.created_at.asc(),
            case(
                (ChatMessage.role == "user", 0),
                (ChatMessage.role == "assistant", 1),
                else_=2,
            ),
            ChatMessage.message_id.asc(),
        )
    ).all()
    return ChatHistoryResponse(
        session_id=session_id,
        messages=[ChatMessageRead.model_validate(message) for message in messages],
    )


@router.post("/messages", response_model=ChatResponse)
def send_message(
    payload: ChatRequest,
    db: Session = Depends(get_db),
    customer: Customer = Depends(get_current_customer),
) -> ChatResponse:
    content = payload.message.strip()
    if not content:
        raise HTTPException(status_code=422, detail="Message cannot be blank")

    session = db.get(ChatSession, payload.session_id) if payload.session_id else None
    if payload.session_id and (
        session is None or session.customer_id != customer.customer_id
    ):
        raise HTTPException(status_code=404, detail="Chat session not found")
    if session is None:
        session = ChatSession(
            customer_id=customer.customer_id, title=content[:200], status="active"
        )
        db.add(session)
        db.flush()
    elif not session.title or session.title == "New conversation":
        session.title = content[:200]

    db.add(
        ChatMessage(
            session_id=session.session_id,
            role="user",
            content=content,
            created_at=datetime.now(UTC),
        )
    )
    session.updated_at = datetime.now(UTC)
    db.commit()
    db.refresh(session)

    reply = generate_reply(db, session, customer, content)
    db.add(
        ChatMessage(
            session_id=session.session_id,
            role="assistant",
            content=reply,
            created_at=datetime.now(UTC),
        )
    )
    session.updated_at = datetime.now(UTC)
    db.commit()
    return ChatResponse(session_id=session.session_id, reply=reply)
