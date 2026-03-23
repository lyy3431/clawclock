#!/bin/bash
#
# ClawClock 跨平台安装脚本
# =========================
#
# 支持：Linux (Debian/Ubuntu/Arch/Fedora), macOS, Windows (Git Bash)
#
# 使用方法:
#   ./install.sh           # Linux/macOS
#   install.bat            # Windows
#

set -e

echo "🕐 ClawClock 安装程序"
echo "====================="
echo ""

# 检测操作系统
detect_os() {
    case "$(uname -s 2>/dev/null || echo '')" in
        Linux*)     echo "linux";;
        Darwin*)    echo "macos";;
        MINGW*|MSYS*|CYGWIN*) echo "windows";;
        *)          echo "unknown";;
    esac
}

OS=$(detect_os)
echo "📌 检测到系统：$OS"

# 安装函数
install_linux() {
    # 检测包管理器
    if command -v apt-get &> /dev/null; then
        echo "📦 使用 apt-get 安装依赖..."
        sudo apt-get update
        sudo apt-get install -y python3 python3-tk python3-pip
    elif command -v dnf &> /dev/null; then
        echo "📦 使用 dnf 安装依赖..."
        sudo dnf install -y python3 python3-tkinter python3-pip
    elif command -v pacman &> /dev/null; then
        echo "📦 使用 pacman 安装依赖..."
        sudo pacman -S --noconfirm python tk python-pip
    elif command -v yum &> /dev/null; then
        echo "📦 使用 yum 安装依赖..."
        sudo yum install -y python3 python3-tkinter python3-pip
    else
        echo "⚠️  未检测到支持的包管理器，请手动安装 Python 3.8+ 和 tkinter"
        exit 1
    fi

    # 安装 Python 依赖
    if [ -f requirements.txt ]; then
        echo "📦 安装 Python 依赖..."
        pip3 install -r requirements.txt
    fi

    echo ""
    echo "✅ 安装完成！"
    echo ""
    echo "运行应用："
    echo "  python3 clock.py"
}

install_macos() {
    echo "📦 检查 Homebrew..."

    if ! command -v brew &> /dev/null; then
        echo "⚠️  Homebrew 未安装"
        echo "请先安装 Homebrew: https://brew.sh"
        exit 1
    fi

    echo "📦 使用 Homebrew 安装依赖..."
    brew install python@3.10

    # 安装 Python 依赖
    if [ -f requirements.txt ]; then
        echo "📦 安装 Python 依赖..."
        pip3 install -r requirements.txt
    fi

    echo ""
    echo "✅ 安装完成！"
    echo ""
    echo "运行应用："
    echo "  python3 clock.py"
}

install_windows() {
    echo "📦 检查 Python 安装..."

    if ! command -v python &> /dev/null && ! command -v python3 &> /dev/null; then
        echo "⚠️  Python 未安装"
        echo "请从 https://python.org 下载并安装 Python 3.8+"
        echo "安装时请勾选 'Add Python to PATH'"
        exit 1
    fi

    # 获取 Python 命令
    PY_CMD="python"
    if command -v python3 &> /dev/null; then
        PY_CMD="python3"
    fi

    echo "📦 Python 版本："
    $PY_CMD --version

    # 安装 Python 依赖
    if [ -f requirements.txt ]; then
        echo "📦 安装 Python 依赖..."
        $PY_CMD -m pip install -r requirements.txt
    fi

    echo ""
    echo "✅ 安装完成！"
    echo ""
    echo "运行应用："
    echo "  python clock.py"
    echo "  或双击 run.bat"
}

# 主程序
case "$OS" in
    linux)
        install_linux
        ;;
    macos)
        install_macos
        ;;
    windows)
        install_windows
        ;;
    *)
        echo "❌ 不支持的操作系统"
        exit 1
        ;;
esac
