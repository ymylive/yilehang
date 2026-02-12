"""
种子数据脚本 - 初始化测试数据
运行方式: python -m scripts.seed_data
"""
import asyncio
import sys
import random
from pathlib import Path
from datetime import date, time, timedelta, datetime
from decimal import Decimal

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select, delete
from app.core.database import AsyncSessionLocal
from app.models import (
    User, Student, Coach,
    MembershipCard, StudentMembership, CoachAvailableSlot,
    Booking, Transaction, Review,
    CardType, MembershipStatus, BookingStatus, TransactionType,
    Notification, NotificationType,
    Conversation, Message, ConversationType, MessageType, MessageStatus,
    EnergyRule, EnergyAccount, EnergyTransaction, EnergySourceType, EnergyTransactionType,
    Merchant, MerchantUser, RedeemItem, RedeemOrder, MerchantStatus, RedeemOrderStatus
)
from app.core.security import get_password_hash


async def clear_data():
    """清空现有测试数据"""
    async with AsyncSessionLocal() as db:
        print("清空现有数据...")
        # 按依赖顺序删除
        await db.execute(delete(RedeemOrder))
        await db.execute(delete(RedeemItem))
        await db.execute(delete(MerchantUser))
        await db.execute(delete(Merchant))
        await db.execute(delete(EnergyTransaction))
        await db.execute(delete(EnergyAccount))
        await db.execute(delete(EnergyRule))
        await db.execute(delete(Message))
        await db.execute(delete(Conversation))
        await db.execute(delete(Notification))
        await db.execute(delete(Review))
        await db.execute(delete(Transaction))
        await db.execute(delete(Booking))
        await db.execute(delete(CoachAvailableSlot))
        await db.execute(delete(StudentMembership))
        await db.execute(delete(MembershipCard))
        await db.execute(delete(Student))
        await db.execute(delete(Coach))
        await db.execute(delete(User))
        await db.commit()
        print("  数据清空完成")


