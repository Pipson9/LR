"""
一键创建测试账号：管理员 admin/admin123，普通用户 xiaoming/123456。
已存在同名用户会跳过，可以放心反复执行。
"""
import asyncio
from sqlalchemy import select
from db.database import asyncSession, create_db
from db.Models.User import User
from auth.security import hash_password


async def main():
    await create_db()   # 顺带保证所有表都存在

    async with asyncSession() as db:
        for username, password, is_admin in [
            ("admin", "admin123", True),      # 管理员账号
            ("xiaoming", "123456", False),    # 普通用户账号
        ]:
            sql = select(User).where(User.username == username)
            exists = (await db.execute(sql)).scalars().first()
            if exists:
                print(f"跳过：{username} 已存在")
                continue
            db.add(User(
                username=username,
                email=f"{username}@example.com",
                hashed_password=hash_password(password),  # 存哈希不存明文
                is_active=True,
                is_admin=is_admin,
            ))
            await db.commit()
            print(f"创建成功：{username}（密码 {password}，管理员={is_admin}）")


if __name__ == "__main__":
    asyncio.run(main())
