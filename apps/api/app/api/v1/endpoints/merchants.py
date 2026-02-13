"""
商家系统 API
"""

import secrets
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import get_current_user, get_db
from app.models import Student
from app.models.merchant import (
    Merchant,
    MerchantStatus,
    MerchantUser,
    RedeemItem,
    RedeemOrder,
    RedeemOrderStatus,
)
from app.schemas.merchant import (
    MerchantDetailResponse,
    MerchantListResponse,
    MerchantResponse,
    MerchantStatsResponse,
    MerchantUpdate,
    RedeemItemListResponse,
    RedeemItemResponse,
    RedeemOrderCreate,
    RedeemOrderListResponse,
    RedeemOrderResponse,
    RedeemOrderVerifyRequest,
    RedeemOrderVerifyResponse,
)
from app.schemas.user import Token, UserLogin, UserResponse
from app.services.auth_service import AuthService
from app.services.energy_service import EnergyService

router = APIRouter()


def _build_token_response(user) -> Token:
    access_token, expires_in = AuthService.create_token(user)
    return Token(
        access_token=access_token, expires_in=expires_in, user=UserResponse.model_validate(user)
    )


async def _build_order_detail_response(db: AsyncSession, order: RedeemOrder) -> RedeemOrderResponse:
    item_result = await db.execute(select(RedeemItem).where(RedeemItem.id == order.item_id))
    item = item_result.scalar_one_or_none()
    student_result = await db.execute(select(Student).where(Student.id == order.student_id))
    student = student_result.scalar_one_or_none()

    resp = RedeemOrderResponse.model_validate(order)
    if item:
        resp.item_name = item.name
        resp.item_image = item.image
    if student:
        resp.student_name = student.name
    return resp


@router.post("/auth/login", response_model=Token)
async def merchant_login(login_data: UserLogin, db: AsyncSession = Depends(get_db)):
    account = (login_data.account or login_data.phone or login_data.email or "").strip()
    user = await AuthService.authenticate_user(db, account, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid account or password"
        )

    if user.status != "active":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is disabled")

    merchant_user = await _get_merchant_user(db, {"user_id": user.id})
    if not merchant_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No merchant permission")

    return _build_token_response(user)


@router.get("/me", response_model=MerchantResponse)
async def get_my_merchant(
    db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)
):
    merchant_user = await _get_merchant_user(db, current_user)
    if not merchant_user:
        raise HTTPException(status_code=403, detail="No merchant permission")

    result = await db.execute(select(Merchant).where(Merchant.id == merchant_user.merchant_id))
    merchant = result.scalar_one_or_none()
    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant not found")
    return MerchantResponse.model_validate(merchant)


