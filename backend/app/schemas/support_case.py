from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SupportCaseBase(BaseModel):
    issue_type: str = Field(min_length=1, max_length=50)
    description: str | None = None
    case_status: str = Field(default="open", max_length=30)
    priority: str = Field(default="medium", max_length=20)
    assigned_team: str | None = Field(default=None, max_length=100)
    resolution: str | None = None
    interaction_history: list[dict[str, Any]] = Field(default_factory=list)


class SupportCaseCreate(SupportCaseBase):
    customer_id: UUID
    booking_id: UUID | None = None


class SupportCaseRead(SupportCaseBase):
    model_config = ConfigDict(from_attributes=True)

    case_id: UUID
    customer_id: UUID
    booking_id: UUID | None
    created_at: datetime
    updated_at: datetime
    resolved_at: datetime | None


class SupportCaseUpdate(BaseModel):
    booking_id: UUID | None = None
    issue_type: str | None = Field(default=None, min_length=1, max_length=50)
    description: str | None = None
    case_status: str | None = Field(default=None, max_length=30)
    priority: str | None = Field(default=None, max_length=20)
    assigned_team: str | None = Field(default=None, max_length=100)
    resolution: str | None = None
    interaction_history: list[dict[str, Any]] | None = None
