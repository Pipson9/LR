from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select

from db.Models.Coupon import Coupon
from db.Models.User import User
from db.database import asyncSession
from dependencies import get_db, get_current_user, get_current_admin   # 两个权限依赖

from schemas.coupon import CouponResponse,CouponCreate,CouponUpdate


router = APIRouter(prefix="/coupons",tags=["优惠券管理"])


# 查询全部优惠券：登录即可（普通用户要能看有哪些券可领，所以不能设成仅管理员）
@router.get("/",response_model=list[CouponResponse])
async def query_all(
    current_user: User = Depends(get_current_user),   # 至少要登录，未登录 401
    async_db:asyncSession=Depends(get_db)
):
    sql=select(Coupon)
    results=await async_db.execute(sql)
    coupons=results.scalars().all()
    return coupons


# 根据id查询优惠券：登录即可
@router.get("/{id}",response_model=CouponResponse)
async def query_by_id(
    id:int,
    current_user: User = Depends(get_current_user),   # 登录即可，看券不涉及个人隐私
    async_db:asyncSession=Depends(get_db)
):
    sql=select(Coupon).where(Coupon.id==id)
    results=await async_db.execute(sql)
    coupon=results.scalars().first()

    if coupon is None:raise HTTPException(status_code=404,detail="优惠券不存在")
    return coupon


# 创建优惠券：仅管理员（发券是运营动作，不能让普通用户自己造券）
@router.post("/",response_model=CouponResponse)
async def create_coupon(
    coupon:CouponCreate,
    current_user: User = Depends(get_current_admin),   # 普通用户在这里被 403 拦下
    async_db:asyncSession=Depends(get_db)
):
    new_coupon=Coupon(
        name=coupon.name,
        code=coupon.code,
        discount_amount=coupon.discount_amount,
        min_amount=coupon.min_amount,
        total_count=coupon.total_count,
        used_count=0,          # 已使用数量由服务端写死为 0——刚发的券不可能已经被用过
        start_time=coupon.start_time,
        end_time=coupon.end_time,
        status="active"        # 状态同样由服务端控制，客户端传什么都不算数
    )
    async_db.add(new_coupon)
    await async_db.commit()
    await async_db.refresh(new_coupon)
    return new_coupon


# 修改优惠券：仅管理员
@router.patch("/{id}",response_model=CouponResponse)
async def update_coupon(
    id:int,
    coupon_update:CouponUpdate,
    current_user: User = Depends(get_current_admin),   # 仅管理员
    async_db:asyncSession=Depends(get_db)
):
    sql=select(Coupon).where(Coupon.id==id)
    results=await async_db.execute(sql)
    coupon=results.scalars().first()
    if coupon is None:
        raise HTTPException(
            status_code=404,
            detail="优惠券不存在"
        )
    if coupon_update.name is not None:
        coupon.name=coupon_update.name

    if coupon_update.discount_amount is not None:
        coupon.discount_amount=coupon_update.discount_amount   # 修复原代码的笔误：discount_amoun 少写了个 t，一改金额就报 NameError

    if coupon_update.min_amount is not None:
        coupon.min_amount=coupon_update.min_amount

    if coupon_update.status is not None:
        coupon.status=coupon_update.status

    await async_db.commit()
    await async_db.refresh(coupon)
    return coupon


# 删除优惠券：仅管理员
@router.delete("/{id}")
async def delete_coupon(
    id:int,
    current_user: User = Depends(get_current_admin),   # 仅管理员
    async_db:asyncSession=Depends(get_db)
):
    sql=select(Coupon).where(Coupon.id==id)
    results=await async_db.execute(sql)
    coupon=results.scalars().first()

    if coupon is None:
        raise HTTPException(
            status_code=404,
            detail="优惠券不存在"
        )

    await async_db.delete(coupon)
    await async_db.commit()
    return {
        "msg":"删除成功"
    }
