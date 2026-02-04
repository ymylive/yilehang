"""
API路由汇总
"""
from fastapi import APIRouter

from app.api.v1.endpoints import auth, students, schedules, training, growth

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(students.router, prefix="/students", tags=["学员"])
api_router.include_router(schedules.router, prefix="/schedules", tags=["排课"])
api_router.include_router(training.router, prefix="/training", tags=["AI训练"])
api_router.include_router(growth.router, prefix="/growth", tags=["成长档案"])
