"""
Schema汇总
"""
from app.schemas.user import (
    UserBase, UserCreate, UserLogin, WechatLogin, UserResponse, Token,
    StudentBase, StudentCreate, StudentUpdate, StudentResponse,
    CoachBase, CoachCreate, CoachResponse,
)
from app.schemas.growth import (
    FitnessMetricBase, FitnessMetricCreate, FitnessMetricResponse,
    FitnessTestBase, FitnessTestCreate, FitnessTestResponse,
    RadarChartData, GrowthProfile,
    TrainingSessionBase, TrainingSessionCreate, TrainingSessionResponse,
)
from app.schemas.course import (
    CourseBase, CourseCreate, CourseUpdate, CourseResponse,
    VenueBase, VenueCreate, VenueResponse,
    ScheduleBase, ScheduleCreate, ScheduleUpdate, ScheduleResponse,
    AttendanceBase, AttendanceCreate, CheckInRequest, AttendanceResponse,
)

__all__ = [
    # 用户
    "UserBase", "UserCreate", "UserLogin", "WechatLogin", "UserResponse", "Token",
    "StudentBase", "StudentCreate", "StudentUpdate", "StudentResponse",
    "CoachBase", "CoachCreate", "CoachResponse",
    # 成长档案
    "FitnessMetricBase", "FitnessMetricCreate", "FitnessMetricResponse",
    "FitnessTestBase", "FitnessTestCreate", "FitnessTestResponse",
    "RadarChartData", "GrowthProfile",
    "TrainingSessionBase", "TrainingSessionCreate", "TrainingSessionResponse",
    # 课程
    "CourseBase", "CourseCreate", "CourseUpdate", "CourseResponse",
    "VenueBase", "VenueCreate", "VenueResponse",
    "ScheduleBase", "ScheduleCreate", "ScheduleUpdate", "ScheduleResponse",
    "AttendanceBase", "AttendanceCreate", "CheckInRequest", "AttendanceResponse",
]
