import json
import logging
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

import httpx
from sqlalchemy import case, select
from sqlalchemy.orm import Session

from app.ai.tools import TOOL_DEFINITIONS, execute_tool, local_reply
from app.core.config import settings
from app.models import ChatMessage, ChatSession, Customer

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are the MakeMyTrip travel assistant for the signed-in customer in this chat.
Use persisted chat history and tools for customer profile, booking, and support facts. Never invent booking status, prices, availability, refund outcomes, or policies. The booking tool creates only a pending demo request; it does not issue a supplier ticket. Before calling it, collect trip type, destination and departure date, summarize the itinerary, and wait for explicit confirmation. Open a support case only when the customer asks for an issue to be tracked or escalated. Keep replies concise, empathetic, and use the customer's preferred language when practical."""


def _history_for_model(db: Session, session_id: UUID) -> list[dict[str, Any]]:
    rows = db.scalars(
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
    messages: list[dict[str, Any]] = [{"role": "system", "content": SYSTEM_PROMPT}]
    for row in rows:
        message: dict[str, Any] = {"role": row.role}
        if row.content is not None:
            message["content"] = row.content
        if row.tool_calls is not None:
            message["tool_calls"] = row.tool_calls
        if row.tool_call_id is not None:
            message["tool_call_id"] = row.tool_call_id
        if row.role == "tool":
            message.setdefault("content", "")
        messages.append(message)
    return messages


def _call_model(messages: list[dict[str, Any]]) -> dict[str, Any]:
    response = httpx.post(
        f"{settings.ai_base_url.rstrip('/')}/chat/completions",
        headers={"Authorization": f"Bearer {settings.ai_api_key}"},
        json={
            "model": settings.ai_model,
            "messages": messages,
            "tools": TOOL_DEFINITIONS,
            "tool_choice": "auto",
        },
        timeout=45,
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]


def generate_reply(
    db: Session, session: ChatSession, customer: Customer, user_message: str
) -> str:
    if not settings.ai_api_key:
        return local_reply(db, customer, user_message)

    messages = _history_for_model(db, session.session_id)
    try:
        for _ in range(6):
            assistant_message = _call_model(messages)
            tool_calls = assistant_message.get("tool_calls") or []
            if not tool_calls:
                return (
                    assistant_message.get("content")
                    or "I’m here to help with your trip."
                ).strip()

            db.add(
                ChatMessage(
                    session_id=session.session_id,
                    role="assistant",
                    content=assistant_message.get("content"),
                    tool_calls=tool_calls,
                    created_at=datetime.now(UTC),
                )
            )
            messages.append(
                {
                    "role": "assistant",
                    "content": assistant_message.get("content"),
                    "tool_calls": tool_calls,
                }
            )
            for tool_call in tool_calls:
                function = tool_call["function"]
                try:
                    arguments = json.loads(function.get("arguments") or "{}")
                    result = execute_tool(
                        db,
                        customer.customer_id,
                        user_message,
                        function["name"],
                        arguments,
                    )
                except (KeyError, TypeError, ValueError) as error:
                    result = {"error": str(error)}
                tool_content = json.dumps(result, ensure_ascii=True, default=str)
                db.add(
                    ChatMessage(
                        session_id=session.session_id,
                        role="tool",
                        content=tool_content,
                        tool_call_id=tool_call["id"],
                        created_at=datetime.now(UTC),
                    )
                )
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call["id"],
                        "content": tool_content,
                    }
                )
            db.commit()
    except httpx.TimeoutException as error:
        db.rollback()
        logger.warning(
            "Hosted AI request timed out (model=%s, error_type=%s)",
            settings.ai_model,
            type(error).__name__,
        )
        return "I’ve saved your message, but the assistant service is unavailable right now. Please try again shortly."
    except httpx.HTTPStatusError as error:
        db.rollback()
        logger.warning(
            "Hosted AI request was rejected (model=%s, status_code=%s)",
            settings.ai_model,
            error.response.status_code,
        )
        return "I’ve saved your message, but the assistant service is unavailable right now. Please try again shortly."
    except httpx.HTTPError as error:
        db.rollback()
        logger.warning(
            "Hosted AI transport failed (model=%s, error_type=%s)",
            settings.ai_model,
            type(error).__name__,
        )
        return "I’ve saved your message, but the assistant service is unavailable right now. Please try again shortly."
    except (KeyError, IndexError, TypeError, ValueError) as error:
        db.rollback()
        logger.exception(
            "Hosted AI response could not be processed (model=%s, error_type=%s)",
            settings.ai_model,
            type(error).__name__,
        )
        return "I’ve saved your message, but the assistant service is unavailable right now. Please try again shortly."

    return "I’m sorry, I couldn’t complete that request. Your conversation is saved; please try a simpler question."
