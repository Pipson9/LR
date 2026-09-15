from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from auth.jwt import decode_token
from db.database import asyncSession
from db.Models.User import User  # 注意：Models 已经挪到 db/ 目录下，import 路径要跟着改，否则启动直接报错

#新增方法
def get_db():
    asyncdb= asyncSession()
    try:
        yield asyncdb
    finally:
        asyncdb.close()
from fastapi import Query


def get_fenye(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100)
):
    return {
        "page": page,
        "page_size": page_size,
        "offset": (page - 1) * page_size
    }
"""
Engine负责连接数据库，
Session负责管理一次数据库操作过程，(会话)
db就是一个具体的Session实例，代码通过db去查询、增加、修改、删除数据库数据。
"""
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


# ----------------------- 登录认证的核心依赖 -----------------------
# 谁的接口需要"登录才能访问"，就在参数里写 Depends(get_current_user)
async def get_current_user(
    token: str = Depends(oauth2_scheme),          # 自动从请求头取令牌
    async_db: asyncSession = Depends(get_db)      # 自动拿到数据库会话
) :
    """校验令牌 → 解析出 user_id → 查数据库 → 返回当前登录的用户"""
    user_id = decode_token(token)  # 令牌无效或过期时返回 None
    if user_id is None:
        # 401 = 未认证（没登录/令牌失效）；配合响应头让 Swagger 弹出登录框
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="登录已过期或令牌无效，请重新登录",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 令牌有效，但数据库里已经没有这个用户了（比如账号已被删除）
    sql = select(User).where(User.id == user_id)
    results = await async_db.execute(sql)
    user = results.scalars().first()
    if user is None:
        raise HTTPException(status_code=401, detail="用户不存在")

    # 账号被停用（is_active=False），即使令牌有效也不放行
    if not user.is_active:
        raise HTTPException(status_code=403, detail="账号已被禁用")

    return user  # 后面的接口拿到 user，就知道"现在是谁在操作"


# ----------------------- 管理员专属依赖 -----------------------
# 谁的接口"只有管理员能用"，就在参数里写 Depends(get_current_admin)
async def get_current_admin(
    current_user: User = Depends(get_current_user)  # 先走一遍上面的登录校验
) -> User:
    """
    在 get_current_user 的基础上再加一道检查：is_admin 必须是 True。
    所以这个依赖 = 必须登录 + 必须是管理员，缺一个都进不来。
    403 = 已登录但权限不够（比如普通用户想删别人的订单）
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="权限不足，需要管理员身份")
    return current_user