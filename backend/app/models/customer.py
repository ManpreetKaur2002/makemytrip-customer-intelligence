from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import DateTime, String, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.booking import Booking
    from app.models.customer_ai_insight import CustomerAIInsight
    from app.models.customer_preference import CustomerPreference
    from app.models.support_case import SupportCase


class Customer(Base):
    __tablename__ = "customers"

    customer_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid4
    )
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), unique=True)
    phone: Mapped[str | None] = mapped_column(String(30))
    preferred_language: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default="en"
    )
    account_status: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default="active"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    preference: Mapped["CustomerPreference | None"] = relationship(
        back_populates="customer", cascade="all, delete-orphan", uselist=False
    )
    bookings: Mapped[list["Booking"]] = relationship(back_populates="customer")
    support_cases: Mapped[list["SupportCase"]] = relationship(back_populates="customer")
    ai_insights: Mapped[list["CustomerAIInsight"]] = relationship(
        back_populates="customer", cascade="all, delete-orphan"
    )
