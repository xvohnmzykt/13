@echo off
rem 在线教学资源平台 —— 启动开发服务器
chcp 65001 >nul
cd /d "%~dp0"

if not exist ".python312\python.exe" (
    echo [错误] 未找到项目内置 Python 运行时 .python312\python.exe
    exit /b 1
)

echo 正在启动 在线教学资源平台 ...
echo 首页:      http://127.0.0.1:8000/
echo 后台管理:  http://127.0.0.1:8000/admin/
echo 按 Ctrl+C 停止服务
echo.
".python312\python.exe" manage.py runserver 127.0.0.1:8000
