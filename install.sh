#!/bin/bash
# ClawClock 安装脚本
# 自动检测系统并安装依赖

set -e

echo "🕐 ClawClock 安装脚本"
echo "===================="
echo ""

# 检测系统
if [ -f /etc/debian_version ]; then
    echo "📦 检测到 Debian/Ubuntu 系统"
    echo "正在更新软件包列表..."
    sudo apt update
    echo "正在安装依赖..."
    sudo apt install -y python3-tk python3-tz libgtk-3-dev libcairo2-dev gcc
elif [ -f /etc/arch-release ]; then
    echo "📦 检测到 Arch Linux 系统"
    echo "正在安装依赖..."
    sudo pacman -S --noconfirm tk python-tz gtk3 cairo gcc
elif [ -f /etc/fedora-release ]; then
    echo "📦 检测到 Fedora 系统"
    echo "正在安装依赖..."
    sudo dnf install -y python3-tkinter python3-dateutil gtk3-devel cairo-devel gcc
else
    echo "⚠️  未识别的系统，请手动安装依赖"
    echo ""
    echo "Python 版本需要："
    echo "  - python3-tk 或 tkinter"
    echo "  - python3-tz 或 tzdata"
    echo ""
    echo "C 版本需要："
    echo "  - libgtk-3-dev 或 gtk3"
    echo "  - libcairo2-dev 或 cairo"
    echo "  - gcc"
    exit 1
fi

echo ""
echo "✅ 依赖安装完成！"
echo ""
echo "🚀 使用方法:"
echo "   Python 版本：python3 clock.py"
echo "   C 版本：     make && ./clock"
echo ""
echo "📖 查看文档：cat README.md"
