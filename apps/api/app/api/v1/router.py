"""API router."""
from fastapi import APIRouter

from app.api.v1.endpoints import (
    ai,
    auth,
    bookings,
    chat,
    coaches,
    dashboard,
    energy,
    growth,
    leaderboard,
    memberships,
    merchants,
    notifications,
    reviews,
    roles,
    schedules,
    students,
    training,
    upload,
)

api_router = APIRouter()

# Core
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(roles.router, prefix="/user", tags=["Roles"])
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

# Notifications
api_router.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])

# Upload
api_router.include_router(upload.router, prefix="/upload", tags=["Upload"])

# Chat
api_router.include_router(chat.router, prefix="/chat", tags=["Chat"])

# Energy System
api_router.include_router(energy.router, prefix="/energy", tags=["Energy"])
api_router.include_router(merchants.router, prefix="/merchants", tags=["Merchants"])
api_router.include_router(leaderboard.router, prefix="/leaderboard", tags=["Leaderboard"])
