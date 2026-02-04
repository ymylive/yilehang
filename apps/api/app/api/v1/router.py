"""
API路由汇总
"""
from fastapi import APIRouter

from app.api.v1.endpoints import auth, students, schedules, training, growth
from app.api.v1.endpoints import bookings, memberships, coaches, reviews

api_router = APIRouter()

# 原有路由
api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(students.router, prefix="/students", tags=["学员"])
api_router.include_router(schedules.router, prefix="/schedules", tags=["排课"])
api_router.include_router(training.router, prefix="/training", tags=["AI训练"])
api_router.include_router(growth.router, prefix="/growth", tags=["成长档案"])

# 约课系统路由
api_router.include_router(bookings.router, prefix="/bookings", tags=["预约管理"])
api_router.include_router(memberships.router, prefix="/memberships", tags=["课时卡"])
api_router.include_router(coaches.router, prefix="/coaches", tags=["教练"])
api_router.include_router(reviews.router, prefix="/reviews", tags=["评价"])

