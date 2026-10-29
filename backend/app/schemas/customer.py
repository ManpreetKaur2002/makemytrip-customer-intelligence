from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class CustomerBase(BaseModel):
    full_name: str = Field(min_length=1, max_length=150)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=30)
    preferred_language: str = Field(default="en", max_length=20)
    account_status: str = Field(default="active", max_length=20)


class CustomerCreate(CustomerBase):
    pass


class CustomerRead(CustomerBase):
    model_config = ConfigDict(from_attributes=True)

    customer_id: UUID
    created_at: datetime
    updated_at: datetime


class CustomerUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=1, max_length=150)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=30)
    preferred_language: str | None = Field(default=None, max_length=20)
    account_status: str | None = Field(default=None, max_length=20)
