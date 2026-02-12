"""
商家系统数据模型
"""

from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import Student, User


def utc_now_naive() -> datetime:
    """UTC now as naive datetime, matching TIMESTAMP WITHOUT TIME ZONE columns."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class MerchantStatus(str, Enum):
    """商家状态"""

    PENDING = "pending"  # 待审核
    ACTIVE = "active"  # 正常
    SUSPENDED = "suspended"  # 暂停
    CLOSED = "closed"  # 关闭


class RedeemOrderStatus(str, Enum):
    """兑换订单状态"""

    PENDING = "pending"  # 待核销
    VERIFIED = "verified"  # 已核销
    CANCELLED = "cancelled"  # 已取消
    EXPIRED = "expired"  # 已过期


class Merchant(Base):
    """合作商家表"""

    __tablename__ = "merchants"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100))  # 商家名称
    logo: Mapped[Optional[str]] = mapped_column(String(500))  # 商家Logo
    category: Mapped[str] = mapped_column(String(50))  # 商家类别：餐饮/运动/教育/娱乐
    address: Mapped[Optional[str]] = mapped_column(String(200))  # 地址
    phone: Mapped[Optional[str]] = mapped_column(String(20))  # 联系电话
    description: Mapped[Optional[str]] = mapped_column(Text)  # 商家介绍
    business_hours: Mapped[Optional[str]] = mapped_column(String(100))  # 营业时间
    latitude: Mapped[Optional[float]] = mapped_column(Numeric(10, 7))  # 纬度
    longitude: Mapped[Optional[float]] = mapped_column(Numeric(10, 7))  # 经度
    status: Mapped[str] = mapped_column(String(20), default=MerchantStatus.ACTIVE.value)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False)  # 是否推荐
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now_naive)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=utc_now_naive,
        onupdate=utc_now_naive,
    )

    # 关系
    users: Mapped[List["MerchantUser"]] = relationship("MerchantUser", back_populates="merchant")
    items: Mapped[List["RedeemItem"]] = relationship("RedeemItem", back_populates="merchant")
    orders: Mapped[List["RedeemOrder"]] = relationship("RedeemOrder", back_populates="merchant")


class MerchantUser(Base):
    """商家用户表（商家登录账号）"""

    __tablename__ = "merchant_users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    merchant_id: Mapped[int] = mapped_column(Integer, ForeignKey("merchants.id"), index=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), unique=True
    )  # 关联系统用户
    role: Mapped[str] = mapped_column(String(20), default="staff")  # owner/manager/staff
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now_naive)

    # 关系
    merchant: Mapped["Merchant"] = relationship("Merchant", back_populates="users")
    user: Mapped["User"] = relationship("User")


class RedeemItem(Base):
    """兑换商品表"""

    __tablename__ = "redeem_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    merchant_id: Mapped[int] = mapped_column(Integer, ForeignKey("merchants.id"), index=True)
    name: Mapped[str] = mapped_column(String(100))  # 商品名称
    image: Mapped[Optional[str]] = mapped_column(String(500))  # 商品图片
    description: Mapped[Optional[str]] = mapped_column(Text)  # 商品描述
    energy_cost: Mapped[int] = mapped_column(Integer)  # 所需能量值
    original_price: Mapped[Optional[float]] = mapped_column(Numeric(10, 2))  # 原价（展示用）
    stock: Mapped[int] = mapped_column(Integer, default=-1)  # 库存，-1表示无限
    daily_limit: Mapped[Optional[int]] = mapped_column(Integer)  # 每日限量
    user_limit: Mapped[Optional[int]] = mapped_column(Integer)  # 每人限兑次数
    valid_days: Mapped[int] = mapped_column(Integer, default=30)  # 兑换后有效天数
    usage_rules: Mapped[Optional[str]] = mapped_column(Text)  # 使用规则
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now_naive)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=utc_now_naive,
        onupdate=utc_now_naive,
    )

    # 关系
    merchant: Mapped["Merchant"] = relationship("Merchant", back_populates="items")
    orders: Mapped[List["RedeemOrder"]] = relationship("RedeemOrder", back_populates="item")


class RedeemOrder(Base):
    """兑换订单表"""

    __tablename__ = "redeem_orders"
    __table_args__ = (
        Index("ix_redeem_orders_student_created", "student_id", "created_at"),
        Index("ix_redeem_orders_merchant_status", "merchant_id", "status"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    order_no: Mapped[str] = mapped_column(String(32), unique=True, index=True)  # 订单号
    student_id: Mapped[int] = mapped_column(Integer, ForeignKey("students.id"), index=True)
    merchant_id: Mapped[int] = mapped_column(Integer, ForeignKey("merchants.id"), index=True)
    item_id: Mapped[int] = mapped_column(Integer, ForeignKey("redeem_items.id"))
    energy_cost: Mapped[int] = mapped_column(Integer)  # 消耗能量值
    verify_code: Mapped[str] = mapped_column(String(20), index=True)  # 核销码
    status: Mapped[str] = mapped_column(String(20), default=RedeemOrderStatus.PENDING.value)
    expire_at: Mapped[datetime] = mapped_column(DateTime)  # 过期时间
    verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime)  # 核销时间
    verified_by: Mapped[Optional[int]] = mapped_column(Integer)  # 核销人ID
    cancelled_at: Mapped[Optional[datetime]] = mapped_column(DateTime)  # 取消时间
    cancel_reason: Mapped[Optional[str]] = mapped_column(String(200))  # 取消原因
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utc_now_naive)

    # 关系
    student: Mapped["Student"] = relationship("Student")
    merchant: Mapped["Merchant"] = relationship("Merchant", back_populates="orders")
    item: Mapped["RedeemItem"] = relationship("RedeemItem", back_populates="orders")
