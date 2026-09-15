from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select

from db.Models.Order import Order
from db.Models.User import User
from db.database import asyncSession
from dependencies import get_db, get_current_user, get_current_admin   # 两个权限依赖：登录校验 / 管理员校验

from schemas.order import OrderResponse,OrderCreate,OrderUpdate


router = APIRouter(prefix="/orders",tags=["订单管理"])


# 查询订单列表：管理员看所有人的，普通用户只看自己的
@router.get("/", response_model=list[OrderResponse])
async def query_all(
    current_user: User = Depends(get_current_user),   # 至少要登录，没登录直接 401
    async_db: asyncSession = Depends(get_db)
):
    sql = select(Order)
    # 权限分叉的核心三行：普通用户在"SQL 层"就加上 where user_id=自己，
    # 比查出来再用 Python 过滤更好——数据库里压根不存在的数据，用户连看都看不到
    if not current_user.is_admin:
        sql = sql.where(Order.user_id == current_user.id)
    results = await async_db.execute(sql)
    orders = results.scalars().all()
    return orders


# 根据id查询单个订单：管理员可查任意，普通用户只能查自己的
@router.get("/{id}", response_model=OrderResponse)
async def query_by_id(
    id:int,
    current_user: User = Depends(get_current_user),   # 先验登录
    async_db: asyncSession = Depends(get_db)
):
    sql = select(Order).where(Order.order_id == id)
    results = await async_db.execute(sql)
    order = results.scalars().first()

    if order is None:
        raise HTTPException(status_code=404, detail="订单不存在")
    # 查到了订单，再判断归属：不是管理员、又不是自己的 → 403
    if not current_user.is_admin and order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="只能查看自己的订单")
    return order


# 创建订单：登录即可（普通用户的核心权利就是下单）
@router.post("/",response_model=OrderResponse)
async def create_order(
    order:OrderCreate,
    current_user: User = Depends(get_current_user),   # 要登录才能下单
    async_db:asyncSession=Depends(get_db)
):
    new_order = Order(
        order_no=order.order_no,
        user_id=current_user.id,   # 关键：user_id 取自令牌解析出的"当前用户"，客户端传什么都不算数
        amount=order.amount,
        status="pending"           # 关键：新订单一律"待支付"，状态流转只能由后续业务（如支付回调）驱动
    )
    async_db.add(new_order)
    await async_db.commit()
    await async_db.refresh(new_order)
    return new_order


# 修改订单：仅管理员
@router.patch("/{id}",response_model=OrderResponse)
async def update_order(
    id:int,
    order_update:OrderUpdate,
    current_user: User = Depends(get_current_admin),   # 依赖从 get_current_user 换成 get_current_admin，普通用户在这里被 403 拦下
    async_db:asyncSession=Depends(get_db)
):
    sql = select(Order).where(Order.order_id==id)
    results = await async_db.execute(sql)
    order = results.scalars().first()
    if order is None:
        raise HTTPException(status_code=404,detail="订单不存在")
    if order_update.amount is not None:
        order.amount = order_update.amount
    if order_update.status is not None:
        order.status = order_update.status
    await async_db.commit()
    await async_db.refresh(order)
    return order


# 删除订单：仅管理员
@router.delete("/{id}")
async def delete_order(
    id:int,
    current_user: User = Depends(get_current_admin),   # 仅管理员可删
    async_db:asyncSession=Depends(get_db)
):
    sql=select(Order).where(Order.order_id==id)
    results=await async_db.execute(sql)
    order=results.scalars().first()
    if order is None:
        raise HTTPException(status_code=404,detail="订单不存在")
    await async_db.delete(order)
    await async_db.commit()
    return {"msg":"删除成功"}
