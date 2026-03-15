# ClawClock Makefile
# 用于编译和运行时钟应用

# 编译器
CC = gcc
CFLAGS = `pkg-config --cflags gtk+-3.0` -lm -Wall -O2
LDFLAGS = `pkg-config --libs gtk+-3.0`

# 目标文件
TARGET = clock
SOURCE = clock.c

# Python 版本
PY_SOURCE = clock.py

.PHONY: all clean run run-py help install-deps

# 默认目标：编译 C 版本
all: $(TARGET)
	@echo "✅ 编译完成！运行 ./$(TARGET) 启动应用"

# 编译 C 版本
$(TARGET): $(SOURCE)
	@echo "🔨 编译 $(SOURCE)..."
	$(CC) -o $(TARGET) $(SOURCE) $(CFLAGS) $(LDFLAGS)
	@echo "✅ 编译成功！"

# 运行 C 版本
run: $(TARGET)
	@echo "🕐 启动 ClawClock (C 版本)..."
	./$(TARGET)

# 运行 Python 版本
run-py:
	@echo "🕐 启动 ClawClock (Python 版本)..."
	python3 $(PY_SOURCE)

# 清理编译文件
clean:
	@echo "🧹 清理编译文件..."
	rm -f $(TARGET)
	rm -f *.o
	@echo "✅ 清理完成"

# 安装依赖（Debian/Ubuntu）
install-deps:
	@echo "📦 安装依赖..."
	sudo apt update
	sudo apt install -y python3-tk python3-tz libgtk-3-dev libcairo2-dev
	@echo "✅ 依赖安装完成"

# 帮助信息
help:
	@echo "🕐 ClawClock 构建系统"
	@echo ""
	@echo "可用命令:"
	@echo "  make          - 编译 C 版本"
	@echo "  make run      - 编译并运行 C 版本"
	@echo "  make run-py   - 运行 Python 版本"
	@echo "  make clean    - 清理编译文件"
	@echo "  make install-deps - 安装依赖（Debian/Ubuntu）"
	@echo "  make help     - 显示帮助信息"
	@echo ""
	@echo "快速启动:"
	@echo "  Python: python3 clock.py"
	@echo "  C 版本：  make && ./clock"
