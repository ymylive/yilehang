"""
约课系统服务层
"""

from datetime import date, datetime, time, timedelta, timezone
from typing import List, Optional, Tuple

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.booking import (
    Booking,
    BookingStatus,
    CoachAvailableSlot,
    CoachFeedback,
    MembershipCard,
    MembershipStatus,
    Review,
    StudentMembership,
    Transaction,
    TransactionType,
)
from app.models.course import Schedule
from app.models.user import Coach, Student
from app.schemas.booking import (
    BookingCancelRequest,
    BookingCreate,
    BookingRescheduleRequest,
    CoachAvailableTimeSlot,
    CoachFeedbackCreate,
    CoachSlotCreate,
    CoachSlotUpdate,
    MembershipCardCreate,
    MembershipCardUpdate,
    MembershipRechargeRequest,
    ReviewCreate,
)


class BookingService:
    """预约服务"""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ==================== 预约冲突检测 ====================

    async def check_booking_conflict(
        self,
        coach_id: int,
        booking_date: date,
        start_time: time,
        end_time: time,
        exclude_booking_id: Optional[int] = None,
    ) -> bool:
        """检查教练在指定时段是否有冲突"""
        query = select(Booking).where(
            Booking.coach_id == coach_id,
            Booking.booking_date == booking_date,
            Booking.status.in_([BookingStatus.PENDING.value, BookingStatus.CONFIRMED.value]),
            or_(
                and_(Booking.start_time <= start_time, Booking.end_time > start_time),
                and_(Booking.start_time < end_time, Booking.end_time >= end_time),
                and_(Booking.start_time >= start_time, Booking.end_time <= end_time),
            ),
        )
        if exclude_booking_id:
            query = query.where(Booking.id != exclude_booking_id)

        result = await self.db.execute(query)
        return result.scalar() is not None

    async def check_student_booking_conflict(
        self,
        student_id: int,
        booking_date: date,
        start_time: time,
        end_time: time,
        exclude_booking_id: Optional[int] = None,
    ) -> bool:
        """检查学员在指定时段是否有冲突"""
        query = select(Booking).where(
            Booking.student_id == student_id,
            Booking.booking_date == booking_date,
            Booking.status.in_([BookingStatus.PENDING.value, BookingStatus.CONFIRMED.value]),
            or_(
                and_(Booking.start_time <= start_time, Booking.end_time > start_time),
                and_(Booking.start_time < end_time, Booking.end_time >= end_time),
                and_(Booking.start_time >= start_time, Booking.end_time <= end_time),
            ),
        )
        if exclude_booking_id:
            query = query.where(Booking.id != exclude_booking_id)

        result = await self.db.execute(query)
        return result.scalar() is not None

    # ==================== 预约管理 ====================

    async def create_booking(
        self, data: BookingCreate, student_id: int, auto_deduct: bool = True
    ) -> Booking:
        """创建预约"""
        await self.db.execute(select(Coach.id).where(Coach.id == data.coach_id).with_for_update())
        await self.db.execute(select(Student.id).where(Student.id == student_id).with_for_update())

        # 检查教练时段冲突
        if await self.check_booking_conflict(
            data.coach_id, data.booking_date, data.start_time, data.end_time
        ):
            raise ValueError("该时段教练已被预约")

        # 检查学员时段冲突
        if await self.check_student_booking_conflict(
            student_id, data.booking_date, data.start_time, data.end_time
        ):
            raise ValueError("该时段您已有其他预约")

        # 获取学员的有效课时卡
        membership = await self._get_active_membership_for_update(student_id)
        if not membership:
            raise ValueError("您没有可用的课时卡")
        if membership.remaining_times <= 0:
            raise ValueError("课时余额不足")

        # 创建预约
        booking = Booking(
            student_id=student_id,
            coach_id=data.coach_id,
            schedule_id=data.schedule_id,
            booking_date=data.booking_date,
            start_time=data.start_time,
            end_time=data.end_time,
            course_type=data.course_type,
            status=BookingStatus.CONFIRMED.value,
            membership_id=membership.id,
            remark=data.remark,
        )
        self.db.add(booking)
        await self.db.flush()

        # 自动扣除课时
        if auto_deduct:
            await self.deduct_class_time(student_id, booking.id, membership.id)

        await self.db.commit()
        await self.db.refresh(booking)
        return booking

    async def _get_active_membership_for_update(
        self, student_id: int
    ) -> Optional[StudentMembership]:
        """获取并锁定学员有效课时卡（优先使用即将过期的）"""
        result = await self.db.execute(
            select(StudentMembership)
            .where(
                StudentMembership.student_id == student_id,
                StudentMembership.status == MembershipStatus.ACTIVE.value,
                StudentMembership.remaining_times > 0,
                or_(
                    StudentMembership.expire_date.is_(None),
                    StudentMembership.expire_date >= date.today(),
                ),
            )
            .order_by(StudentMembership.expire_date.asc().nullslast())
            .with_for_update()
        )
        return result.scalar_one_or_none()

    async def cancel_booking(
        self, booking_id: int, user_id: int, data: BookingCancelRequest
    ) -> Booking:
        """取消预约"""
        booking = await self.get_booking(booking_id)
        if not booking:
            raise ValueError("预约不存在")

        if booking.status not in [BookingStatus.PENDING.value, BookingStatus.CONFIRMED.value]:
            raise ValueError("该预约状态不可取消")

        # 检查取消时限
        from app.core.config import settings

        booking_datetime = datetime.combine(booking.booking_date, booking.start_time)
        cancel_deadline = booking_datetime - timedelta(hours=settings.BOOKING_CANCEL_HOURS_BEFORE)
        if datetime.now() > cancel_deadline:
            raise ValueError(f"距离上课不足{settings.BOOKING_CANCEL_HOURS_BEFORE}小时，无法取消")

        # 更新预约状态
        booking.status = BookingStatus.CANCELLED.value
        booking.cancel_reason = data.cancel_reason
        booking.cancelled_at = datetime.now(timezone.utc)
        booking.cancelled_by = user_id

        # 退还课时
        if booking.membership_id:
            await self.refund_class_time(booking.student_id, booking.id, booking.membership_id)

        await self.db.commit()
        await self.db.refresh(booking)
        return booking

    async def reschedule_booking(self, booking_id: int, data: BookingRescheduleRequest) -> Booking:
        """改期预约"""
        booking = await self.get_booking(booking_id)
        if not booking:
            raise ValueError("预约不存在")

        if booking.status not in [BookingStatus.PENDING.value, BookingStatus.CONFIRMED.value]:
            raise ValueError("该预约状态不可改期")

        # 检查新时段冲突
        if await self.check_booking_conflict(
            booking.coach_id,
            data.new_date,
            data.new_start_time,
            data.new_end_time,
            exclude_booking_id=booking_id,
        ):
            raise ValueError("新时段教练已被预约")

        if await self.check_student_booking_conflict(
            booking.student_id,
            data.new_date,
            data.new_start_time,
            data.new_end_time,
            exclude_booking_id=booking_id,
        ):
            raise ValueError("新时段您已有其他预约")

        # 更新预约时间
        booking.booking_date = data.new_date
        booking.start_time = data.new_start_time
        booking.end_time = data.new_end_time
        booking.updated_at = datetime.now(timezone.utc)

        await self.db.commit()
        await self.db.refresh(booking)
        return booking

    async def complete_booking(self, booking_id: int) -> Booking:
        """完成预约（上课结束）"""
        booking = await self.get_booking(booking_id)
        if not booking:
            raise ValueError("预约不存在")

        booking.status = BookingStatus.COMPLETED.value
        booking.updated_at = datetime.now(timezone.utc)

        await self.db.commit()
        await self.db.refresh(booking)
        return booking

    async def mark_no_show(self, booking_id: int) -> Booking:
        """标记未到"""
        booking = await self.get_booking(booking_id)
        if not booking:
            raise ValueError("预约不存在")

        booking.status = BookingStatus.NO_SHOW.value
        booking.updated_at = datetime.now(timezone.utc)

        await self.db.commit()
        await self.db.refresh(booking)
        return booking

    async def get_booking(self, booking_id: int) -> Optional[Booking]:
        """获取预约详情"""
        result = await self.db.execute(
            select(Booking)
            .options(
                selectinload(Booking.student),
                selectinload(Booking.coach),
                selectinload(Booking.schedule).selectinload(Schedule.course),
            )
            .where(Booking.id == booking_id)
        )
        return result.scalar_one_or_none()

    async def get_student_bookings(
        self,
        student_id: int,
        status: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[Booking], int]:
        """获取学员预约列表"""
        query = (
            select(Booking)
            .options(
                selectinload(Booking.student),
                selectinload(Booking.coach),
                selectinload(Booking.schedule).selectinload(Schedule.course),
            )
            .where(Booking.student_id == student_id)
        )

        if status:
            query = query.where(Booking.status == status)
        if start_date:
            query = query.where(Booking.booking_date >= start_date)
        if end_date:
            query = query.where(Booking.booking_date <= end_date)

        # 获取总数
        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.db.execute(count_query)).scalar()

        # 分页
        query = query.order_by(Booking.booking_date.desc(), Booking.start_time.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await self.db.execute(query)
        return result.scalars().all(), total

    async def get_coach_bookings(
        self,
        coach_id: int,
        status: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[Booking], int]:
        """获取教练预约列表"""
        query = (
            select(Booking)
            .options(
                selectinload(Booking.student),
                selectinload(Booking.coach),
                selectinload(Booking.schedule).selectinload(Schedule.course),
            )
            .where(Booking.coach_id == coach_id)
        )

        if status:
            query = query.where(Booking.status == status)
        if start_date:
            query = query.where(Booking.booking_date >= start_date)
        if end_date:
            query = query.where(Booking.booking_date <= end_date)

        # 获取总数
        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.db.execute(count_query)).scalar()

        # 分页
        query = query.order_by(Booking.booking_date.desc(), Booking.start_time.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await self.db.execute(query)
        return result.scalars().all(), total

    # ==================== 课时管理 ====================

    async def get_active_membership(self, student_id: int) -> Optional[StudentMembership]:
        """获取学员有效的课时卡（优先使用即将过期的）"""
        result = await self.db.execute(
            select(StudentMembership)
            .where(
                StudentMembership.student_id == student_id,
                StudentMembership.status == MembershipStatus.ACTIVE.value,
                StudentMembership.remaining_times > 0,
                or_(
                    StudentMembership.expire_date.is_(None),
                    StudentMembership.expire_date >= date.today(),
                ),
            )
            .order_by(StudentMembership.expire_date.asc().nullslast())
        )
        return result.scalar_one_or_none()

    async def get_student_memberships(self, student_id: int) -> List[StudentMembership]:
        """获取学员所有课时卡"""
        result = await self.db.execute(
            select(StudentMembership)
            .options(selectinload(StudentMembership.card))
            .where(StudentMembership.student_id == student_id)
            .order_by(StudentMembership.created_at.desc())
        )
        return result.scalars().all()

    async def deduct_class_time(
        self, student_id: int, booking_id: int, membership_id: int
    ) -> Transaction:
        """扣除课时"""
        result = await self.db.execute(
            select(StudentMembership).where(StudentMembership.id == membership_id).with_for_update()
        )
        membership = result.scalar_one_or_none()
        if not membership or membership.remaining_times <= 0:
            raise ValueError("课时余额不足")

        membership.remaining_times -= 1

        # 检查是否用完
        if membership.remaining_times <= 0:
            membership.status = MembershipStatus.EXHAUSTED.value

        # 创建消费记录
        transaction = Transaction(
            student_id=student_id,
            type=TransactionType.CONSUME.value,
            times_change=-1,
            membership_id=membership_id,
            booking_id=booking_id,
            description="预约扣费",
        )
        self.db.add(transaction)

        # 同步更新学员表的剩余课时
        student = await self.db.get(Student, student_id)
        if student:
            student.remaining_lessons = max(0, student.remaining_lessons - 1)

        return transaction

    async def refund_class_time(
        self, student_id: int, booking_id: int, membership_id: int
    ) -> Transaction:
        """退还课时"""
        membership = await self.db.get(StudentMembership, membership_id)
        if not membership:
            raise ValueError("课时卡不存在")

        membership.remaining_times += 1
        if membership.status == MembershipStatus.EXHAUSTED.value:
            membership.status = MembershipStatus.ACTIVE.value

        # 创建退款记录
        transaction = Transaction(
            student_id=student_id,
            type=TransactionType.REFUND.value,
            times_change=1,
            membership_id=membership_id,
            booking_id=booking_id,
            description="取消预约退还",
        )
        self.db.add(transaction)

        # 同步更新学员表的剩余课时
        student = await self.db.get(Student, student_id)
        if student:
            student.remaining_lessons += 1

        return transaction

    async def recharge_membership(
        self, data: MembershipRechargeRequest, operator_id: int
    ) -> StudentMembership:
        """管理员手动充值课时"""
        # 获取课时卡信息
        card = await self.db.get(MembershipCard, data.card_id)
        if not card:
            raise ValueError("课时卡类型不存在")

        # 查找或创建学员课时账户
        result = await self.db.execute(
            select(StudentMembership).where(
                StudentMembership.student_id == data.student_id,
                StudentMembership.card_id == data.card_id,
                StudentMembership.status == MembershipStatus.ACTIVE.value,
            )
        )
        membership = result.scalar_one_or_none()

        if membership:
            # 已有账户，增加次数
            membership.remaining_times += data.times
        else:
            # 创建新账户
            expire_date = None
            if card.duration_days:
                expire_date = date.today() + timedelta(days=card.duration_days)

            membership = StudentMembership(
                student_id=data.student_id,
                card_id=data.card_id,
                remaining_times=data.times,
                expire_date=expire_date,
                status=MembershipStatus.ACTIVE.value,
            )
            self.db.add(membership)
            await self.db.flush()

        # 创建充值记录
        transaction = Transaction(
            student_id=data.student_id,
            type=TransactionType.MANUAL.value,
            times_change=data.times,
            membership_id=membership.id,
            description=data.remark or f"管理员充值{data.times}次",
            operator_id=operator_id,
        )
        self.db.add(transaction)

        # 同步更新学员表的剩余课时
        student = await self.db.get(Student, data.student_id)
        if student:
            student.remaining_lessons += data.times

        await self.db.commit()
        await self.db.refresh(membership)
        return membership

    # ==================== 教练时段管理 ====================

    async def create_coach_slot(self, coach_id: int, data: CoachSlotCreate) -> CoachAvailableSlot:
        """创建教练可约时段"""
        slot = CoachAvailableSlot(
            coach_id=coach_id,
            day_of_week=data.day_of_week,
            start_time=data.start_time,
            end_time=data.end_time,
            slot_duration=data.slot_duration,
            max_students=data.max_students,
        )
        self.db.add(slot)
        await self.db.commit()
        await self.db.refresh(slot)
        return slot

    async def update_coach_slot(self, slot_id: int, data: CoachSlotUpdate) -> CoachAvailableSlot:
        """更新教练可约时段"""
        slot = await self.db.get(CoachAvailableSlot, slot_id)
        if not slot:
            raise ValueError("时段不存在")

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(slot, field, value)

        await self.db.commit()
        await self.db.refresh(slot)
        return slot

    async def delete_coach_slot(self, slot_id: int) -> bool:
        """删除教练可约时段"""
        slot = await self.db.get(CoachAvailableSlot, slot_id)
        if not slot:
            return False

        await self.db.delete(slot)
        await self.db.commit()
        return True

    async def get_coach_slots(self, coach_id: int) -> List[CoachAvailableSlot]:
        """获取教练所有可约时段"""
        result = await self.db.execute(
            select(CoachAvailableSlot)
            .where(CoachAvailableSlot.coach_id == coach_id, CoachAvailableSlot.is_active.is_(True))
            .order_by(CoachAvailableSlot.day_of_week, CoachAvailableSlot.start_time)
        )
        return result.scalars().all()

    async def get_coach_available_times(
        self, coach_id: int, start_date: date, end_date: date
    ) -> List[CoachAvailableTimeSlot]:
        """获取教练在指定日期范围内的可约时间"""
        # 获取教练的可约时段配置
        slots = await self.get_coach_slots(coach_id)
        if not slots:
            return []

        # 获取已有预约
        result = await self.db.execute(
            select(Booking).where(
                Booking.coach_id == coach_id,
                Booking.booking_date >= start_date,
                Booking.booking_date <= end_date,
                Booking.status.in_([BookingStatus.PENDING.value, BookingStatus.CONFIRMED.value]),
            )
        )
        existing_bookings = result.scalars().all()

        # 生成可约时间列表
        available_times = []
        current_date = start_date
        while current_date <= end_date:
            day_of_week = current_date.weekday()
            # Python weekday: 0=Monday, 需要转换为 0=Sunday
            day_of_week = (day_of_week + 1) % 7

            for slot in slots:
                if slot.day_of_week == day_of_week:
                    # 检查该时段是否已被预约
                    is_booked = any(
                        b.booking_date == current_date
                        and b.start_time == slot.start_time
                        and b.end_time == slot.end_time
                        for b in existing_bookings
                    )

                    available_times.append(
                        CoachAvailableTimeSlot(
                            date=current_date,
                            start_time=slot.start_time,
                            end_time=slot.end_time,
                            is_available=not is_booked,
                            remaining_slots=0 if is_booked else slot.max_students,
                        )
                    )

            current_date += timedelta(days=1)

        return available_times


class MembershipCardService:
    """课时卡服务"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_card(self, data: MembershipCardCreate) -> MembershipCard:
        """创建课时卡"""
        card = MembershipCard(**data.model_dump())
        self.db.add(card)
        await self.db.commit()
        await self.db.refresh(card)
        return card

    async def update_card(self, card_id: int, data: MembershipCardUpdate) -> MembershipCard:
        """更新课时卡"""
        card = await self.db.get(MembershipCard, card_id)
        if not card:
            raise ValueError("课时卡不存在")

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(card, field, value)

        card.updated_at = datetime.now(timezone.utc)
        await self.db.commit()
        await self.db.refresh(card)
        return card

    async def get_card(self, card_id: int) -> Optional[MembershipCard]:
        """获取课时卡详情"""
        return await self.db.get(MembershipCard, card_id)

    async def get_active_cards(self) -> List[MembershipCard]:
        """获取所有可用课时卡"""
        result = await self.db.execute(
            select(MembershipCard)
            .where(MembershipCard.is_active.is_(True))
            .order_by(MembershipCard.sort_order, MembershipCard.price)
        )
        return result.scalars().all()


class ReviewService:
    """评价服务"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_review(self, data: ReviewCreate, student_id: int) -> Review:
        """创建评价"""
        # 检查预约是否存在且已完成
        booking = await self.db.get(Booking, data.booking_id)
        if not booking:
            raise ValueError("预约不存在")
        if booking.status != BookingStatus.COMPLETED.value:
            raise ValueError("只能评价已完成的课程")
        if booking.student_id != student_id:
            raise ValueError("只能评价自己的课程")

        # 检查是否已评价
        result = await self.db.execute(select(Review).where(Review.booking_id == data.booking_id))
        if result.scalar_one_or_none():
            raise ValueError("该课程已评价")

        # 创建评价
        import json

        review = Review(
            booking_id=data.booking_id,
            student_id=student_id,
            coach_id=booking.coach_id,
            rating=data.rating,
            content=data.content,
            tags=json.dumps(data.tags) if data.tags else None,
            is_anonymous=data.is_anonymous,
        )
        self.db.add(review)
        await self.db.commit()
        await self.db.refresh(review)
        return review

    async def reply_review(self, review_id: int, coach_id: int, reply: str) -> Review:
        """教练回复评价"""
        review = await self.db.get(Review, review_id)
        if not review:
            raise ValueError("评价不存在")
        if review.coach_id != coach_id:
            raise ValueError("只能回复自己的评价")

        review.coach_reply = reply
        review.coach_reply_at = datetime.now(timezone.utc)

        await self.db.commit()
        await self.db.refresh(review)
        return review

    async def get_coach_reviews(
        self, coach_id: int, page: int = 1, page_size: int = 20
    ) -> Tuple[List[Review], int, float]:
        """获取教练评价列表"""
        query = select(Review).where(Review.coach_id == coach_id)

        # 获取总数
        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.db.execute(count_query)).scalar()

        # 获取平均分
        avg_query = select(func.avg(Review.rating)).where(Review.coach_id == coach_id)
        avg_rating = (await self.db.execute(avg_query)).scalar() or 0.0

        # 分页
        query = query.order_by(Review.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await self.db.execute(query)
        return result.scalars().all(), total, float(avg_rating)


class CoachFeedbackService:
    """教练反馈服务"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_feedback(self, data: CoachFeedbackCreate, coach_id: int) -> CoachFeedback:
        """创建教练反馈"""
        # 检查预约是否存在
        booking = await self.db.get(Booking, data.booking_id)
        if not booking:
            raise ValueError("预约不存在")
        if booking.coach_id != coach_id:
            raise ValueError("只能为自己的课程提交反馈")

        feedback = CoachFeedback(
            booking_id=data.booking_id,
            coach_id=coach_id,
            student_id=data.student_id,
            performance_rating=data.performance_rating,
            content=data.content,
            suggestions=data.suggestions,
        )
        self.db.add(feedback)
        await self.db.commit()
        await self.db.refresh(feedback)
        return feedback

    async def get_student_feedbacks(
        self, student_id: int, page: int = 1, page_size: int = 20
    ) -> Tuple[List[CoachFeedback], int]:
        """获取学员收到的反馈列表"""
        query = select(CoachFeedback).where(CoachFeedback.student_id == student_id)

        # 获取总数
        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.db.execute(count_query)).scalar()

        # 分页
        query = query.order_by(CoachFeedback.created_at.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)

        result = await self.db.execute(query)
        return result.scalars().all(), total
