from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase ,sessionmaker
from core.config import settings

#导入创建引擎的的包
# DeclarativeBase :定义数据库模型的类，表结构
# SQLAlchemy 是数据库操作框架；操作数据库的一个库
# ORM 是其中一种用 Python 对象操作数据库的方式。  Object Relational Mapping  对象关系映射
# sessionmaker 创建操作数据库的 Session对象，是用他来操作数据库的。

DATABASE_URL =settings. database_url
#告诉 SQLAlchemy：我要连接哪一个数据库，用什么驱动，账号密码是什么，数据库在哪里。
async_engine= create_async_engine(DATABASE_URL)            # 使用数据库连接信息 DATABASE_URL 创建一个 SQLAlchemy 的 Engine 对象。
asyncSession =async_sessionmaker(  #创建session 对象
    bind=async_engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False)


class Base(DeclarativeBase):  #为了统一管理创建一个Bsae，也可以直接继承DeclarativeBase
    pass
async def create_db():  #定义一个函数创建
    async with async_engine.begin() as conn:
        # .begin() 拿到一个连接并开启事务，退出时自动提交
        await conn.run_sync(Base.metadata.create_all)  #run_sync的作用意思：在异步环境里面执行同步函数。
""""   
        Base.metadata.create_all(engine) 就是让 SQLAlchemy 根据 ORM 模型自动在数据库里建表
        ORM模型 = 继承Base的、代表数据库表的 Python类
        Models中的User(Base)、Product(Base)这些就是ORM模型。
        就是你在Model中创建的User,然后映射到数据库
"""



