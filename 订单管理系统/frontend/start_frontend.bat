@echo off
chcp 65001 >nul
title 订单管理系统 - 前端开发服务器

REM ============================================================
REM  启动 Vue3 前端开发服务器（端口 5173）
REM  首次运行会自动安装依赖，需要几分钟。
REM  请先确保后端已在 http://127.0.0.1:8000 运行。
REM ============================================================

cd /d "%~dp0"

if not exist "node_modules" (
    echo [提示] 首次运行，正在安装依赖...
    call npm install
    if errorlevel 1 (
        echo [错误] 依赖安装失败，请确认已安装 Node.js ^>= 18
        pause
        exit /b
    )
)

echo ========================================
echo   订单管理系统 - 前端开发服务器
echo   地址: http://localhost:5173
echo ========================================
echo.

call npm run dev

pause
