"""
种子数据脚本 - 初始化测试数据
运行方式: python -m scripts.seed_data
"""
import asyncio
import sys
from pathlib import Path
from datetime import date, time, timedelta
from decimal import Decimal

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models import (
    User, Student, Coach,
    MembershipCard, StudentMembership, CoachAvailableSlot,
    Booking, Transaction,
    CardType, MembershipStatus, BookingStatus, TransactionType
)
from app.core.security import get_password_hash


async def seed_data():
    """创建种子数据"""
    async with AsyncSessionLocal() as db:
        print("开始创建种子数据...")

        # 1. 创建管理员用户
        admin_user = User(
            phone="13800000000",
            password_hash=get_password_hash("admin123"),
            role="admin",
            nickname="管理员",
            status="active"
        )
        db.add(admin_user)
        await db.flush()
        print(f"  创建管理员: {admin_user.phone}")

        # 2. 创建教练
        coaches_data = [
            {"name": "张教练", "phone": "13800000001", "specialties": ["篮球", "体能训练"], "hourly_rate": 200},
            {"name": "李教练", "phone": "13800000002", "specialties": ["足球", "敏捷训练"], "hourly_rate": 180},
            {"name": "王教练", "phone": "13800000003", "specialties": ["游泳", "体能训练"], "hourly_rate": 220},
        ]

        coaches = []
        for data in coaches_data:
            user = User(
                phone=data["phone"],
                password_hash=get_password_hash("coach123"),
                role="coach",
                nickname=data["name"],
                status="active"
            )
            db.add(user)
            await db.flush()

            coach = Coach(
                user_id=user.id,
                coach_no=f"C{data['phone'][-4:]}",
                name=data["name"],
                specialty=",".join(data["specialties"]),  # 存储为逗号分隔字符串
                hourly_rate=Decimal(str(data["hourly_rate"])),
                introduction=f"专业{data['specialties'][0]}教练，从业5年以上",
                is_active=True
            )
            db.add(coach)
            await db.flush()
            coaches.append(coach)
            print(f"  创建教练: {coach.name}")

        # 3. 创建学员
        students_data = [
            {"name": "小明", "phone": "13900000001", "age": 10, "gender": "male"},
            {"name": "小红", "phone": "13900000002", "age": 9, "gender": "female"},
            {"name": "小刚", "phone": "13900000003", "age": 11, "gender": "male"},
            {"name": "小美", "phone": "13900000004", "age": 8, "gender": "female"},
        ]

        students = []
        for data in students_data:
            user = User(
                phone=data["phone"],
                password_hash=get_password_hash("student123"),
                role="student",
                nickname=data["name"],
                status="active"
            )
            db.add(user)
            await db.flush()

            student = Student(
                user_id=user.id,
                student_no=f"S{data['phone'][-4:]}",
                name=data["name"],
                phone=data["phone"],
                age=data["age"],
                gender=data["gender"],
                is_active=True
            )
            db.add(student)
            await db.flush()
            students.append(student)
            print(f"  创建学员: {student.name}")

        # 4. 创建课时卡
        cards_data = [
            {"name": "体验卡", "card_type": CardType.TIMES, "total_times": 2, "price": 99, "original_price": 200},
            {"name": "10次卡", "card_type": CardType.TIMES, "total_times": 10, "price": 1800, "original_price": 2000},
            {"name": "20次卡", "card_type": CardType.TIMES, "total_times": 20, "price": 3200, "original_price": 4000},
            {"name": "月卡", "card_type": CardType.DURATION, "duration_days": 30, "price": 2500, "original_price": 3000},
            {"name": "季卡", "card_type": CardType.DURATION, "duration_days": 90, "price": 6000, "original_price": 9000},
        ]

        cards = []
        for data in cards_data:
            card = MembershipCard(
                name=data["name"],
                card_type=data["card_type"],
                total_times=data.get("total_times"),
                duration_days=data.get("duration_days"),
                price=Decimal(str(data["price"])),
                original_price=Decimal(str(data["original_price"])),
                course_type="all",
                is_active=True
            )
            db.add(card)
            await db.flush()
            cards.append(card)
            print(f"  创建课时卡: {card.name}")

        # 5. 为学员分配课时卡
        for i, student in enumerate(students):
            card = cards[1]  # 10次卡
            membership = StudentMembership(
                student_id=student.id,
                card_id=card.id,
                remaining_times=card.total_times - i,  # 模拟已使用部分
                expire_date=date.today() + timedelta(days=180),
                status=MembershipStatus.ACTIVE
            )
            db.add(membership)
            await db.flush()

            # 创建购买记录
            transaction = Transaction(
                student_id=student.id,
                type=TransactionType.PURCHASE,
                amount=card.price,
                times_change=card.total_times,
                membership_id=membership.id,
                description=f"购买{card.name}"
            )
            db.add(transaction)
            print(f"  为 {student.name} 分配课时卡: {card.name}")

        # 6. 创建教练可约时段
        for coach in coaches:
            for day in range(1, 6):  # 周一到周五
                for hour in [9, 10, 14, 15, 16]:  # 上午9-11点，下午2-5点
                    slot = CoachAvailableSlot(
                        coach_id=coach.id,
                        day_of_week=day,
                        start_time=time(hour, 0),
                        end_time=time(hour + 1, 0),
                        slot_duration=60,
                        max_students=1,
                        is_active=True
                    )
                    db.add(slot)
            print(f"  为 {coach.name} 创建可约时段")

        # 7. 创建一些预约记录
        today = date.today()
        bookings_data = [
            {"student": students[0], "coach": coaches[0], "date": today, "start": time(9, 0), "end": time(10, 0), "status": BookingStatus.COMPLETED},
            {"student": students[1], "coach": coaches[0], "date": today, "start": time(10, 0), "end": time(11, 0), "status": BookingStatus.CONFIRMED},
            {"student": students[2], "coach": coaches[1], "date": today, "start": time(14, 0), "end": time(15, 0), "status": BookingStatus.PENDING},
            {"student": students[0], "coach": coaches[0], "date": today + timedelta(days=1), "start": time(9, 0), "end": time(10, 0), "status": BookingStatus.CONFIRMED},
        ]

        for data in bookings_data:
            # 获取学员的课时卡
            result = await db.execute(
                select(StudentMembership).where(
                    StudentMembership.student_id == data["student"].id,
                    StudentMembership.status == MembershipStatus.ACTIVE
                )
            )
            membership = result.scalar_one_or_none()

            booking = Booking(
                student_id=data["student"].id,
                coach_id=data["coach"].id,
                booking_date=data["date"],
                start_time=data["start"],
                end_time=data["end"],
                status=data["status"],
                membership_id=membership.id if membership else None
            )
            db.add(booking)
            print(f"  创建预约: {data['student'].name} -> {data['coach'].name} ({data['date']})")

        await db.commit()
        print("\n种子数据创建完成！")

        # 打印登录信息
        print("\n测试账号:")
        print("  管理员: 13800000000 / admin123")
        print("  教练: 13800000001 / coach123")
        print("  学员: 13900000001 / student123")


if __name__ == "__main__":
    asyncio.run(seed_data())
