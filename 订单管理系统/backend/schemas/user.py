from pydantic import BaseModel, Field
from typing import Optional


# 创建用户（注册）
class UserCreate(BaseModel):

    username: str = Field(
        min_length=1,
        max_length=500
    )

    email: str

    password: str = Field(min_length=6)  # 字段名改成 password：客户端传"明文密码"，哈希这件事由服务端做
    # 这里刻意"不收" is_active / is_admin 两个字段——
    # 如果允许客户端传 is_admin=true，任何人注册一下就能变成管理员，等于权限体系形同虚设



# 修改用户
class UserUpdate(BaseModel):

    username: Optional[str] = None

    email: Optional[str] = None

    is_active: Optional[bool] = None

    is_admin: Optional[bool] = None



# 返回用户
class UserResponse(BaseModel):

    id: int

    username: str

    email: str

    is_active: bool

    is_admin: bool

    avatar: Optional[str] = None


    class Config:
        from_attributes = True