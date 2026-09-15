from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from Router import  Products,Order,Coupon,User,Secutity  ,  Files , Captcha # 引入登录路由，不注册它 /login 就不存在
from contextlib import asynccontextmanager
from db.database import create_db
from LOG.log import request_log_middleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db()
    yield



app = FastAPI(lifespan=lifespan)
# ===== CORS：允许前端（Vite 默认 5173）跨域调用后端接口 =====
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # 学习项目放开；生产请改成前端具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(Products.router)
app.include_router(Order.router)
app.include_router(User.router)
app.include_router(Coupon.router)
app.include_router(Captcha.router)  # 验证码接口 /captcha（登录前就能访问，无需鉴权）
app.include_router(Secutity.router)   # 登录接口在这里挂到 app 上（漏了这行 /login 就是 404）
app.middleware("http")(request_log_middleware)
app.include_router(Files.router)


app.mount("/files", StaticFiles(directory="uploads"), name="static")

@app.get('/')
def hello_world():
    return '欢迎'
