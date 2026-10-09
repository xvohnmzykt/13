@echo off
rem 在线教学资源平台 —— 执行任意 Django 管理命令
rem 用法示例:  manage.bat migrate
rem            manage.bat createsuperuser
rem            manage.bat create_testdata
chcp 65001 >nul
cd /d "%~dp0"

if not exist ".python312\python.exe" (
    echo [错误] 未找到项目内置 Python 运行时 .python312\python.exe
    exit /b 1
)

".python312\python.exe" manage.py %*
