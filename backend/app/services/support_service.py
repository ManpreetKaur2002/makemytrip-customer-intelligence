from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import SupportCase
from app.schemas.support_case import SupportCaseCreate, SupportCaseUpdate
from app.services.common import commit_or_raise


def list_support_cases(
    db: Session, status: str | None, priority: str | None, limit: int, offset: int
) -> list[SupportCase]:
    statement = select(SupportCase)
    if status:
        statement = statement.where(SupportCase.case_status == status)
    if priority:
        statement = statement.where(SupportCase.priority == priority)
    statement = (
        statement.order_by(SupportCase.created_at.desc()).offset(offset).limit(limit)
    )
    return list(db.scalars(statement).all())


def get_support_case(db: Session, case_id: UUID) -> SupportCase | None:
    return db.get(SupportCase, case_id)


def create_support_case(db: Session, payload: SupportCaseCreate) -> SupportCase:
    support_case = SupportCase(**payload.model_dump())
    db.add(support_case)
    commit_or_raise(db)
    db.refresh(support_case)
    return support_case


def update_support_case(
    db: Session, support_case: SupportCase, payload: SupportCaseUpdate
) -> SupportCase:
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(support_case, field, value)
    if support_case.case_status in {"resolved", "closed"}:
        support_case.resolved_at = support_case.resolved_at or datetime.now(UTC)
    else:
        support_case.resolved_at = None
    commit_or_raise(db)
    db.refresh(support_case)
    return support_case
