from pathlib import Path
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy import select
from db.Models.User import User
from db.database import asyncSession
from dependencies import get_db, get_current_user, get_current_admin   # 引入两个权限依赖
from auth.security import hash_password   # 引入密码哈希工具
from schemas.user import (UserResponse,UserCreate,UserUpdate)

ALLOWED_AVATAR_TYPES = {
    "image/jpeg", "image/png", "image/webp",
    "image/jpg", "image/gif", "image/bmp",
}
MAX_AVATAR_SIZE = 2 * 1024 * 1024  # 2MB


router = APIRouter(prefix="/users",tags=["用户管理"])


# 查询全部用户（仅管理员）
# 对比原来的代码只是参数里多了一行 current_user=Depends(get_current_admin)，
# FastAPI 的机制：进入函数体之前会先执行依赖，权限不够在这里就被拦下（403），根本走不到查询代码
@router.get("/", response_model=list[UserResponse])
async def query_all(
    current_user: User = Depends(get_current_admin),   # 必须是管理员才能看所有用户（用户列表属于敏感信息）
    async_db: asyncSession = Depends(get_db)
):
    sql = select(User)
    results = await async_db.execute(sql)
    users = results.scalars().all()
    return users


# 根据id查询用户（登录即可，但只能查自己；管理员可查任何人）
@router.get("/{id}", response_model=UserResponse)
async def query_by_id(
    id: int,
    current_user: User = Depends(get_current_user),   # 先要求"已登录"
    async_db: asyncSession = Depends(get_db)):
    # 权限判断：不是管理员 且 查的不是自己 → 403（已登录但权限不够用 403，和没登录的 401 区分开）
    if not current_user.is_admin and current_user.id != id:
        raise HTTPException(status_code=403, detail="只能查看自己的信息")
    sql = select(User).where(User.id == id)
    results = await async_db.execute(sql)
    user = results.scalars().first()
    if user is None:raise HTTPException(status_code=404,detail="用户不存在")
    return user


# 创建用户（注册）—— 不需要登录，开放接口
@router.post("/", response_model=UserResponse)
async def create_user(
    user: UserCreate,
    async_db: asyncSession = Depends(get_db)
):

    # 先查重名/重复邮箱，给用户一个明确的报错，而不是让数据库抛裸异常
    sql = select(User).where((User.username == user.username) | (User.email == user.email))
    exists = (await async_db.execute(sql)).scalars().first()
    if exists:
        raise HTTPException(status_code=400, detail="用户名或邮箱已被注册")

    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hash_password(user.password),  # 关键改动：存进数据库的是哈希值，不是明文！
        is_active=True,    # 服务端写死，不给客户端决定的机会
        is_admin=False     # 新注册的都是普通用户；管理员只能由数据库管理员手动改
    )
    async_db.add(new_user)
    await async_db.commit()
    await async_db.refresh(new_user)
    return new_user


# 修改用户（仅管理员）——改别人的 is_admin/禁用账号都属于管理动作
@router.patch("/{id}", response_model=UserResponse)
async def update_user(
    id: int,
    user_update: UserUpdate,
    current_user: User = Depends(get_current_admin),   # 仅管理员
    async_db: asyncSession = Depends(get_db)
):
    sql = select(User).where(User.id == id)
    results = await async_db.execute(sql)
    user = results.scalars().first()
    if user is None:
        raise HTTPException(status_code=404,detail="修改的用户不存在")
    if user_update.username is not None:
        user.username = user_update.username
    if user_update.email is not None:
        user.email = user_update.email
    if user_update.is_active is not None:
        user.is_active = user_update.is_active
    if user_update.is_admin is not None:
        user.is_admin = user_update.is_admin
    await async_db.commit()
    await async_db.refresh(user)
    return user



# 上传头像：普通用户只能传自己的，管理员可帮任何人上传
@router.post("/{id}/avatar", response_model=UserResponse)
async def upload_avatar(
    id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    async_db: asyncSession = Depends(get_db)
):
    if not current_user.is_admin and current_user.id != id:
        raise HTTPException(status_code=403, detail="只能上传自己的头像")

    if file.content_type not in ALLOWED_AVATAR_TYPES:
        raise HTTPException(status_code=400, detail="请上传图片文件")

    data = await file.read()
    if len(data) > MAX_AVATAR_SIZE:
        raise HTTPException(status_code=400, detail="头像图片不能超过 2MB")

    ext = Path(file.filename).suffix or ".jpg"
    upload_dir = Path("uploads/avatars")
    upload_dir.mkdir(parents=True, exist_ok=True)
    filename = f"avatar_{id}_{uuid.uuid4().hex[:8]}{ext}"
    file_path = upload_dir / filename
    file_path.write_bytes(data)

    sql = select(User).where(User.id == id)
    results = await async_db.execute(sql)
    user = results.scalars().first()
    if user is None:
        raise HTTPException(status_code=404, detail="用户不存在")

    user.avatar = f"/files/avatars/{filename}"
    await async_db.commit()
    await async_db.refresh(user)
    return user


# 删除用户（仅管理员）
@router.delete("/{id}")
async def delete_user(
    id: int,
    current_user: User = Depends(get_current_admin),   # 仅管理员
    async_db: asyncSession = Depends(get_db)
):
    if id == current_user.id:   # 防呆：管理员把自己删了，系统就没管理员了
        raise HTTPException(status_code=400, detail="不能删除自己")
    sql = select(User).where(User.id == id)
    results = await async_db.execute(sql)
    user = results.scalars().first()
    if user is None:
        raise HTTPException(status_code=404,detail="删除的用户不存在")
    await async_db.delete(user)
    await async_db.commit()
    return {"msg":"删除成功"}
