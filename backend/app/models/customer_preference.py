from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import (
    JSON,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    Uuid,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class CustomerPreference(Base):
    __tablename__ = "customer_preferences"
    __table_args__ = (
        CheckConstraint(
            "min_budget IS NULL OR min_budget >= 0", name="ck_preferences_min_budget"
        ),
        CheckConstraint(
            "max_budget IS NULL OR max_budget >= 0", name="ck_preferences_max_budget"
        ),
        CheckConstraint(
            "min_budget IS NULL OR max_budget IS NULL OR min_budget <= max_budget",
            name="ck_preferences_budget_range",
        ),
    )

    preference_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid4
    )
    customer_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("customers.customer_id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    min_budget: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    max_budget: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    currency: Mapped[str] = mapped_column(
        String(3), nullable=False, server_default="INR"
    )
    preferred_destinations: Mapped[list[Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=False,
        default=list,
        server_default=text("'[]'"),
    )
    preferred_hotel_category: Mapped[str | None] = mapped_column(String(30))
    travel_style: Mapped[str | None] = mapped_column(String(50))
    preferred_seat: Mapped[str | None] = mapped_column(String(30))
    dietary_preferences: Mapped[list[Any]] = mapped_column(
        JSON().with_variant(JSONB, "postgresql"),
        nullable=False,
        default=list,
        server_default=text("'[]'"),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    customer: Mapped["Customer"] = relationship(back_populates="preference")