@router.put("/me", response_model=MerchantResponse)
async def update_my_merchant(
    data: MerchantUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    merchant_user = await _get_merchant_user(db, current_user)
    if not merchant_user:
        raise HTTPException(status_code=403, detail="No merchant permission")

    result = await db.execute(select(Merchant).where(Merchant.id == merchant_user.merchant_id))
    merchant = result.scalar_one_or_none()
    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant not found")

    updatable_fields = [
        "name",
        "logo",
        "category",
        "address",
        "phone",
        "description",
        "business_hours",
        "latitude",
        "longitude",
    ]
    for field in updatable_fields:
        value = getattr(data, field)
        if value is not None:
            setattr(merchant, field, value)

    await db.commit()
    await db.refresh(merchant)
    return MerchantResponse.model_validate(merchant)


# ============ 商家列表（学生端） ============


@router.get("", response_model=MerchantListResponse)
async def get_merchants(
    category: Optional[str] = Query(None, description="商家类别"),
    featured: Optional[bool] = Query(None, description="是否推荐"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """获取商家列表"""
    query = select(Merchant).where(Merchant.status == MerchantStatus.ACTIVE.value)

    if category:
        query = query.where(Merchant.category == category)
    if featured is not None:
        query = query.where(Merchant.is_featured == featured)

    query = query.order_by(Merchant.sort_order, Merchant.id)

    result = await db.execute(query)
    merchants = result.scalars().all()

    return MerchantListResponse(
        items=[MerchantResponse.model_validate(m) for m in merchants], total=len(merchants)
    )


@router.get("/{merchant_id}", response_model=MerchantDetailResponse)
async def get_merchant_detail(
    merchant_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """获取商家详情"""
    result = await db.execute(select(Merchant).where(Merchant.id == merchant_id))
    merchant = result.scalar_one_or_none()
    if not merchant:
        raise HTTPException(status_code=404, detail="商家不存在")

    # 统计商品数量和兑换数量
    items_count = await db.execute(
        select(func.count())
        .select_from(RedeemItem)
        .where(and_(RedeemItem.merchant_id == merchant_id, RedeemItem.is_active.is_(True)))
    )
    total_redeemed = await db.execute(
        select(func.count())
        .select_from(RedeemOrder)
        .where(
            and_(
                RedeemOrder.merchant_id == merchant_id,
                RedeemOrder.status == RedeemOrderStatus.VERIFIED.value,
            )
        )
    )

    response = MerchantDetailResponse.model_validate(merchant)
    response.items_count = items_count.scalar() or 0
    response.total_redeemed = total_redeemed.scalar() or 0

    return response


@router.get("/{merchant_id}/items", response_model=RedeemItemListResponse)
async def get_merchant_items(
    merchant_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """获取商家兑换商品列表"""
    result = await db.execute(
        select(RedeemItem)
        .where(
            and_(
                RedeemItem.merchant_id == merchant_id,
                RedeemItem.is_active.is_(True),
            )
        )
        .order_by(RedeemItem.sort_order, RedeemItem.id)
    )
    items = result.scalars().all()

    # 获取商家信息
    merchant_result = await db.execute(select(Merchant).where(Merchant.id == merchant_id))
    merchant = merchant_result.scalar_one_or_none()

    item_responses = []
    for item in items:
        resp = RedeemItemResponse.model_validate(item)
        if merchant:
            resp.merchant_name = merchant.name
            resp.merchant_logo = merchant.logo
        item_responses.append(resp)

    return RedeemItemListResponse(items=item_responses, total=len(items))


# ============ 兑换商品（全部） ============


@router.get("/items/all", response_model=RedeemItemListResponse)
async def get_all_items(
    category: Optional[str] = Query(None, description="商家类别"),
    min_cost: Optional[int] = Query(None, description="最低能量值"),
    max_cost: Optional[int] = Query(None, description="最高能量值"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """获取所有兑换商品"""
    query = (
        select(RedeemItem, Merchant)
        .join(Merchant, RedeemItem.merchant_id == Merchant.id)
        .where(and_(RedeemItem.is_active.is_(True), Merchant.status == MerchantStatus.ACTIVE.value))
    )

    if category:
        query = query.where(Merchant.category == category)
    if min_cost is not None:
        query = query.where(RedeemItem.energy_cost >= min_cost)
    if max_cost is not None:
        query = query.where(RedeemItem.energy_cost <= max_cost)

    query = query.order_by(RedeemItem.energy_cost, RedeemItem.id)

    result = await db.execute(query)
    rows = result.all()

    item_responses = []
    for item, merchant in rows:
        resp = RedeemItemResponse.model_validate(item)
        resp.merchant_name = merchant.name
        resp.merchant_logo = merchant.logo
        item_responses.append(resp)

    return RedeemItemListResponse(items=item_responses, total=len(item_responses))


# ============ 兑换操作 ============


@router.post("/redeem", response_model=RedeemOrderResponse)
async def redeem_item(
    request: RedeemOrderCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """兑换商品"""
    # 获取学员ID
    student_id = await _get_student_id(db, current_user)
    if not student_id:
        raise HTTPException(status_code=400, detail="未找到关联的学员账户")

    # 获取商品
    result = await db.execute(select(RedeemItem).where(RedeemItem.id == request.item_id))
    item = result.scalar_one_or_none()
    if not item or not item.is_active:
        raise HTTPException(status_code=404, detail="商品不存在或已下架")

    # 检查库存
    if item.stock != -1 and item.stock <= 0:
        raise HTTPException(status_code=400, detail="商品库存不足")

    # 检查用户兑换次数限制
    if item.user_limit:
        user_redeemed = await db.execute(
            select(func.count())
            .select_from(RedeemOrder)
            .where(
                and_(
                    RedeemOrder.student_id == student_id,
                    RedeemOrder.item_id == item.id,
                    RedeemOrder.status != RedeemOrderStatus.CANCELLED.value,
                )
            )
        )
        if (user_redeemed.scalar() or 0) >= item.user_limit:
            raise HTTPException(status_code=400, detail=f"每人限兑 {item.user_limit} 次")

    # 消费能量
    success, amount, balance, message = await EnergyService.spend(
        db, student_id, item.energy_cost, "redeem_order", item.id, f"兑换商品: {item.name}"
    )

    if not success:
        raise HTTPException(status_code=400, detail=message)

    # 创建订单
    order = RedeemOrder(
        order_no=_generate_order_no(),
        student_id=student_id,
        merchant_id=item.merchant_id,
        item_id=item.id,
        energy_cost=item.energy_cost,
        verify_code=_generate_verify_code(),
        status=RedeemOrderStatus.PENDING.value,
        expire_at=datetime.now(timezone.utc) + timedelta(days=item.valid_days),
    )
    db.add(order)

    # 扣减库存
    if item.stock != -1:
        item.stock -= 1

    await db.commit()
    await db.refresh(order)

    # 获取商家信息
    merchant_result = await db.execute(select(Merchant).where(Merchant.id == item.merchant_id))
    merchant = merchant_result.scalar_one_or_none()

    response = RedeemOrderResponse.model_validate(order)
    response.item_name = item.name
    response.item_image = item.image
    if merchant:
        response.merchant_name = merchant.name
        response.merchant_address = merchant.address

    return response


@router.get("/redeem/orders", response_model=RedeemOrderListResponse)
async def get_my_orders(
    status: Optional[str] = Query(None, description="订单状态"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """获取我的兑换订单"""
    student_id = await _get_student_id(db, current_user)
    if not student_id:
        raise HTTPException(status_code=400, detail="未找到关联的学员账户")

    query = select(RedeemOrder).where(RedeemOrder.student_id == student_id)

    if status:
        query = query.where(RedeemOrder.status == status)

    # 总数
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    # 分页
    query = query.order_by(RedeemOrder.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    orders = result.scalars().all()

    # 批量获取关联信息（避免 N+1 查询）
    items_map = {}
    merchants_map = {}
    students_map = {}

    if orders:
        item_ids = {order.item_id for order in orders}
        merchant_ids = {order.merchant_id for order in orders}
        student_ids = {order.student_id for order in orders}

        items_result = await db.execute(select(RedeemItem).where(RedeemItem.id.in_(item_ids)))
        items_map = {item.id: item for item in items_result.scalars().all()}

        merchants_result = await db.execute(select(Merchant).where(Merchant.id.in_(merchant_ids)))
        merchants_map = {merchant.id: merchant for merchant in merchants_result.scalars().all()}

        students_result = await db.execute(select(Student).where(Student.id.in_(student_ids)))
        students_map = {student.id: student for student in students_result.scalars().all()}

    order_responses = []
    for order in orders:
        item = items_map.get(order.item_id)
        merchant = merchants_map.get(order.merchant_id)
        student = students_map.get(order.student_id)

        resp = RedeemOrderResponse.model_validate(order)
        if item:
            resp.item_name = item.name
            resp.item_image = item.image
        if student:
            resp.student_name = student.name
        if merchant:
            resp.merchant_name = merchant.name
            resp.merchant_address = merchant.address
        order_responses.append(resp)

    return RedeemOrderListResponse(
        items=order_responses, total=total, page=page, page_size=page_size
    )


# ============ 商家端 API ============


@router.post("/redeem/{order_id}/verify", response_model=RedeemOrderVerifyResponse)
async def verify_order(
    order_id: int,
    request: RedeemOrderVerifyRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """商家核销订单"""
    # 检查商家权限
    merchant_user = await _get_merchant_user(db, current_user)
    if not merchant_user:
        raise HTTPException(status_code=403, detail="无商家权限")

    # 获取订单
    result = await db.execute(select(RedeemOrder).where(RedeemOrder.id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")

    # 检查商家归属
    if order.merchant_id != merchant_user.merchant_id:
        raise HTTPException(status_code=403, detail="无权核销此订单")

    # 检查核销码
    if order.verify_code != request.verify_code:
        return RedeemOrderVerifyResponse(success=False, message="核销码错误")

    # 检查订单状态
    if order.status == RedeemOrderStatus.VERIFIED.value:
        return RedeemOrderVerifyResponse(success=False, message="订单已核销")
    if order.status == RedeemOrderStatus.CANCELLED.value:
        return RedeemOrderVerifyResponse(success=False, message="订单已取消")
    if order.status == RedeemOrderStatus.EXPIRED.value or order.expire_at < datetime.now(
        timezone.utc
    ):
        return RedeemOrderVerifyResponse(success=False, message="订单已过期")

    # 核销
    order.status = RedeemOrderStatus.VERIFIED.value
    order.verified_at = datetime.now(timezone.utc)
    order.verified_by = current_user.get("user_id")

    await db.commit()

    return RedeemOrderVerifyResponse(
        success=True, message="核销成功", order=RedeemOrderResponse.model_validate(order)
    )


@router.post("/redeem/verify-by-code", response_model=RedeemOrderVerifyResponse)
async def verify_order_by_code(
    request: RedeemOrderVerifyRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """通过核销码核销订单（扫码核销）"""
    merchant_user = await _get_merchant_user(db, current_user)
    if not merchant_user:
        raise HTTPException(status_code=403, detail="无商家权限")

    # 根据核销码查找订单
    result = await db.execute(
        select(RedeemOrder).where(
            and_(
                RedeemOrder.verify_code == request.verify_code,
                RedeemOrder.merchant_id == merchant_user.merchant_id,
            )
        )
    )
    order = result.scalar_one_or_none()
    if not order:
        return RedeemOrderVerifyResponse(success=False, message="未找到订单或核销码错误")

    # 检查订单状态
    if order.status == RedeemOrderStatus.VERIFIED.value:
        return RedeemOrderVerifyResponse(success=False, message="订单已核销")
    if order.status == RedeemOrderStatus.CANCELLED.value:
        return RedeemOrderVerifyResponse(success=False, message="订单已取消")
    if order.expire_at < datetime.now(timezone.utc):
        order.status = RedeemOrderStatus.EXPIRED.value
        await db.commit()
        return RedeemOrderVerifyResponse(success=False, message="订单已过期")

    # 核销
    order.status = RedeemOrderStatus.VERIFIED.value
    order.verified_at = datetime.now(timezone.utc)
    order.verified_by = current_user.get("user_id")

    await db.commit()

    # 获取商品信息
    item_result = await db.execute(select(RedeemItem).where(RedeemItem.id == order.item_id))
    item = item_result.scalar_one_or_none()

    resp = RedeemOrderResponse.model_validate(order)
    if item:
        resp.item_name = item.name
        resp.item_image = item.image

    return RedeemOrderVerifyResponse(success=True, message="核销成功", order=resp)


@router.get("/redeem/code/{verify_code}", response_model=RedeemOrderResponse)
async def get_order_by_verify_code(
    verify_code: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get order detail by verification code (read only)."""
    merchant_user = await _get_merchant_user(db, current_user)
    if not merchant_user:
        raise HTTPException(status_code=403, detail="No merchant permission")

    result = await db.execute(
        select(RedeemOrder).where(
            and_(
                RedeemOrder.verify_code == verify_code,
                RedeemOrder.merchant_id == merchant_user.merchant_id,
            )
        )
    )
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return await _build_order_detail_response(db, order)


@router.get("/redeem/{order_id}", response_model=RedeemOrderResponse)
async def get_merchant_order_detail(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """Get merchant order detail by id (read only)."""
    merchant_user = await _get_merchant_user(db, current_user)
    if not merchant_user:
        raise HTTPException(status_code=403, detail="No merchant permission")

    result = await db.execute(select(RedeemOrder).where(RedeemOrder.id == order_id))
    order = result.scalar_one_or_none()
    if not order or order.merchant_id != merchant_user.merchant_id:
        raise HTTPException(status_code=404, detail="Order not found")

    item_result = await db.execute(select(RedeemItem).where(RedeemItem.id == order.item_id))
    item = item_result.scalar_one_or_none()
    student_result = await db.execute(select(Student).where(Student.id == order.student_id))
    student = student_result.scalar_one_or_none()

    resp = RedeemOrderResponse.model_validate(order)
    if item:
        resp.item_name = item.name
        resp.item_image = item.image
    if student:
        resp.student_name = student.name
    return resp


@router.get("/merchant/stats", response_model=MerchantStatsResponse)
async def get_merchant_stats(
    db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)
):
    """获取商家统计数据"""
    merchant_user = await _get_merchant_user(db, current_user)
    if not merchant_user:
        raise HTTPException(status_code=403, detail="无商家权限")

    merchant_id = merchant_user.merchant_id
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = now - timedelta(days=now.weekday())
    week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # 今日待核销
    today_pending = await db.execute(
        select(func.count())
        .select_from(RedeemOrder)
        .where(
            and_(
                RedeemOrder.merchant_id == merchant_id,
                RedeemOrder.status == RedeemOrderStatus.PENDING.value,
                RedeemOrder.created_at >= today_start,
            )
        )
    )

    # 今日已核销
    today_verified = await db.execute(
        select(func.count())
        .select_from(RedeemOrder)
        .where(
            and_(
                RedeemOrder.merchant_id == merchant_id,
                RedeemOrder.status == RedeemOrderStatus.VERIFIED.value,
                RedeemOrder.verified_at >= today_start,
            )
        )
    )

    # 本周已核销
    week_verified = await db.execute(
        select(func.count())
        .select_from(RedeemOrder)
        .where(
            and_(
                RedeemOrder.merchant_id == merchant_id,
                RedeemOrder.status == RedeemOrderStatus.VERIFIED.value,
                RedeemOrder.verified_at >= week_start,
            )
        )
    )

    # 本月已核销
    month_verified = await db.execute(
        select(func.count())
        .select_from(RedeemOrder)
        .where(
            and_(
                RedeemOrder.merchant_id == merchant_id,
                RedeemOrder.status == RedeemOrderStatus.VERIFIED.value,
                RedeemOrder.verified_at >= month_start,
            )
        )
    )

    # 总核销
    total_verified = await db.execute(
        select(func.count())
        .select_from(RedeemOrder)
        .where(
            and_(
                RedeemOrder.merchant_id == merchant_id,
                RedeemOrder.status == RedeemOrderStatus.VERIFIED.value,
            )
        )
    )

    # 总消耗能量
    total_energy = await db.execute(
        select(func.sum(RedeemOrder.energy_cost)).where(
            and_(
                RedeemOrder.merchant_id == merchant_id,
                RedeemOrder.status == RedeemOrderStatus.VERIFIED.value,
            )
        )
    )

    return MerchantStatsResponse(
        merchant_id=merchant_id,
        today_pending=today_pending.scalar() or 0,
        today_verified=today_verified.scalar() or 0,
        week_verified=week_verified.scalar() or 0,
        month_verified=month_verified.scalar() or 0,
        total_verified=total_verified.scalar() or 0,
        total_energy_consumed=total_energy.scalar() or 0,
    )


@router.get("/merchant/orders", response_model=RedeemOrderListResponse)
async def get_merchant_orders(
    status: Optional[str] = Query(None, description="订单状态"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """获取商家订单列表"""
    merchant_user = await _get_merchant_user(db, current_user)
    if not merchant_user:
        raise HTTPException(status_code=403, detail="无商家权限")

    query = select(RedeemOrder).where(RedeemOrder.merchant_id == merchant_user.merchant_id)

    if status:
        query = query.where(RedeemOrder.status == status)

    # 总数
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    # 分页
    query = query.order_by(RedeemOrder.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    orders = result.scalars().all()

    # 批量获取关联信息（避免 N+1 查询）
    items_map = {}
    students_map = {}

    if orders:
        item_ids = {order.item_id for order in orders}
        student_ids = {order.student_id for order in orders}

        items_result = await db.execute(select(RedeemItem).where(RedeemItem.id.in_(item_ids)))
        items_map = {item.id: item for item in items_result.scalars().all()}

        students_result = await db.execute(select(Student).where(Student.id.in_(student_ids)))
        students_map = {student.id: student for student in students_result.scalars().all()}

    order_responses = []
    for order in orders:
        item = items_map.get(order.item_id)
        student = students_map.get(order.student_id)

        resp = RedeemOrderResponse.model_validate(order)
        if item:
            resp.item_name = item.name
            resp.item_image = item.image
        if student:
            resp.student_name = student.name
        order_responses.append(resp)

    return RedeemOrderListResponse(
        items=order_responses, total=total, page=page, page_size=page_size
    )


# ============ 辅助函数 ============


async def _get_student_id(db: AsyncSession, current_user: dict) -> Optional[int]:
    """获取当前用户关联的学员ID"""
    user_id = current_user.get("user_id")
    role = current_user.get("role")

    if role == "student":
        result = await db.execute(select(Student.id).where(Student.user_id == user_id))
        return result.scalar_one_or_none()
    elif role == "parent":
        result = await db.execute(select(Student.id).where(Student.parent_id == user_id).limit(1))
        return result.scalar_one_or_none()

    return None


async def _get_merchant_user(db: AsyncSession, current_user: dict) -> Optional[MerchantUser]:
    """获取当前用户的商家身份"""
    user_id = current_user.get("user_id")
    result = await db.execute(
        select(MerchantUser).where(
            and_(MerchantUser.user_id == user_id, MerchantUser.is_active.is_(True))
        )
    )
    return result.scalar_one_or_none()


def _generate_order_no() -> str:
    """生成订单号"""
    return datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S") + uuid.uuid4().hex[:8].upper()


def _generate_verify_code() -> str:
    """生成核销码"""
    return secrets.token_hex(4).upper()
