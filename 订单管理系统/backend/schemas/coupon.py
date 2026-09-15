from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime



# 创建优惠券

class CouponCreate(BaseModel):

    name: str = Field(
        min_length=1,
        max_length=100
    )

    code: str

    discount_amount: float = Field(
        gt=0
    )

    min_amount: float = Field(
        ge=0
    )

    total_count: int = Field(
        gt=0
    )

    start_time: datetime

    end_time: datetime
    # 这里刻意去掉了 used_count 和 status 两个字段：
    # used_count（已使用数量）和 status 必须由服务端控制——
    # 如果允许客户端传，用户注册个券传 used_count=100 或直接传下架状态，数据就被污染了
    # 和订单的 user_id / status 是同一个原则：关键状态字段不信任客户端



# 修改优惠券

class CouponUpdate(BaseModel):

    name: Optional[str] = None

    discount_amount: Optional[float] = None

    min_amount: Optional[float] = None

    total_count: Optional[int] = None

    status: Optional[str] = None



# 返回优惠券

class CouponResponse(BaseModel):

    id: int

    name: str

    code: str

    discount_amount: float

    min_amount: float

    total_count: int

    used_count: int

    start_time: datetime

    end_time: datetime

    status: str

    created_at: datetime


    class Config:
        from_attributes = True