"""
数据模型汇总
"""

from app.models.booking import (
    Booking,
    BookingStatus,
    CardType,
    CoachAvailableSlot,
    CoachFeedback,
    MembershipCard,
    MembershipStatus,
    Review,
    StudentMembership,
    Transaction,
    TransactionType,
)
from app.models.chat import (
    Conversation,
    ConversationType,
    Message,
    MessageReadStatus,
    MessageStatus,
    MessageType,
)
from app.models.course import Attendance, Course, CourseCategory, CourseType, Schedule, Venue
from app.models.energy import (
    ENERGY_LEVELS,
    EnergyAccount,
    EnergyRule,
    EnergySourceType,
    EnergyTransaction,
    EnergyTransactionType,
)
from app.models.growth import FitnessMetric, FitnessTest, MetricType, TrainingSession
from app.models.merchant import (
    Merchant,
    MerchantStatus,
    MerchantUser,
    RedeemItem,
    RedeemOrder,
    RedeemOrderStatus,
)
from app.models.notification import Notification, NotificationType
from app.models.rbac import (
    Menu,
    MenuType,
    Permission,
    PermissionType,
    Role,
    RoleType,
    role_menus,
    role_permissions,
    user_roles,
)
from app.models.user import Coach, ParentStudentRelation, Student, User, UserRole, UserStatus

# Backward-compatible alias used by init/seed scripts.
Enrollment = Attendance

__all__ = [
    # RBAC 权限域
    "Role",
    "Permission",
    "Menu",
    "RoleType",
    "PermissionType",
    "MenuType",
    "user_roles",
    "role_permissions",
    "role_menus",
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
    "Enrollment",
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
    # 通知域
    "Notification",
    "NotificationType",
    # 聊天域
    "Conversation",
    "Message",
    "MessageReadStatus",
    "ConversationType",
    "MessageType",
    "MessageStatus",
    # 能量系统域
    "EnergyRule",
    "EnergyAccount",
    "EnergyTransaction",
    "EnergyTransactionType",
    "EnergySourceType",
    "ENERGY_LEVELS",
    # 商家系统域
    "Merchant",
    "MerchantUser",
    "RedeemItem",
    "RedeemOrder",
    "MerchantStatus",
    "RedeemOrderStatus",
]
