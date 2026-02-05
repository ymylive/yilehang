"""
数据模型汇总
"""
from app.models.user import User, Student, Coach, ParentStudentRelation, UserRole, UserStatus
from app.models.course import Course, Venue, Schedule, Attendance, CourseType, CourseCategory
from app.models.growth import FitnessTest, FitnessMetric, TrainingSession, MetricType
from app.models.booking import (
    MembershipCard, StudentMembership, CoachAvailableSlot, Booking,
    Transaction, Review, CoachFeedback,
    CardType, MembershipStatus, BookingStatus, TransactionType
)

__all__ = [
    # 用户域
    "User",
    "Student",
    "Coach",
    "ParentStudentRelation",
    "UserRole",
    "UserStatus",
    # 课程域
    "Course",
    "Venue",
    "Schedule",
    "Attendance",
    "CourseType",
    "CourseCategory",
    # 成长档案域
    "FitnessTest",
    "FitnessMetric",
    "TrainingSession",
    "MetricType",
    # 约课系统域
    "MembershipCard",
    "StudentMembership",
    "CoachAvailableSlot",
    "Booking",
    "Transaction",
    "Review",
    "CoachFeedback",
    "CardType",
    "MembershipStatus",
    "BookingStatus",
    "TransactionType",
]
