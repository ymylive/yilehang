"""
能量系统 Schemas
"""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict

# ============ 能量规则 ============

class EnergyRuleBase(BaseModel):
    """能量规则基础"""
    name: str
    code: str
    source_type: str
    points: int
    multiplier: float = 1.0
    daily_limit: Optional[int] = None
    weekly_limit: Optional[int] = None
    monthly_limit: Optional[int] = None
    description: Optional[str] = None


class EnergyRuleCreate(EnergyRuleBase):
    """创建能量规则"""
    pass


class EnergyRuleUpdate(BaseModel):
    """更新能量规则"""
    name: Optional[str] = None
    points: Optional[int] = None
    multiplier: Optional[float] = None
    daily_limit: Optional[int] = None
    weekly_limit: Optional[int] = None
    monthly_limit: Optional[int] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class EnergyRuleResponse(EnergyRuleBase):
    """能量规则响应"""
    id: int
    is_active: bool
    sort_order: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ============ 能量账户 ============

class EnergyAccountResponse(BaseModel):
    """能量账户响应"""
    id: int
    student_id: int
    balance: int
    total_earned: int
    total_spent: int
    level: int
    level_name: str = ""
    level_icon: str = ""
    next_level_points: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EnergyAccountSummary(BaseModel):
    """能量账户摘要（首页展示用）"""
    balance: int
    level: int
    level_name: str
    level_icon: str
    today_earned: int = 0
    week_earned: int = 0
    rank: Optional[int] = None


# ============ 能量交易 ============

class EnergyTransactionResponse(BaseModel):
    """能量交易记录响应"""
    id: int
    type: str
    source_type: Optional[str] = None
    amount: int
    balance_after: int
    description: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EnergyTransactionList(BaseModel):
    """能量交易记录列表"""
    items: List[EnergyTransactionResponse]
    total: int
    page: int
    page_size: int


# ============ 能量获取请求 ============

class EnergyEarnRequest(BaseModel):
    """能量获取请求（内部调用）"""
    student_id: int
    rule_code: str
    reference_type: Optional[str] = None
    reference_id: Optional[int] = None
    description: Optional[str] = None


class EnergyEarnResponse(BaseModel):
    """能量获取响应"""
    success: bool
    amount: int = 0
    balance: int = 0
    message: str = ""


# ============ 能量消费请求 ============

class EnergySpendRequest(BaseModel):
    """能量消费请求"""
    student_id: int
    amount: int
    reference_type: str
    reference_id: int
    description: Optional[str] = None


class EnergySpendResponse(BaseModel):
    """能量消费响应"""
    success: bool
    amount: int = 0
    balance: int = 0
    message: str = ""


# ============ 排行榜 ============

class LeaderboardEntry(BaseModel):
    """排行榜条目"""
    rank: int
    student_id: int
    student_name: str
    avatar: Optional[str] = None
    value: int  # 能量值/训练次数/进步分数
    level: Optional[int] = None
    level_icon: Optional[str] = None


class LeaderboardResponse(BaseModel):
    """排行榜响应"""
    type: str  # energy/training/fitness
    period: str  # week/month/all
    items: List[LeaderboardEntry]
    my_rank: Optional[int] = None
    my_value: Optional[int] = None
    updated_at: datetime
