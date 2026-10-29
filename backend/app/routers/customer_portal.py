from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models import Booking, Customer, CustomerPreference, SupportCase
from app.schemas.customer_portal import CustomerSupportCaseCreate
from app.schemas.customer_preference import (
    CustomerPreferenceBase,
    CustomerPreferenceRead,
)
from app.schemas.booking import BookingRead
from app.schemas.support_case import SupportCaseRead
from app.security import get_current_customer
from app.services.common import commit_or_raise
from app.services.support_service import create_support_case
from app.schemas.support_case import SupportCaseCreate

router = APIRouter()


@router.get("/bookings", response_model=list[BookingRead])
def list_my_bookings(
    db: Session = Depends(get_db),
    customer: Customer = Depends(get_current_customer),
) -> list[Booking]:
    return list(
        db.scalars(
            select(Booking)
            .where(Booking.customer_id == customer.customer_id)
            .order_by(Booking.created_at.desc())
        ).all()
    )


@router.get("/preferences", response_model=CustomerPreferenceRead)
def get_my_preferences(
    db: Session = Depends(get_db),
    customer: Customer = Depends(get_current_customer),
) -> CustomerPreference:
    preference = db.scalar(
        select(CustomerPreference).where(
            CustomerPreference.customer_id == customer.customer_id
        )
    )
    if preference is None:
        raise HTTPException(status_code=404, detail="Travel preferences are not set")
    return preference


@router.put("/preferences", response_model=CustomerPreferenceRead)
def save_my_preferences(
    payload: CustomerPreferenceBase,
    db: Session = Depends(get_db),
    customer: Customer = Depends(get_current_customer),
) -> CustomerPreference:
    preference = db.scalar(
        select(CustomerPreference).where(
            CustomerPreference.customer_id == customer.customer_id
        )
    )
    if preference is None:
        preference = CustomerPreference(
            customer_id=customer.customer_id,
            **payload.model_dump(),
        )
        db.add(preference)
    else:
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(preference, field, value)
    try:
        commit_or_raise(db)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    db.refresh(preference)
    return preference


@router.get("/support-cases", response_model=list[SupportCaseRead])
def list_my_support_cases(
    db: Session = Depends(get_db),
    customer: Customer = Depends(get_current_customer),
) -> list[SupportCase]:
    return list(
        db.scalars(
            select(SupportCase)
            .where(SupportCase.customer_id == customer.customer_id)
            .order_by(SupportCase.created_at.desc())
        ).all()
    )


@router.post("/support-cases", response_model=SupportCaseRead, status_code=201)
def create_my_support_case(
    payload: CustomerSupportCaseCreate,
    db: Session = Depends(get_db),
    customer: Customer = Depends(get_current_customer),
) -> SupportCase:
    if payload.booking_id is not None:
        booking = db.get(Booking, payload.booking_id)
        if booking is None or booking.customer_id != customer.customer_id:
            raise HTTPException(status_code=404, detail="Booking not found")
    support_case = create_support_case(
        db,
        SupportCaseCreate(
            customer_id=customer.customer_id,
            **payload.model_dump(),
        ),
    )
    return support_case
