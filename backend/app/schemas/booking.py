from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class BookingBase(BaseModel):
    booking_reference: str | None = Field(default=None, max_length=100)
    booking_type: str = Field(min_length=1, max_length=30)
    origin: str | None = Field(default=None, max_length=150)
    destination: str | None = Field(default=None, max_length=150)
    departure_date: date | None = None
    return_date: date | None = None
    amount: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2)
    currency: str = Field(default="INR", min_length=3, max_length=3)
    booking_status: str = Field(default="pending", max_length=30)

    @model_validator(mode="after")
    def check_date_range(self) -> "BookingBase":
        if (
            self.departure_date
            and self.return_date
            and self.return_date < self.departure_date
        ):
            raise ValueError("return_date cannot be before departure_date")
        return self


class BookingCreate(BookingBase):
    customer_id: UUID


class BookingRead(BookingBase):
    model_config = ConfigDict(from_attributes=True)

    booking_id: UUID
    customer_id: UUID
    created_at: datetime
    updated_at: datetime


class BookingUpdate(BaseModel):
    booking_reference: str | None = Field(default=None, max_length=100)
    booking_type: str | None = Field(default=None, min_length=1, max_length=30)
    origin: str | None = Field(default=None, max_length=150)
    destination: str | None = Field(default=None, max_length=150)
    departure_date: date | None = None
    return_date: date | None = None
    amount: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2)
    currency: str | None = Field(default=None, min_length=3, max_length=3)
    booking_status: str | None = Field(default=None, max_length=30)
