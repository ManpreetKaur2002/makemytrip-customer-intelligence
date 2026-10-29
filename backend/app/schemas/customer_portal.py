from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class CustomerSupportCaseCreate(BaseModel):
    booking_id: UUID | None = None
    issue_type: str = Field(min_length=1, max_length=50)
    description: str
    priority: str = Field(default="medium", max_length=20)
    interaction_history: list[dict[str, Any]] = Field(default_factory=list)
