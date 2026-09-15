from fastapi import APIRouter, Depends, HTTPException, Form
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select

from db.database import asyncSession      # 原来写的是 from database import ...，目录重构后要指向 db/
from dependencies import get_db
from db.Models.User import User           # 同上，Models 现在在 db/Models/ 下面
from auth.jwt import create_token
from auth.security import verify_password
from captcha import verify_captcha, cleanup_expired
from schemas.token import Token

router = APIRouter(tags=["认证"])


# 登录接口。OAuth2PasswordRequestForm 是 FastAPI 内置的表单类，
# 会自动解析 POST 提交的 username / password 两个表单字段。
# 使用表单而不是 JSON，是为了兼容 OAuth2 标准和 Swagger 的 Authorize 按钮
# code / captcha_id 是图形验证码字段，单独用 Form(...) 接收
@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    code: str = Form(...),
    captcha_id: str = Form(...),
    async_db: asyncSession = Depends(get_db)
):
    # 0. 先校验图形验证码（一次性 + 过期判断都在 verify_captcha 里）
    cleanup_expired()
    if not verify_captcha(captcha_id, code):
        raise HTTPException(status_code=400, detail="验证码错误或已过期")

    # 1. 按用户名查用户
    sql = select(User).where(User.username == form_data.username)
    results = await async_db.execute(sql)
    user = results.scalars().first()

    # 2. 用户不存在 或 密码不对，都统一返回同一个错误信息。
    #    如果分开提示"用户不存在"/"密码错误"，攻击者就能借此探测系统里有哪些账号
    if user is None or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    # 3. 账号被禁用的用户不允许登录
    if not user.is_active:
        raise HTTPException(status_code=403, detail="账号已被禁用")

    # 4. 校验通过，签发令牌。载荷里只放 user_id（够用了，且不含敏感信息）
    token = create_token({"user_id": user.id})
    return {"access_token": token, "token_type": "bearer"}
