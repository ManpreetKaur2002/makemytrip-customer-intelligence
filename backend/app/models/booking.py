from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    Uuid,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.customer import Customer
    from app.models.support_case import SupportCase


class Booking(Base):
    __tablename__ = "bookings"
    __table_args__ = (
        CheckConstraint("amount IS NULL OR amount >= 0", name="ck_bookings_amount"),
        CheckConstraint(
            "return_date IS NULL OR departure_date IS NULL OR return_date >= departure_date",
            name="ck_bookings_dates",
        ),
        Index("idx_bookings_customer_date", "customer_id", "created_at"),
        Index("idx_bookings_destination", "destination"),
    )

    booking_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid4
    )
    customer_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("customers.customer_id"), nullable=False
    )
    booking_reference: Mapped[str | None] = mapped_column(String(100), unique=True)
    booking_type: Mapped[str] = mapped_column(String(30), nullable=False)
    origin: Mapped[str | None] = mapped_column(String(150))
    destination: Mapped[str | None] = mapped_column(String(150))
    departure_date: Mapped[date | None] = mapped_column(Date)
    return_date: Mapped[date | None] = mapped_column(Date)
    amount: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    currency: Mapped[str] = mapped_column(
        String(3), nullable=False, server_default="INR"
    )
    booking_status: Mapped[str] = mapped_column(
        String(30), nullable=False, server_default="pending"
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

    customer: Mapped["Customer"] = relationship(back_populates="bookings")
    support_cases: Mapped[list["SupportCase"]] = relationship(back_populates="booking")
