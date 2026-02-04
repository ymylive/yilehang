"""
Schema汇总
"""
from app.schemas.user import (
    UserBase, UserCreate, UserLogin, WechatLogin, WechatPhoneLogin,
    SmsCodeRequest, SmsCodeLogin, PasswordReset, PasswordChange,
    UserUpdate, UserResponse, UserDetailResponse, Token, TokenRefresh,
    StudentBase, StudentCreate, StudentRegister, StudentUpdate, StudentResponse, StudentDetailResponse,
    CoachBase, CoachCreate, CoachRegister, CoachResponse, CoachProfileResponse,
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
from app.schemas.booking import (
    MembershipCardBase, MembershipCardCreate, MembershipCardUpdate, MembershipCardResponse,
    StudentMembershipBase, StudentMembershipCreate, StudentMembershipResponse, MembershipRechargeRequest,
    CoachSlotBase, CoachSlotCreate, CoachSlotUpdate, CoachSlotResponse,
    BookingBase, BookingCreate, BookingUpdate, BookingResponse, BookingListResponse,
    BookingCancelRequest, BookingRescheduleRequest,
    TransactionBase, TransactionCreate, TransactionResponse,
    ReviewBase, ReviewCreate, ReviewResponse, CoachReplyRequest,
    CoachFeedbackBase, CoachFeedbackCreate, CoachFeedbackResponse,
    CoachDetailResponse, CoachAvailableTimeSlot, CoachAvailableSlotsResponse,
    DashboardOverview, AttendanceStats, RevenueStats, AlertInfo,
)

__all__ = [
    # 用户
    "UserBase", "UserCreate", "UserLogin", "WechatLogin", "WechatPhoneLogin",
    "SmsCodeRequest", "SmsCodeLogin", "PasswordReset", "PasswordChange",
    "UserUpdate", "UserResponse", "UserDetailResponse", "Token", "TokenRefresh",
    "StudentBase", "StudentCreate", "StudentRegister", "StudentUpdate", "StudentResponse", "StudentDetailResponse",
    "CoachBase", "CoachCreate", "CoachRegister", "CoachResponse", "CoachProfileResponse",
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
    # 约课系统
    "MembershipCardBase", "MembershipCardCreate", "MembershipCardUpdate", "MembershipCardResponse",
    "StudentMembershipBase", "StudentMembershipCreate", "StudentMembershipResponse", "MembershipRechargeRequest",
    "CoachSlotBase", "CoachSlotCreate", "CoachSlotUpdate", "CoachSlotResponse",
    "BookingBase", "BookingCreate", "BookingUpdate", "BookingResponse", "BookingListResponse",
    "BookingCancelRequest", "BookingRescheduleRequest",
    "TransactionBase", "TransactionCreate", "TransactionResponse",
    "ReviewBase", "ReviewCreate", "ReviewResponse", "CoachReplyRequest",
    "CoachFeedbackBase", "CoachFeedbackCreate", "CoachFeedbackResponse",
    "CoachDetailResponse", "CoachAvailableTimeSlot", "CoachAvailableSlotsResponse",
    "DashboardOverview", "AttendanceStats", "RevenueStats", "AlertInfo",
]
