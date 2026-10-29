from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CustomerPreferenceBase(BaseModel):
    min_budget: Decimal | None = Field(
        default=None, ge=0, max_digits=12, decimal_places=2
    )
    max_budget: Decimal | None = Field(
        default=None, ge=0, max_digits=12, decimal_places=2
    )
    currency: str = Field(default="INR", min_length=3, max_length=3)
    preferred_destinations: list[Any] = Field(default_factory=list)
    preferred_hotel_category: str | None = Field(default=None, max_length=30)
    travel_style: str | None = Field(default=None, max_length=50)
    preferred_seat: str | None = Field(default=None, max_length=30)
    dietary_preferences: list[Any] = Field(default_factory=list)


class CustomerPreferenceCreate(CustomerPreferenceBase):
    customer_id: UUID


class CustomerPreferenceRead(CustomerPreferenceBase):
    model_config = ConfigDict(from_attributes=True)

    preference_id: UUID
    customer_id: UUID
    updated_at: datetime


class CustomerPreferenceUpdate(CustomerPreferenceBase):
    min_budget: Decimal | None = Field(
        default=None, ge=0, max_digits=12, decimal_places=2
    )
    max_budget: Decimal | None = Field(
        default=None, ge=0, max_digits=12, decimal_places=2
    )
