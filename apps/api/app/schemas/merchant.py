"""
商家系统 Schemas
"""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict

# ============ 商家 ============

class MerchantBase(BaseModel):
    """商家基础"""
    name: str
    logo: Optional[str] = None
    category: str
    address: Optional[str] = None
    phone: Optional[str] = None
    description: Optional[str] = None
    business_hours: Optional[str] = None


class MerchantCreate(MerchantBase):
    """创建商家"""
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class MerchantUpdate(BaseModel):
    """更新商家"""
    name: Optional[str] = None
    logo: Optional[str] = None
    category: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    description: Optional[str] = None
    business_hours: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    status: Optional[str] = None
    is_featured: Optional[bool] = None


class MerchantResponse(MerchantBase):
    """商家响应"""
    id: int
    status: str
    is_featured: bool
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MerchantListResponse(BaseModel):
    """商家列表响应"""
    items: List[MerchantResponse]
    total: int


class MerchantDetailResponse(MerchantResponse):
    """商家详情响应"""
    items_count: int = 0
    total_redeemed: int = 0


# ============ 兑换商品 ============

class RedeemItemBase(BaseModel):
    """兑换商品基础"""
    name: str
    image: Optional[str] = None
    description: Optional[str] = None
    energy_cost: int
    original_price: Optional[float] = None
    stock: int = -1
    daily_limit: Optional[int] = None
    user_limit: Optional[int] = None
    valid_days: int = 30
    usage_rules: Optional[str] = None


class RedeemItemCreate(RedeemItemBase):
    """创建兑换商品"""
    merchant_id: int


class RedeemItemUpdate(BaseModel):
    """更新兑换商品"""
    name: Optional[str] = None
    image: Optional[str] = None
    description: Optional[str] = None
    energy_cost: Optional[int] = None
    original_price: Optional[float] = None
    stock: Optional[int] = None
    daily_limit: Optional[int] = None
    user_limit: Optional[int] = None
    valid_days: Optional[int] = None
    usage_rules: Optional[str] = None
    is_active: Optional[bool] = None


class RedeemItemResponse(RedeemItemBase):
    """兑换商品响应"""
    id: int
    merchant_id: int
    is_active: bool
    sort_order: int
    created_at: datetime
    # 附加信息
    merchant_name: Optional[str] = None
    merchant_logo: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class RedeemItemListResponse(BaseModel):
    """兑换商品列表响应"""
    items: List[RedeemItemResponse]
    total: int


# ============ 兑换订单 ============

class RedeemOrderCreate(BaseModel):
    """创建兑换订单"""
    item_id: int


class RedeemOrderResponse(BaseModel):
    """兑换订单响应"""
    id: int
    order_no: str
    student_id: int
    merchant_id: int
    item_id: int
    energy_cost: int
    verify_code: str
    status: str
    expire_at: datetime
    verified_at: Optional[datetime] = None
    created_at: datetime
    # 附加信息
    item_name: Optional[str] = None
    item_image: Optional[str] = None
    student_name: Optional[str] = None
    merchant_name: Optional[str] = None
    merchant_address: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class RedeemOrderListResponse(BaseModel):
    """兑换订单列表响应"""
    items: List[RedeemOrderResponse]
    total: int
    page: int
    page_size: int


class RedeemOrderVerifyRequest(BaseModel):
    """核销请求"""
    verify_code: str


class RedeemOrderVerifyResponse(BaseModel):
    """核销响应"""
    success: bool
    message: str
    order: Optional[RedeemOrderResponse] = None


# ============ 商家统计 ============

class MerchantStatsResponse(BaseModel):
    """商家统计响应"""
    merchant_id: int
    today_verified: int = 0
    today_pending: int = 0
    week_verified: int = 0
    month_verified: int = 0
    total_verified: int = 0
    total_energy_consumed: int = 0


# ============ 商家用户 ============

class MerchantUserResponse(BaseModel):
    """商家用户响应"""
    id: int
    merchant_id: int
    user_id: int
    role: str
    is_active: bool
    merchant_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
