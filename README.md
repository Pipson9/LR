# LR

个人项目仓库，包含两个相互独立、可单独运行的项目：

```
LR/
├── RAG知识库问答/        企业知识库 RAG 检索问答系统（Python / LangChain）
└── 订单管理系统/         前后端分离的订单管理 Demo（FastAPI + Vue 3）
```

两个项目**没有任何代码依赖关系**，技术栈、依赖、启动方式都各自独立。想跑哪个就进哪个目录，详见各目录下的 README。

---

## 1. RAG知识库问答

企业知识库检索问答系统。把公司制度、产品手册、客服话术等文档灌入本地向量库，用自然语言提问，系统检索相关片段后交给大模型作答，并返回答案出处（文件名 + 页码 + 分类）。

**技术栈**：LangChain + Chroma + BGE Embedding（本地）+ 通义千问

**大致流程**：

```bash
cd RAG知识库问答
pip install -r requirements.txt
cp .env.example .env        # 填入通义千问 API Key
python build_db_index.py    # 构建向量库
python main.py              # 开始问答
```

→ 详细说明见 [RAG知识库问答/README.md](RAG知识库问答/README.md)

## 2. 订单管理系统

前后端分离的订单管理 Demo，含用户、商品、订单、优惠券四大模块，带图形验证码登录、JWT 鉴权和管理员权限控制。

**技术栈**：FastAPI + SQLAlchemy 2.0（异步）+ MySQL / Vue 3 + Vite + Element Plus

**两个服务要分别启动**：

```bash
# 后端（端口 8000）
cd 订单管理系统/backend
pip install -r requirements.txt
cp .env.example .env        # 填入数据库连接串
python -m uvicorn main:app --reload --port 8000

# 前端（端口 5173）
cd 订单管理系统/frontend
npm install
npm run dev
```

Windows 用户也可以直接双击各自目录下的 `start_server.bat` / `start_frontend.bat`。

→ 详细说明见 [订单管理系统/README.md](订单管理系统/README.md)

---

## 说明

- 所有敏感配置（数据库密码、API Key、JWT 密钥）都通过各项目内的 `.env` 提供，**不进仓库**，仓库里只有 `.env.example` 模板
- 演示账号见各项目 README，正式部署前请务必修改
