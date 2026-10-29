from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CustomerAIInsightBase(BaseModel):
    insight_type: str = Field(min_length=1, max_length=50)
    insight_text: str
    confidence: Decimal | None = Field(
        default=None, ge=0, le=1, max_digits=4, decimal_places=3
    )
    evidence: dict[str, Any] = Field(default_factory=dict)
    expires_at: datetime | None = None
    model_version: str | None = Field(default=None, max_length=100)


class CustomerAIInsightCreate(CustomerAIInsightBase):
    customer_id: UUID


class CustomerAIInsightRead(CustomerAIInsightBase):
    model_config = ConfigDict(from_attributes=True)

    insight_id: UUID
    customer_id: UUID
    generated_at: datetime
