from sqlalchemy import or_, select
from sqlalchemy.orm import Session
from uuid import UUID

from app.models import Customer
from app.schemas.customer import CustomerCreate, CustomerUpdate
from app.services.common import commit_or_raise


def list_customers(
    db: Session, search: str | None, status: str | None, limit: int, offset: int
) -> list[Customer]:
    statement = select(Customer)
    if search:
        term = f"%{search}%"
        statement = statement.where(
            or_(Customer.full_name.ilike(term), Customer.email.ilike(term))
        )
    if status:
        statement = statement.where(Customer.account_status == status)
    statement = (
        statement.order_by(Customer.created_at.desc()).offset(offset).limit(limit)
    )
    return list(db.scalars(statement).all())


def get_customer(db: Session, customer_id: UUID) -> Customer | None:
    return db.get(Customer, customer_id)


def create_customer(db: Session, payload: CustomerCreate) -> Customer:
    customer = Customer(**payload.model_dump())
    db.add(customer)
    commit_or_raise(db)
    db.refresh(customer)
    return customer


def update_customer(
    db: Session, customer: Customer, payload: CustomerUpdate
) -> Customer:
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(customer, field, value)
    commit_or_raise(db)
    db.refresh(customer)
    return customer
