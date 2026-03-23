@echo off
REM ClawClock Windows 启动脚本

python clock.py
if %errorlevel% neq 0 (
    echo.
    echo ❌ 应用启动失败
    echo.
    pause
)
