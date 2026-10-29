from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models import Customer, CustomerAIInsight
from app.schemas.customer_ai_insight import (
    CustomerAIInsightCreate,
    CustomerAIInsightRead,
)
from app.services.common import commit_or_raise

router = APIRouter()


@router.get("", response_model=list[CustomerAIInsightRead])
def list_insights(
    customer_id: UUID | None = None,
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
) -> list[CustomerAIInsight]:
    statement = select(CustomerAIInsight)
    if customer_id:
        statement = statement.where(CustomerAIInsight.customer_id == customer_id)
    statement = statement.order_by(CustomerAIInsight.generated_at.desc()).limit(limit)
    return list(db.scalars(statement).all())


@router.post("", response_model=CustomerAIInsightRead, status_code=201)
def create_insight(
    payload: CustomerAIInsightCreate, db: Session = Depends(get_db)
) -> CustomerAIInsight:
    if db.get(Customer, payload.customer_id) is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    insight = CustomerAIInsight(**payload.model_dump())
    db.add(insight)
    try:
        commit_or_raise(db)
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
    db.refresh(insight)
    return insight
