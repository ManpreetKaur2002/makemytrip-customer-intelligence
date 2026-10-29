from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Booking
from app.schemas.booking import BookingCreate, BookingUpdate
from app.services.common import commit_or_raise


def list_bookings(
    db: Session, customer_id: UUID | None, status: str | None, limit: int, offset: int
) -> list[Booking]:
    statement = select(Booking)
    if customer_id:
        statement = statement.where(Booking.customer_id == customer_id)
    if status:
        statement = statement.where(Booking.booking_status == status)
    statement = (
        statement.order_by(Booking.created_at.desc()).offset(offset).limit(limit)
    )
    return list(db.scalars(statement).all())


def get_booking(db: Session, booking_id: UUID) -> Booking | None:
    return db.get(Booking, booking_id)


def create_booking(db: Session, payload: BookingCreate) -> Booking:
    booking = Booking(**payload.model_dump())
    db.add(booking)
    commit_or_raise(db)
    db.refresh(booking)
    return booking


def update_booking(db: Session, booking: Booking, payload: BookingUpdate) -> Booking:
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(booking, field, value)
    commit_or_raise(db)
    db.refresh(booking)
    return booking
