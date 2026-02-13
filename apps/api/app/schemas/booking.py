"""
约课系统相关Schema
"""

from datetime import date, datetime, time
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

# ==================== 课时卡相关 ====================


class MembershipCardBase(BaseModel):
    """课时卡基础Schema"""

    name: str = Field(..., description="卡名")
    card_type: str = Field(..., description="类型：times/duration")
    total_times: Optional[int] = Field(None, description="总次数")
    duration_days: Optional[int] = Field(None, description="有效天数")
    price: float = Field(..., description="价格")
    original_price: Optional[float] = Field(None, description="原价")
    course_type: Optional[str] = Field(None, description="适用课程类型")
    description: Optional[str] = Field(None, description="描述")


class MembershipCardCreate(MembershipCardBase):
    """创建课时卡"""

    pass


class MembershipCardUpdate(BaseModel):
    """更新课时卡"""

    name: Optional[str] = None
    price: Optional[float] = None
    original_price: Optional[float] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    sort_order: Optional[int] = None


class MembershipCardResponse(MembershipCardBase):
    """课时卡响应"""

    id: int
    is_active: bool
    sort_order: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==================== 学员课时账户相关 ====================


class StudentMembershipBase(BaseModel):
    """学员课时账户基础Schema"""

    student_id: int
    card_id: int
    remaining_times: int = 0
    expire_date: Optional[date] = None


class StudentMembershipCreate(StudentMembershipBase):
    """创建学员课时账户"""

    pass


class StudentMembershipResponse(BaseModel):
    """学员课时账户响应"""

    id: int
    student_id: int
    card_id: int
    remaining_times: int
    expire_date: Optional[date]
    status: str
    purchase_date: datetime
    card: Optional[MembershipCardResponse] = None

    model_config = ConfigDict(from_attributes=True)


class MembershipRechargeRequest(BaseModel):
    """课时充值请求（管理员手动充值）"""

    student_id: int
    card_id: int
    times: int = Field(..., gt=0, description="充值次数")
    remark: Optional[str] = Field(None, description="备注")


# ==================== 教练可约时段相关 ====================


class CoachSlotBase(BaseModel):
    """教练可约时段基础Schema"""

    day_of_week: int = Field(..., ge=0, le=6, description="星期几，0=周日")
    start_time: time
    end_time: time
    slot_duration: int = Field(60, description="时段时长（分钟）")
    max_students: int = Field(1, description="最大学员数")


class CoachSlotCreate(CoachSlotBase):
    """创建教练可约时段"""

    pass


class CoachSlotUpdate(BaseModel):
    """更新教练可约时段"""

    start_time: Optional[time] = None
    end_time: Optional[time] = None
    slot_duration: Optional[int] = None
    max_students: Optional[int] = None
    is_active: Optional[bool] = None


class CoachSlotResponse(CoachSlotBase):
    """教练可约时段响应"""

    id: int
    coach_id: int
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==================== 预约相关 ====================


class BookingBase(BaseModel):
    """预约基础Schema"""

    coach_id: int
    booking_date: date
    start_time: time
    end_time: time
    course_type: str = "private"
    remark: Optional[str] = None


class BookingCreate(BookingBase):
    """创建预约"""

    student_id: Optional[int] = None  # 如果不传，使用当前用户关联的学员
    schedule_id: Optional[int] = None


class BookingUpdate(BaseModel):
    """更新预约"""

    status: Optional[str] = None
    remark: Optional[str] = None


class BookingCancelRequest(BaseModel):
    """取消预约请求"""

    cancel_reason: Optional[str] = None


class BookingRescheduleRequest(BaseModel):
    """改期请求"""

    new_date: date
    new_start_time: time
    new_end_time: time


class BookingResponse(BaseModel):
    """预约响应"""

    id: int
    student_id: int
    coach_id: int
    schedule_id: Optional[int]
    booking_date: date
    start_time: time
    end_time: time
    course_type: str
    status: str
    cancel_reason: Optional[str]
    cancelled_at: Optional[datetime]
    remark: Optional[str]
    created_at: datetime
    # 关联信息
    student_name: Optional[str] = None
    coach_name: Optional[str] = None
    course_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class BookingListResponse(BaseModel):
    """预约列表响应"""

    items: List[BookingResponse]
    total: int
    page: int
    page_size: int


