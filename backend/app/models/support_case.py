from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import JSON, DateTime, ForeignKey, Index, String, Text, Uuid, func, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class SupportCase(Base):
    __tablename__ = "support_cases"
    __table_args__ = (
        Index("idx_support_customer_status", "customer_id", "case_status"),
    )

    case_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid4
    )
    customer_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("customers.customer_id"), nullable=False
    )
    booking_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("bookings.booking_id")
    )
    issue_type: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    case_status: Mapped[str] = mapped_column(
        String(30), nullable=False, server_default="open"
    )
    priority: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default="medium"
    )
    assigned_team: Mapped[str | None] = mapped_column(String(100))
    resolution: Mapped[str | None] = mapped_column(Text)
    interaction_history: Mapped[list[Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=False,
        default=list,
        server_default=text("'[]'"),
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
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    customer: Mapped["Customer"] = relationship(back_populates="support_cases")
    booking: Mapped["Booking | None"] = relationship(back_populates="support_cases")