async def seed_data():
    """创建种子数据"""
    await clear_data()

    async with AsyncSessionLocal() as db:
        print("开始创建种子数据...")

        # 1. 创建管理员用户
        admin_user = User(
            phone="13800000000",
            email="admin@rl.cornna.xyz",
            password_hash=get_password_hash("admin123"),
            role="admin",
            nickname="管理员",
            status="active"
        )
        db.add(admin_user)
        await db.flush()
        print(f"  创建管理员: {admin_user.email} / {admin_user.phone}")

        # 2. 创建家长用户 (6个)
        parents_data = [
            {"nickname": "张妈妈", "phone": "13900000010", "email": "parent1@test.com"},
            {"nickname": "李爸爸", "phone": "13900000011", "email": "parent2@test.com"},
            {"nickname": "王妈妈", "phone": "13900000012", "email": "parent3@test.com"},
            {"nickname": "刘爸爸", "phone": "13900000013", "email": "parent4@test.com"},
            {"nickname": "陈妈妈", "phone": "13900000014", "email": "parent5@test.com"},
            {"nickname": "杨爸爸", "phone": "13900000015", "email": "parent6@test.com"},
        ]

        parents = []
        for data in parents_data:
            user = User(
                phone=data["phone"],
                email=data["email"],
                password_hash=get_password_hash("parent123"),
                role="parent",
                nickname=data["nickname"],
                status="active"
            )
            db.add(user)
            await db.flush()
            parents.append(user)
            print(f"  创建家长: {user.nickname} ({user.email})")

        # 3. 创建教练 (8个)
        coaches_data = [
            {"name": "张教练", "phone": "13800000001", "email": "coach1@rl.cornna.xyz", "specialties": ["篮球", "体能训练"], "hourly_rate": 200, "intro": "专业篮球教练，从业5年以上"},
            {"name": "李教练", "phone": "13800000002", "email": "coach2@rl.cornna.xyz", "specialties": ["足球", "敏捷训练"], "hourly_rate": 180, "intro": "前职业足球运动员，专注青少年足球培训"},
            {"name": "王教练", "phone": "13800000003", "email": "coach3@rl.cornna.xyz", "specialties": ["游泳", "体能训练"], "hourly_rate": 220, "intro": "国家一级游泳运动员，10年教学经验"},
            {"name": "赵教练", "phone": "13800000004", "email": "coach4@rl.cornna.xyz", "specialties": ["羽毛球", "体能"], "hourly_rate": 190, "intro": "国家二级运动员，羽毛球专项教练"},
            {"name": "孙教练", "phone": "13800000005", "email": "coach5@rl.cornna.xyz", "specialties": ["乒乓球", "协调训练"], "hourly_rate": 170, "intro": "省队退役选手，擅长青少年乒乓球启蒙"},
            {"name": "周教练", "phone": "13800000006", "email": "coach6@rl.cornna.xyz", "specialties": ["跳绳", "体适能"], "hourly_rate": 160, "intro": "专注儿童体适能训练，让运动更有趣"},
            {"name": "吴教练", "phone": "13800000007", "email": "coach7@rl.cornna.xyz", "specialties": ["网球", "力量训练"], "hourly_rate": 250, "intro": "持有ITF教练证书，网球专业教练"},
            {"name": "郑教练", "phone": "13800000008", "email": "coach8@rl.cornna.xyz", "specialties": ["田径", "爆发力"], "hourly_rate": 200, "intro": "田径专项教练，专注短跑和跳跃训练"},
        ]

        coaches = []
        for data in coaches_data:
            user = User(
                phone=data["phone"],
                email=data["email"],
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
                specialty=",".join(data["specialties"]),
                hourly_rate=Decimal(str(data["hourly_rate"])),
                introduction=data["intro"],
                is_active=True
            )
            db.add(coach)
            await db.flush()
            coaches.append(coach)
            print(f"  创建教练: {coach.name} ({data['email']})")

        # 4. 创建学员 (12个，关联家长)
        students_data = [
            # 张妈妈的孩子
            {"name": "小明", "phone": "13900000001", "email": "student1@test.com", "age": 10, "gender": "male", "parent_idx": 0},
            {"name": "小雪", "phone": "13900000002", "email": "student2@test.com", "age": 8, "gender": "female", "parent_idx": 0},
            # 李爸爸的孩子
            {"name": "小刚", "phone": "13900000003", "email": "student3@test.com", "age": 11, "gender": "male", "parent_idx": 1},
            {"name": "小红", "phone": "13900000004", "email": "student4@test.com", "age": 9, "gender": "female", "parent_idx": 1},
            # 王妈妈的孩子
            {"name": "小华", "phone": "13900000005", "email": "student5@test.com", "age": 10, "gender": "male", "parent_idx": 2},
            {"name": "小丽", "phone": "13900000006", "email": "student6@test.com", "age": 9, "gender": "female", "parent_idx": 2},
            # 刘爸爸的孩子
            {"name": "小强", "phone": "13900000007", "email": "student7@test.com", "age": 12, "gender": "male", "parent_idx": 3},
            # 陈妈妈的孩子
            {"name": "小芳", "phone": "13900000008", "email": "student8@test.com", "age": 8, "gender": "female", "parent_idx": 4},
            {"name": "小龙", "phone": "13900000009", "email": "student9@test.com", "age": 11, "gender": "male", "parent_idx": 4},
            # 杨爸爸的孩子
            {"name": "小燕", "phone": "13900000020", "email": "student10@test.com", "age": 7, "gender": "female", "parent_idx": 5},
            {"name": "小鹏", "phone": "13900000021", "email": "student11@test.com", "age": 13, "gender": "male", "parent_idx": 5},
            {"name": "小美", "phone": "13900000022", "email": "student12@test.com", "age": 10, "gender": "female", "parent_idx": 5},
        ]

        students = []
        for data in students_data:
            user = User(
                phone=data["phone"],
                email=data["email"],
                password_hash=get_password_hash("student123"),
                role="student",
                nickname=data["name"],
                status="active"
            )
            db.add(user)
            await db.flush()

            parent = parents[data["parent_idx"]]
            student = Student(
                user_id=user.id,
                student_no=f"S{data['phone'][-4:]}",
                name=data["name"],
                phone=data["phone"],
                age=data["age"],
                gender=data["gender"],
                parent_id=parent.id,
                is_active=True
            )
            db.add(student)
            await db.flush()
            students.append(student)
            print(f"  创建学员: {student.name} (家长: {parent.nickname})")

        # 5. 创建课时卡
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

        # 6. 为学员分配课时卡
        memberships = []
        for i, student in enumerate(students):
            card = cards[1]  # 10次卡
            remaining = random.randint(3, 10)
            membership = StudentMembership(
                student_id=student.id,
                card_id=card.id,
                remaining_times=remaining,
                expire_date=date.today() + timedelta(days=180),
                status=MembershipStatus.ACTIVE
            )
            db.add(membership)
            await db.flush()
            memberships.append(membership)

            transaction = Transaction(
                student_id=student.id,
                type=TransactionType.PURCHASE,
                amount=card.price,
                times_change=card.total_times,
                membership_id=membership.id,
                description=f"购买{card.name}"
            )
            db.add(transaction)
            print(f"  为 {student.name} 分配课时卡: {card.name} (剩余{remaining}次)")

        # 7. 创建教练可约时段
        for coach in coaches:
            for day in range(1, 6):  # 周一到周五
                for hour in [9, 10, 14, 15, 16]:
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

        # 8. 创建预约记录 (每个教练3-5条)
        today = date.today()
        all_bookings = []
        booking_statuses = [
            BookingStatus.COMPLETED,
            BookingStatus.COMPLETED,
            BookingStatus.CONFIRMED,
            BookingStatus.PENDING,
            BookingStatus.CANCELLED,
        ]

        for coach_idx, coach in enumerate(coaches):
            num_bookings = random.randint(3, 5)
            for b in range(num_bookings):
                student = random.choice(students)
                membership = memberships[students.index(student)]
                day_offset = random.randint(-7, 7)
                booking_date = today + timedelta(days=day_offset)
                hour = random.choice([9, 10, 14, 15, 16])
                status = random.choice(booking_statuses)

                # 过去的预约应该是已完成或已取消
                if day_offset < 0:
                    status = random.choice([BookingStatus.COMPLETED, BookingStatus.CANCELLED])
                # 未来的预约应该是待确认或已确认
                elif day_offset > 0:
                    status = random.choice([BookingStatus.PENDING, BookingStatus.CONFIRMED])

                booking = Booking(
                    student_id=student.id,
                    coach_id=coach.id,
                    booking_date=booking_date,
                    start_time=time(hour, 0),
                    end_time=time(hour + 1, 0),
                    status=status,
                    membership_id=membership.id
                )
                db.add(booking)
                await db.flush()
                all_bookings.append(booking)
                print(f"  创建预约: {student.name} -> {coach.name} ({booking_date}, {status.value})")

        # 9. 为已完成的课程添加评价
        review_contents = [
            "教练很专业，孩子进步很大！",
            "非常耐心，讲解清晰易懂。",
            "孩子很喜欢这位教练，每次上课都很开心。",
            "教学方法很好，孩子学得很快。",
            "准时、专业、有耐心，强烈推荐！",
            "教练很负责任，会根据孩子情况调整训练计划。",
            "孩子的体能明显提升了，感谢教练！",
            "课程内容丰富，孩子收获很多。",
        ]

        for booking in all_bookings:
            if booking.status == BookingStatus.COMPLETED:
                # 80%的已完成课程有评价
                if random.random() < 0.8:
                    rating = random.randint(3, 5)
                    content = random.choice(review_contents)
                    review = Review(
                        booking_id=booking.id,
                        student_id=booking.student_id,
                        coach_id=booking.coach_id,
                        rating=rating,
                        content=content,
                        is_anonymous=random.random() < 0.2
                    )
                    db.add(review)
                    print(f"  创建评价: {rating}星 - {content[:15]}...")

        # 10. 创建通知数据
        print("\n创建通知数据...")
        notification_templates = [
            {"type": NotificationType.BOOKING, "title": "预约成功", "content": "您已成功预约明天的篮球训练课程"},
            {"type": NotificationType.REMINDER, "title": "课程提醒", "content": "您预约的课程将在1小时后开始"},
            {"type": NotificationType.SYSTEM, "title": "系统通知", "content": "平台将于本周六进行系统维护"},
            {"type": NotificationType.SYSTEM, "title": "优惠活动", "content": "新用户专享：首次购卡立减100元"},
            {"type": NotificationType.FEEDBACK, "title": "收到新评价", "content": "家长对您的课程给出了5星好评"},
        ]

        for parent in parents:
            for _ in range(random.randint(2, 4)):
                template = random.choice(notification_templates)
                notification = Notification(
                    user_id=parent.id,
                    type=template["type"],
                    title=template["title"],
                    content=template["content"],
                    is_read=random.random() < 0.5
                )
                db.add(notification)
        print("  通知数据创建完成")

        # 11. 创建聊天会话和消息
        print("\n创建聊天数据...")
        chat_messages = [
            "您好，请问明天的课程还有名额吗？",
            "好的，我帮您查一下",
            "有的，还有2个名额",
            "太好了，我想给孩子预约一下",
            "好的，已经帮您预约成功了",
            "谢谢教练！",
            "不客气，有问题随时联系我",
            "孩子今天表现怎么样？",
            "今天表现很棒，进步很大！",
            "太好了，感谢教练的指导",
        ]

        # 为每个家长和教练创建一些会话
        for i, parent in enumerate(parents[:4]):
            coach = coaches[i % len(coaches)]
            coach_user_result = await db.execute(
                select(User).where(User.id == coach.user_id)
            )
            coach_user = coach_user_result.scalar_one()

            # 创建会话
            conversation = Conversation(
                type=ConversationType.PRIVATE,
                participant1_id=parent.id,
                participant2_id=coach_user.id,
                student_id=students[i].id if i < len(students) else None
            )
            db.add(conversation)
            await db.flush()

            # 添加消息
            num_messages = random.randint(4, 8)
            for j in range(num_messages):
                sender_id = parent.id if j % 2 == 0 else coach_user.id
                message = Message(
                    conversation_id=conversation.id,
                    sender_id=sender_id,
                    type=MessageType.TEXT,
                    content=chat_messages[j % len(chat_messages)],
                    status=MessageStatus.SENT
                )
                db.add(message)
                await db.flush()

                # 更新会话最后消息
                conversation.last_message_id = message.id
                conversation.last_message_at = message.created_at

            print(f"  创建会话: {parent.nickname} <-> {coach.name}")

        print("  聊天数据创建完成")

        # 12. 创建能量积分规则
        print("\n创建能量系统数据...")
        energy_rules_data = [
            {"name": "完成训练", "code": "training_complete", "source_type": EnergySourceType.TRAINING, "points": 20, "daily_limit": 100, "desc": "每完成一次训练获得20能量"},
            {"name": "课程签到", "code": "checkin", "source_type": EnergySourceType.CHECKIN, "points": 10, "daily_limit": 10, "desc": "每日签到获得10能量"},
            {"name": "完成体测", "code": "fitness_test", "source_type": EnergySourceType.FITNESS_TEST, "points": 50, "monthly_limit": 200, "desc": "完成体测获得50能量"},
            {"name": "评价课程", "code": "review", "source_type": EnergySourceType.REVIEW, "points": 15, "daily_limit": 30, "desc": "评价课程获得15能量"},
            {"name": "推荐好友", "code": "referral", "source_type": EnergySourceType.REFERRAL, "points": 100, "monthly_limit": 500, "desc": "成功推荐好友获得100能量"},
            {"name": "活动奖励", "code": "activity", "source_type": EnergySourceType.ACTIVITY, "points": 30, "desc": "参与活动获得能量奖励"},
        ]

        energy_rules = []
        for data in energy_rules_data:
            rule = EnergyRule(
                name=data["name"],
                code=data["code"],
                source_type=data["source_type"],
                points=data["points"],
                daily_limit=data.get("daily_limit"),
                weekly_limit=data.get("weekly_limit"),
                monthly_limit=data.get("monthly_limit"),
                description=data["desc"],
                is_active=True
            )
            db.add(rule)
            await db.flush()
            energy_rules.append(rule)
            print(f"  创建积分规则: {rule.name} (+{rule.points})")

        # 13. 为学员创建能量账户和交易记录
        for student in students:
            # 创建账户
            total_earned = random.randint(100, 800)
            total_spent = random.randint(0, min(total_earned, 200))
            level = 1
            if total_earned >= 500: level = 3
            elif total_earned >= 100: level = 2

            account = EnergyAccount(
                student_id=student.id,
                balance=total_earned - total_spent,
                total_earned=total_earned,
                total_spent=total_spent,
                level=level
            )
            db.add(account)
            await db.flush()

            # 创建一些交易记录
            for _ in range(random.randint(3, 8)):
                rule = random.choice(energy_rules)
                amount = rule.points
                trans = EnergyTransaction(
                    account_id=account.id,
                    student_id=student.id,
                    type=EnergyTransactionType.EARN,
                    source_type=rule.source_type,
                    amount=amount,
                    balance_after=account.balance,
                    rule_id=rule.id,
                    description=rule.name
                )
                db.add(trans)

            print(f"  为 {student.name} 创建能量账户: {account.balance} 能量")

        # 14. 创建合作商家
        print("\n创建商家数据...")
        merchants_data = [
            {"name": "阳光餐厅", "category": "餐饮", "address": "社区中心1楼", "phone": "13800001001", "desc": "健康营养餐，专为青少年定制"},
            {"name": "运动装备店", "category": "运动", "address": "社区中心2楼", "phone": "13800001002", "desc": "专业运动装备，品质保证"},
            {"name": "书香阁", "category": "教育", "address": "社区中心3楼", "phone": "13800001003", "desc": "优质图书文具，助力学习成长"},
            {"name": "欢乐游戏厅", "category": "娱乐", "address": "社区中心B1楼", "phone": "13800001004", "desc": "健康娱乐，快乐成长"},
        ]

        merchants = []
        merchant_users = []
        for data in merchants_data:
            # 创建商家
            merchant = Merchant(
                name=data["name"],
                category=data["category"],
                address=data["address"],
                phone=data["phone"],
                description=data["desc"],
                business_hours="09:00-21:00",
                status=MerchantStatus.ACTIVE,
                is_featured=random.random() < 0.5
            )
            db.add(merchant)
            await db.flush()
            merchants.append(merchant)

            # 创建商家用户
            merchant_user = User(
                phone=data["phone"],
                email=f"merchant{len(merchants)}@rl.cornna.xyz",
                password_hash=get_password_hash("merchant123"),
                role="merchant",
                nickname=data["name"],
                status="active"
            )
            db.add(merchant_user)
            await db.flush()

            merchant_user_rel = MerchantUser(
                merchant_id=merchant.id,
                user_id=merchant_user.id,
                role="owner",
                is_active=True
            )
            db.add(merchant_user_rel)
            merchant_users.append(merchant_user)

            print(f"  创建商家: {merchant.name} ({data['category']})")

        # 15. 创建兑换商品
        items_data = [
            # 餐饮商家商品
            {"merchant_idx": 0, "name": "营养套餐券", "energy_cost": 50, "original_price": 25, "desc": "可兑换一份营养套餐"},
            {"merchant_idx": 0, "name": "果汁饮品券", "energy_cost": 20, "original_price": 10, "desc": "可兑换一杯鲜榨果汁"},
            {"merchant_idx": 0, "name": "甜点券", "energy_cost": 30, "original_price": 15, "desc": "可兑换一份健康甜点"},
            # 运动商家商品
            {"merchant_idx": 1, "name": "运动水壶", "energy_cost": 100, "original_price": 50, "desc": "便携运动水壶一个"},
            {"merchant_idx": 1, "name": "运动毛巾", "energy_cost": 60, "original_price": 30, "desc": "吸汗运动毛巾一条"},
            {"merchant_idx": 1, "name": "跳绳", "energy_cost": 80, "original_price": 40, "desc": "专业计数跳绳一根"},
            # 教育商家商品
            {"merchant_idx": 2, "name": "笔记本", "energy_cost": 40, "original_price": 20, "desc": "精美笔记本一本"},
            {"merchant_idx": 2, "name": "文具套装", "energy_cost": 70, "original_price": 35, "desc": "学习文具套装"},
            # 娱乐商家商品
            {"merchant_idx": 3, "name": "游戏币", "energy_cost": 30, "original_price": 15, "desc": "游戏币10枚"},
            {"merchant_idx": 3, "name": "娃娃机券", "energy_cost": 50, "original_price": 25, "desc": "娃娃机游戏券3次"},
        ]

        redeem_items = []
        for data in items_data:
            merchant = merchants[data["merchant_idx"]]
            item = RedeemItem(
                merchant_id=merchant.id,
                name=data["name"],
                energy_cost=data["energy_cost"],
                original_price=Decimal(str(data["original_price"])),
                description=data["desc"],
                stock=-1,  # 无限库存
                valid_days=30,
                is_active=True
            )
            db.add(item)
            await db.flush()
            redeem_items.append(item)
            print(f"  创建兑换商品: {item.name} ({data['energy_cost']}能量)")

        print("  商家和商品数据创建完成")

        await db.commit()
        print("\n种子数据创建完成！")

        print("\n" + "=" * 60)
        print("测试账号汇总")
        print("=" * 60)
        print("\n  管理员 (1个):")
        print("    手机号: 13800000000  密码: admin123")
        print("    邮箱: admin@rl.cornna.xyz")
        print("\n  家长 (6个):")
        for p in parents_data:
            print(f"    手机号: {p['phone']}  密码: parent123  ({p['nickname']})")
        print("\n  教练 (8个):")
        for c in coaches_data:
            print(f"    手机号: {c['phone']}  密码: coach123  ({c['name']})")
        print("\n  学员 (12个):")
        for s in students_data[:6]:
            print(f"    手机号: {s['phone']}  密码: student123  ({s['name']})")
        print("    ... 更多学员请查看数据库")
        print("\n  商家 (4个):")
        for i, m in enumerate(merchants_data):
            print(f"    手机号: {m['phone']}  密码: merchant123  ({m['name']})")
        print("\n  提示: 开发模式下验证码会打印在控制台，")
        print("  也可通过 GET /api/v1/auth/dev/email-code/{email} 获取")


if __name__ == "__main__":
    asyncio.run(seed_data())
