@echo off
chcp 65001 >nul
title 订单管理系统 - 后端服务

REM ============================================================
REM  启动 FastAPI 后端（端口 8000）
REM  使用前请先激活你的 Python 虚拟环境，并安装依赖：
REM      python -m venv venv  &&  venv\Scripts\activate
REM      pip install -r requirements.txt
REM  然后复制 .env.example 为 .env，填入自己的数据库配置。
REM ============================================================

cd /d "%~dp0"

if not exist ".env" (
    echo [提示] 未找到 .env，正在从模板创建...
    copy ".env.example" ".env" >nul
    echo [提示] 请先编辑 .env 填入数据库账号密码，然后重新运行本脚本。
    pause
    exit /b
)

echo ========================================
echo   订单管理系统 - FastAPI 后端
echo   地址: http://127.0.0.1:8000
echo   接口文档: http://127.0.0.1:8000/docs
echo ========================================
echo.

python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000

pause
