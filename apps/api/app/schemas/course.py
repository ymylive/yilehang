"""
课程相关Schema
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class CourseBase(BaseModel):
    """课程基础Schema"""
    name: str
    type: str = "group"
    category: str
    description: Optional[str] = None
    duration: int = 60
    max_students: int = 20
    price: float = 0


class CourseCreate(CourseBase):
    """课程创建Schema"""
    code: str


class CourseUpdate(BaseModel):
    """课程更新Schema"""
    name: Optional[str] = None
    description: Optional[str] = None
    duration: Optional[int] = None
    max_students: Optional[int] = None
    price: Optional[float] = None
    status: Optional[str] = None


class CourseResponse(CourseBase):
    """课程响应Schema"""
    id: int
    code: str
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class VenueBase(BaseModel):
    """场地基础Schema"""
    name: str
    address: Optional[str] = None
    capacity: int = 50


class VenueCreate(VenueBase):
    """场地创建Schema"""
    pass


class VenueResponse(VenueBase):
    """场地响应Schema"""
    id: int
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ScheduleBase(BaseModel):
    """排课基础Schema"""
    course_id: int
    coach_id: int
    venue_id: Optional[int] = None
    start_time: datetime
    end_time: datetime
    capacity: int = 20


class ScheduleCreate(ScheduleBase):
    """排课创建Schema"""
    pass


class ScheduleUpdate(BaseModel):
    """排课更新Schema"""
    venue_id: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    capacity: Optional[int] = None
    status: Optional[str] = None


class ScheduleResponse(ScheduleBase):
    """排课响应Schema"""
    id: int
    enrolled_count: int
    status: str
    course: Optional[CourseResponse] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AttendanceBase(BaseModel):
    """考勤基础Schema"""
    schedule_id: int
    student_id: int


class AttendanceCreate(AttendanceBase):
    """考勤创建Schema"""
    pass


class CheckInRequest(BaseModel):
    """签到请求"""
    schedule_id: int
    student_id: int
    check_in_method: str = "qrcode"


class AttendanceResponse(AttendanceBase):
    """考勤响应Schema"""
    id: int
    check_in_time: Optional[datetime] = None
    check_in_method: Optional[str] = None
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
