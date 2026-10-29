from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi import Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.base import Base
from app.db.database import engine, get_db
from app.models import Booking, Customer, CustomerAIInsight, SupportCase
from app.routers import (
    ai_insights,
    auth,
    auth,
    bookings,
    chat,
    customers,
    customer_portal,
    preferences,
    support_cases,
)


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="MakeMyTrip Customer Operations", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(customers.router, prefix="/customers", tags=["customers"])
app.include_router(auth.router, prefix="/auth", tags=["authentication"])
app.include_router(customer_portal.router, prefix="/me", tags=["customer account"])
app.include_router(auth.router, prefix="/auth", tags=["authentication"])
app.include_router(preferences.router, prefix="/preferences", tags=["preferences"])
app.include_router(bookings.router, prefix="/bookings", tags=["bookings"])
app.include_router(
    support_cases.router, prefix="/support-cases", tags=["support cases"]
)
app.include_router(ai_insights.router, prefix="/ai-insights", tags=["AI insights"])
app.include_router(chat.router, prefix="/chat", tags=["chat"])


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/dashboard/summary", tags=["dashboard"])
def dashboard_summary(db: Session = Depends(get_db)) -> dict[str, int]:
    return {
        "customers": db.scalar(select(func.count()).select_from(Customer)) or 0,
        "bookings": db.scalar(select(func.count()).select_from(Booking)) or 0,
        "open_cases": db.scalar(
            select(func.count())
            .select_from(SupportCase)
            .where(SupportCase.case_status == "open")
        )
        or 0,
        "ai_insights": db.scalar(select(func.count()).select_from(CustomerAIInsight))
        or 0,
    }
