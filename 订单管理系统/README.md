# 订单管理系统

一个前后端分离的订单管理 Demo，包含用户、商品、订单、优惠券四大模块，带图形验证码登录、JWT 鉴权、管理员权限控制。

技术栈：**FastAPI + SQLAlchemy 2.0（异步）+ MySQL** / **Vue 3 + Vite + Element Plus**。

---

## 目录结构

```
订单管理系统/
├── backend/                  FastAPI 后端，端口 8000
│   ├── main.py               应用入口，注册所有路由
│   ├── core/config.py        配置读取（真实值来自 .env）
│   ├── auth/                 JWT 签发/解析、密码哈希
│   ├── db/                   SQLAlchemy 模型与异步引擎
│   ├── Router/               用户 / 商品 / 订单 / 优惠券 / 验证码 / 文件上传
│   ├── schemas/              Pydantic 请求响应模型
│   ├── migrations/           Alembic 迁移
│   ├── tests/                端到端测试与演示数据脚本
│   ├── start_server.bat      Windows 一键启动
│   └── .env.example          环境变量模板
└── frontend/                 Vue 3 前端，端口 5173
    ├── src/views/            9 个页面
    ├── src/api/              axios 封装与全部接口调用
    ├── src/router/           路由与登录守卫
    ├── src/stores/           登录状态
    ├── vite.config.js        开发代理 /api → 127.0.0.1:8000
    └── start_frontend.bat    Windows 一键启动
```

## 功能一览

| 模块 | 说明 |
| --- | --- |
| 登录 / 注册 | 图形验证码（base64）、JWT 令牌，注册走 `POST /users/` |
| 商品管理 | 分页查询；管理员可增删改、上下架 |
| 订单管理 | 下单（订单号自动生成）；管理员可改状态、删除；普通用户只看自己的订单 |
| 优惠券 | 面额/门槛/领取进度的卡片式展示，管理员可发券编辑删除 |
| 用户管理 | 仅管理员可见，可改角色、禁用、删除（禁止删除自己） |
| 个人中心 | 资料查看 + 头像上传（multipart，2MB 限制） |

前端的菜单和按钮会按 `is_admin` 显隐，但**真正的权限校验始终在后端**。

## 快速开始

### 1. 准备数据库

```sql
CREATE DATABASE fastapi_demo CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 2. 启动后端

```bash
cd backend

python -m venv venv
# Windows: venv\Scripts\activate      macOS/Linux: source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env        # Windows: copy .env.example .env
# 编辑 .env，填入自己的数据库连接串和 JWT 密钥

python init_data.py         # 可选：初始化演示账号
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Windows 用户也可以直接双击 `backend/start_server.bat`。

后端跑起来后，接口文档在 <http://127.0.0.1:8000/docs>。

### 3. 启动前端

```bash
cd frontend
npm install
npm run dev
```

Windows 用户双击 `frontend/start_frontend.bat` 即可。浏览器打开 <http://localhost:5173>。

> 前端通过 Vite 代理把 `/api` 和 `/files` 转发到后端，所以不需要额外配跨域。

### 4. 登录

演示账号（由 `init_data.py` 创建）：

| 账号 | 密码 | 角色 |
| --- | --- | --- |
| admin | admin123 | 管理员 |
| xiaoming | 123456 | 普通用户 |

**正式部署前请务必改掉这些默认账号密码。**

## 环境变量

在 `backend/.env` 中配置：

| 变量 | 说明 | 默认值 |
| --- | --- | --- |
| `DATABASE_URL` | 数据库连接串，驱动必须是 `asyncmy` | `mysql+asyncmy://user:password@127.0.0.1:3306/fastapi_demo` |
| `SECRET_KEY` | JWT 签名密钥，生产环境换成随机长字符串 | `change-me-to-a-random-string` |
| `ALGORITHM` | JWT 签名算法 | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | 令牌有效期（分钟） | `1440`（24 小时） |

生成安全密钥：

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

`.env` 已被 `.gitignore` 排除，不会进仓库；仓库里只保留 `.env.example` 模板。

## 几个踩过的坑（写在前面，省得你再踩）

1. **必须请求带尾斜杠的路径。** 后端路由注册的是 `/products/`、`/orders/` 这类带尾斜杠的路径。请求 `/products` 时 FastAPI 会返回 307 重定向，而重定向过程会丢掉 `Authorization` 头，最终变成 401。前端 `src/api/index.js` 里已经全部加了尾斜杠。

2. **数据库驱动必须是 asyncmy，不是 pymysql。** `db/database.py` 用的是 `create_async_engine`，配同步驱动会直接报 `NoSuchModuleError`。

3. **bcrypt 只处理密码前 72 字节。** 超长密码在 bcrypt 5.x 会直接报错，`auth/security.py` 里已做截断。项目用的是 bcrypt 官方库，不是 passlib（后者已停止维护，与新版本 bcrypt 不兼容）。

4. **后端有时会打印 `SAWarning: garbage collector is trying to clean up non-checked-in connection`。** 这是连接没有显式归还连接池导致的，不影响功能。

## 安全说明

- 数据库连接串、JWT 密钥全部走 `.env`，代码里只有占位值
- 演示账号密码写在 `init_data.py` 和测试脚本里，仅用于本地演示，部署前请修改
