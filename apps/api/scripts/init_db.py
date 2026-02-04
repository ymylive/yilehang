"""
数据库初始化脚本
运行方式: python -m scripts.init_db
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import engine, Base
from app.models import (
    User, Student, Coach, Course, Schedule, Enrollment,
    MembershipCard, StudentMembership, CoachAvailableSlot,
    Booking, Transaction, Review, CoachFeedback
)


async def init_db():
    """初始化数据库，创建所有表"""
    print("开始创建数据库表...")

    async with engine.begin() as conn:
        # 创建所有表
        await conn.run_sync(Base.metadata.create_all)

    print("数据库表创建完成！")
    print("\n已创建的表:")
    for table in Base.metadata.sorted_tables:
        print(f"  - {table.name}")


async def drop_all():
    """删除所有表（危险操作，仅用于开发环境）"""
    print("警告：即将删除所有数据库表！")
    confirm = input("确认删除？输入 'yes' 继续: ")
    if confirm != 'yes':
        print("操作已取消")
        return

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    print("所有表已删除")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--drop":
        asyncio.run(drop_all())
    else:
        asyncio.run(init_db())
