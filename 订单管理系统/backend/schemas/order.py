from pydantic import BaseModel
from typing import Optional



# 创建订单
class OrderCreate(BaseModel):

    order_no: str

    amount: float
    # 这里刻意去掉了 user_id 和 status 两个字段：
    # user_id 必须取自登录令牌——如果允许客户端传，用户就能替别人下单（越权漏洞）
    # status 由服务端强制写成 "pending"（待支付）——如果允许客户端传，用户传 "paid" 就等于白嫖
    # 记住这个原则：服务端永远不信任客户端传来的"关键归属/状态"字段



# 修改订单

class OrderUpdate(BaseModel):

    amount: Optional[float] = None

    status: Optional[str] = None



# 返回订单

class OrderResponse(BaseModel):

    order_id: int

    order_no: str

    user_id: int

    amount: float

    status: str


    class Config:
        from_attributes = True