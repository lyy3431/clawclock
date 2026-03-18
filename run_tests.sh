#!/bin/bash
#
# ClawClock 测试运行脚本
# =====================
#
# 使用方法:
#   ./run_tests.sh           # 运行所有测试
#   ./run_tests.sh -v        # 详细输出
#   ./run_tests.sh --help    # 显示帮助
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 显示帮助
show_help() {
    echo "🧪 ClawClock 测试套件"
    echo ""
    echo "使用方法:"
    echo "  ./run_tests.sh           运行所有测试"
    echo "  ./run_tests.sh -v        详细输出模式"
    echo "  ./run_tests.sh --help    显示此帮助信息"
    echo ""
    echo "依赖:"
    echo "  - Python 3.8+"
    echo "  - unittest (内置)"
    echo "  - pytest (可选，用于更详细的输出)"
}

# 检查 Python 版本
check_python() {
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ 错误：未找到 Python 3${NC}"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    echo -e "${GREEN}✅ Python 版本：${PYTHON_VERSION}${NC}"
}

# 运行测试
run_tests() {
    local verbose=$1
    
    echo ""
    echo "🕐 ClawClock 自动化测试"
    echo "========================"
    echo ""
    
    # 检查测试目录
    if [ ! -d "tests" ]; then
        echo -e "${RED}❌ 错误：测试目录不存在${NC}"
        exit 1
    fi
    
    # 尝试使用 pytest（如果可用）
    if command -v pytest &> /dev/null; then
        echo "📦 使用 pytest 运行测试..."
        echo ""
        if [ "$verbose" = "-v" ]; then
            python3 -m pytest tests/ -v --tb=short
        else
            python3 -m pytest tests/ --tb=short
        fi
    else
        echo "📦 使用 unittest 运行测试..."
        echo ""
        if [ "$verbose" = "-v" ]; then
            python3 -m unittest discover -s tests -v
        else
            python3 -m unittest discover -s tests
        fi
    fi
    
    local exit_code=$?
    
    echo ""
    if [ $exit_code -eq 0 ]; then
        echo -e "${GREEN}✅ 所有测试通过！${NC}"
    else
        echo -e "${RED}❌ 部分测试失败${NC}"
    fi
    
    return $exit_code
}

# 主函数
main() {
    case "${1:-}" in
        -v|--verbose)
            check_python
            run_tests -v
            ;;
        -h|--help)
            show_help
            ;;
        "")
            check_python
            run_tests
            ;;
        *)
            echo -e "${RED}❌ 未知选项：${1}${NC}"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

main "$@"
