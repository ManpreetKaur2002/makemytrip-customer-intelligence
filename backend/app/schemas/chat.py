from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


# Create a new conversation session
class ChatSessionCreate(BaseModel):
    title: str | None = Field(default=None, max_length=200)


# Return a conversation session
class ChatSessionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    session_id: UUID
    customer_id: UUID
    title: str | None
    status: str
    created_at: datetime
    updated_at: datetime


# Send a message to the AI agent
class ChatRequest(BaseModel):
    session_id: UUID | None = None
    message: str = Field(min_length=1, max_length=4000)


# Store or return a chat message
class ChatMessageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    message_id: UUID
    session_id: UUID
    role: str
    content: str | None
    tool_calls: dict[str, Any] | list[dict[str, Any]] | None = None
    tool_call_id: str | None = None
    created_at: datetime


# Return the AI agent's response
class ChatResponse(BaseModel):
    session_id: UUID
    reply: str


# Return a conversation's message history
class ChatHistoryResponse(BaseModel):
    session_id: UUID
    messages: list[ChatMessageRead]
