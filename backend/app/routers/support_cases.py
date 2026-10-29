from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models import SupportCase
from app.schemas.support_case import (
    SupportCaseCreate,
    SupportCaseRead,
    SupportCaseUpdate,
)
from app.services import support_service

router = APIRouter()


@router.get("", response_model=list[SupportCaseRead])
def list_support_cases(
    status: str | None = None,
    priority: str | None = None,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> list[SupportCase]:
    return support_service.list_support_cases(db, status, priority, limit, offset)


@router.post("", response_model=SupportCaseRead, status_code=201)
def create_support_case(
    payload: SupportCaseCreate, db: Session = Depends(get_db)
) -> SupportCase:
    try:
        return support_service.create_support_case(db, payload)
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error


@router.get("/{case_id}", response_model=SupportCaseRead)
def get_support_case(case_id: UUID, db: Session = Depends(get_db)) -> SupportCase:
    support_case = support_service.get_support_case(db, case_id)
    if support_case is None:
        raise HTTPException(status_code=404, detail="Support case not found")
    return support_case


@router.patch("/{case_id}", response_model=SupportCaseRead)
def update_support_case(
    case_id: UUID, payload: SupportCaseUpdate, db: Session = Depends(get_db)
) -> SupportCase:
    support_case = support_service.get_support_case(db, case_id)
    if support_case is None:
        raise HTTPException(status_code=404, detail="Support case not found")
    try:
        return support_service.update_support_case(db, support_case, payload)
    except ValueError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error
