"""API router."""
from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth,
    students,
    schedules,
    training,
    growth,
    bookings,
    memberships,
    coaches,
    reviews,
    dashboard,
    ai,
)

api_router = APIRouter()

# Core
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(students.router, prefix="/students", tags=["Students"])
api_router.include_router(schedules.router, prefix="/schedules", tags=["Schedules"])
api_router.include_router(training.router, prefix="/training", tags=["Training"])
api_router.include_router(growth.router, prefix="/growth", tags=["Growth"])

# Booking
api_router.include_router(bookings.router, prefix="/bookings", tags=["Bookings"])
api_router.include_router(memberships.router, prefix="/memberships", tags=["Memberships"])
api_router.include_router(coaches.router, prefix="/coaches", tags=["Coaches"])
api_router.include_router(reviews.router, prefix="/reviews", tags=["Reviews"])

# Admin dashboard
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])

# AI
api_router.include_router(ai.router, prefix="/ai", tags=["AI"])
