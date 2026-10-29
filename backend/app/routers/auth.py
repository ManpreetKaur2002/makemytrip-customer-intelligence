from datetime import UTC, datetime

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models import Customer, CustomerCredential, CustomerAuthSession
from app.schemas.auth import CustomerLogin, CustomerRegister
from app.schemas.customer import CustomerRead
from app.security import (
    AUTH_COOKIE_NAME,
    get_current_customer,
    hash_password,
    issue_customer_session,
    verify_password,
)
from app.core.config import settings

router = APIRouter()


@router.post("/register", response_model=CustomerRead, status_code=201)
def register_customer(
    payload: CustomerRegister,
    response: Response,
    db: Session = Depends(get_db),
) -> Customer:
    normalized_email = str(payload.email).strip().lower()
    existing = db.scalar(
        select(Customer.customer_id).where(
            func.lower(Customer.email) == normalized_email
        )
    )
    if existing is not None:
        raise HTTPException(
            status_code=409, detail="Unable to register with that email"
        )

    customer = Customer(
        full_name=payload.full_name,
        email=normalized_email,
        phone=payload.phone,
    )
    db.add(customer)
    try:
        db.flush()
        db.add(
            CustomerCredential(
                customer_id=customer.customer_id,
                password_hash=hash_password(payload.password),
            )
        )
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(
            status_code=409, detail="Unable to register with that email"
        ) from error

    db.refresh(customer)
    issue_customer_session(db, customer.customer_id, response)
    return customer


@router.post("/login", response_model=CustomerRead)
def login_customer(
    payload: CustomerLogin,
    response: Response,
    db: Session = Depends(get_db),
) -> Customer:
    normalized_email = str(payload.email).strip().lower()
    customer = db.scalar(
        select(Customer).where(func.lower(Customer.email) == normalized_email)
    )
    credential = (
        db.scalar(
            select(CustomerCredential).where(
                CustomerCredential.customer_id == customer.customer_id
            )
        )
        if customer is not None
        else None
    )
    if (
        customer is None
        or credential is None
        or customer.account_status != "active"
        or not verify_password(payload.password, credential.password_hash)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Cookie"},
        )

    issue_customer_session(db, customer.customer_id, response)
    return customer


@router.post("/logout", status_code=204)
def logout_customer(
    response: Response,
    customer_session: str | None = Cookie(default=None, alias=AUTH_COOKIE_NAME),
    db: Session = Depends(get_db),
) -> Response:
    if customer_session:
        from hashlib import sha256

        token_hash = sha256(customer_session.encode("utf-8")).hexdigest()
        auth_session = db.scalar(
            select(CustomerAuthSession).where(
                CustomerAuthSession.token_hash == token_hash
            )
        )
        if auth_session is not None:
            db.delete(auth_session)
            db.commit()
    response.delete_cookie(
        key=AUTH_COOKIE_NAME,
        path="/",
        httponly=True,
        secure=settings.auth_cookie_secure,
        samesite="lax",
    )
    response.status_code = 204
    return response


@router.get("/me", response_model=CustomerRead)
def current_customer(
    customer: Customer = Depends(get_current_customer),
) -> Customer:
    return customer
