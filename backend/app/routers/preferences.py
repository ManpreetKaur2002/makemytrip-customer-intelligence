from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models import Customer, CustomerPreference
from app.schemas.customer_preference import (
    CustomerPreferenceBase,
    CustomerPreferenceRead,
)
from app.services.common import commit_or_raise

router = APIRouter()


@router.get("/{customer_id}", response_model=CustomerPreferenceRead)
def get_preference(
    customer_id: UUID, db: Session = Depends(get_db)
) -> CustomerPreference:
    preference = db.scalar(
        select(CustomerPreference).where(CustomerPreference.customer_id == customer_id)
    )
    if preference is None:
        raise HTTPException(status_code=404, detail="Customer preference not found")
    return preference


@router.put("/{customer_id}", response_model=CustomerPreferenceRead)
def save_preference(
    customer_id: UUID, payload: CustomerPreferenceBase, db: Session = Depends(get_db)
) -> CustomerPreference:
    customer = db.get(Customer, customer_id)
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    preference = db.scalar(
        select(CustomerPreference).where(CustomerPreference.customer_id == customer_id)
    )
    if preference is None:
        preference = CustomerPreference(customer_id=customer_id, **payload.model_dump())
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
