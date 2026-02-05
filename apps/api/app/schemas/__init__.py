"""Schema exports."""
from app.schemas.user import (
    UserBase, UserCreate, UserLogin, WechatLogin, WechatPhoneLogin,
    SmsCodeRequest, SmsCodeLogin, SmsRegister,
    PasswordReset, PasswordChange,
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
from app.schemas.ai import (
    JumpRopeAnalyzeRequest, JumpRopeAnalyzeResponse,
    AiAdviceRequest, AiAdviceResponse,
    AiChatRequest, AiChatResponse,
)

__all__ = [
    # User
    "UserBase", "UserCreate", "UserLogin", "WechatLogin", "WechatPhoneLogin",
    "SmsCodeRequest", "SmsCodeLogin", "SmsRegister",
    "PasswordReset", "PasswordChange",
    "UserUpdate", "UserResponse", "UserDetailResponse", "Token", "TokenRefresh",
    "StudentBase", "StudentCreate", "StudentRegister", "StudentUpdate", "StudentResponse", "StudentDetailResponse",
    "CoachBase", "CoachCreate", "CoachRegister", "CoachResponse", "CoachProfileResponse",
    # Growth
    "FitnessMetricBase", "FitnessMetricCreate", "FitnessMetricResponse",
    "FitnessTestBase", "FitnessTestCreate", "FitnessTestResponse",
    "RadarChartData", "GrowthProfile",
    "TrainingSessionBase", "TrainingSessionCreate", "TrainingSessionResponse",
    # Courses
    "CourseBase", "CourseCreate", "CourseUpdate", "CourseResponse",
    "VenueBase", "VenueCreate", "VenueResponse",
    "ScheduleBase", "ScheduleCreate", "ScheduleUpdate", "ScheduleResponse",
    "AttendanceBase", "AttendanceCreate", "CheckInRequest", "AttendanceResponse",
    # Booking
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
    # AI
    "JumpRopeAnalyzeRequest", "JumpRopeAnalyzeResponse",
    "AiAdviceRequest", "AiAdviceResponse",
    "AiChatRequest", "AiChatResponse",
]
