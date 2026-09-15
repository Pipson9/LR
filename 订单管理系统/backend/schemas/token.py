from pydantic import BaseModel


# 登录成功后返回给前端的数据结构。
# 前端拿到 access_token 后，之后每次请求都放在请求头里：
# Authorization: Bearer <令牌>   （Bearer 是固定写法，意为"持有此令牌的人"）
class Token(BaseModel):
    access_token: str   # JWT 令牌本体，一长串用点分隔的字符串
    token_type: str     # 固定为 "bearer"