# ==================== 消费记录相关 ====================


class TransactionBase(BaseModel):
    """消费记录基础Schema"""

    student_id: int
    type: str
    amount: Optional[float] = None
    times_change: int = 0
    description: Optional[str] = None


class TransactionCreate(TransactionBase):
    """创建消费记录"""

    membership_id: Optional[int] = None
    booking_id: Optional[int] = None


class TransactionResponse(BaseModel):
    """消费记录响应"""

    id: int
    student_id: int
    type: str
    amount: Optional[float]
    times_change: int
    membership_id: Optional[int]
    booking_id: Optional[int]
    description: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==================== 评价相关 ====================


class ReviewBase(BaseModel):
    """评价基础Schema"""

    rating: int = Field(..., ge=1, le=5, description="1-5星评分")
    content: Optional[str] = None
    tags: Optional[List[str]] = None
    is_anonymous: bool = False


class ReviewCreate(ReviewBase):
    """创建评价"""

    booking_id: int


class ReviewResponse(BaseModel):
    """评价响应"""

    id: int
    booking_id: int
    student_id: int
    coach_id: int
    rating: int
    content: Optional[str]
    tags: Optional[List[str]]
    is_anonymous: bool
    coach_reply: Optional[str]
    coach_reply_at: Optional[datetime]
    created_at: datetime
    # 关联信息
    student_name: Optional[str] = None
    student_avatar: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class CoachReplyRequest(BaseModel):
    """教练回复评价请求"""

    reply: str


# ==================== 教练反馈相关 ====================


class CoachFeedbackBase(BaseModel):
    """教练反馈基础Schema"""

    performance_rating: Optional[int] = Field(None, ge=1, le=5)
    content: str
    suggestions: Optional[str] = None


class CoachFeedbackCreate(CoachFeedbackBase):
    """创建教练反馈"""

    booking_id: int
    student_id: int


class CoachFeedbackResponse(BaseModel):
    """教练反馈响应"""

    id: int
    booking_id: int
    coach_id: int
    student_id: int
    performance_rating: Optional[int]
    content: str
    suggestions: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==================== 教练相关扩展 ====================


class CoachDetailResponse(BaseModel):
    """教练详情响应"""

    id: int
    coach_no: str
    name: str
    avatar: Optional[str]
    specialty: Optional[List[str]]
    introduction: Optional[str]
    certificates: Optional[List[str]]
    years_of_experience: Optional[int]
    hourly_rate: Optional[float]
    # 统计信息
    total_students: int = 0
    total_lessons: int = 0
    avg_rating: float = 0.0
    review_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class CoachAvailableTimeSlot(BaseModel):
    """教练可约时间段"""

    date: date
    start_time: time
    end_time: time
    is_available: bool = True
    remaining_slots: int = 1


class CoachAvailableSlotsResponse(BaseModel):
    """教练可约时段响应"""

    coach_id: int
    coach_name: str
    slots: List[CoachAvailableTimeSlot]


# ==================== 数据看板相关 ====================


class DashboardOverview(BaseModel):
    """数据看板概览"""

    total_students: int
    active_students: int
    total_coaches: int
    total_bookings_today: int
    total_bookings_week: int
    total_revenue_month: float
    attendance_rate: float


class AttendanceStats(BaseModel):
    """到课率统计"""

    date: date
    total_bookings: int
    completed: int
    no_show: int
    cancelled: int
    attendance_rate: float


class RevenueStats(BaseModel):
    """收入统计"""

    date: date
    amount: float
    transaction_count: int


class AlertInfo(BaseModel):
    """预警信息"""

    type: str  # low_balance/expiring_soon/no_show_warning
    student_id: int
    student_name: str
    message: str
    created_at: datetime
