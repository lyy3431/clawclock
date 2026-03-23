@echo off
REM ClawClock Windows 安装脚本
REM ==========================

echo.
echo 🕐 ClawClock 安装程序
echo =====================
echo.

REM 检查 Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  Python 未安装
    echo.
    echo 请从 https://python.org 下载并安装 Python 3.8+
    echo 安装时请勾选 'Add Python to PATH'
    pause
    exit /b 1
)

echo 📦 Python 已安装
python --version
echo.

REM 安装依赖
if exist requirements.txt (
    echo 📦 安装 Python 依赖...
    python -m pip install -r requirements.txt
) else (
    echo 📦 安装基础依赖...
    python -m pip install pytz
)

echo.
echo ✅ 安装完成！
echo.
echo 🚀 运行应用：
echo    python clock.py
echo.
pause
