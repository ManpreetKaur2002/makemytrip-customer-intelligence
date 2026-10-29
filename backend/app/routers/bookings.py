from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models import Booking
from app.schemas.booking import BookingCreate, BookingRead, BookingUpdate
from app.services import booking_service

router = APIRouter()


@router.get("", response_model=list[BookingRead])
def list_bookings(
    customer_id: UUID | None = None,
    status: str | None = None,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> list[Booking]:
    return booking_service.list_bookings(db, customer_id, status, limit, offset)


@router.post("", response_model=BookingRead, status_code=201)
def create_booking(payload: BookingCreate, db: Session = Depends(get_db)) -> Booking:
    try:
        return booking_service.create_booking(db, payload)
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error


@router.get("/{booking_id}", response_model=BookingRead)
def get_booking(booking_id: UUID, db: Session = Depends(get_db)) -> Booking:
    booking = booking_service.get_booking(db, booking_id)
    if booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking


@router.patch("/{booking_id}", response_model=BookingRead)
def update_booking(
    booking_id: UUID, payload: BookingUpdate, db: Session = Depends(get_db)
) -> Booking:
    booking = booking_service.get_booking(db, booking_id)
    if booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")
    try:
        return booking_service.update_booking(db, booking, payload)
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
