"""
数据模型汇总
"""
from app.models.rbac import (
    Role, Permission, Menu,
    RoleType, PermissionType, MenuType,
    user_roles, role_permissions, role_menus,
)
from app.models.user import User, Student, Coach, ParentStudentRelation, UserRole, UserStatus
from app.models.course import Course, Venue, Schedule, Attendance, CourseType, CourseCategory
from app.models.growth import FitnessTest, FitnessMetric, TrainingSession, MetricType
from app.models.booking import (
    MembershipCard, StudentMembership, CoachAvailableSlot, Booking,
    Transaction, Review, CoachFeedback,
    CardType, MembershipStatus, BookingStatus, TransactionType
)
from app.models.notification import Notification, NotificationType
from app.models.chat import Conversation, Message, MessageReadStatus, ConversationType, MessageType, MessageStatus
from app.models.energy import (
    EnergyRule, EnergyAccount, EnergyTransaction,
    EnergyTransactionType, EnergySourceType, ENERGY_LEVELS
)
from app.models.merchant import (
    Merchant, MerchantUser, RedeemItem, RedeemOrder,
    MerchantStatus, RedeemOrderStatus
)

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
