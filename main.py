# ClawClock 主应用入口
"""
ClawClock 主应用
"""
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
from clock import ClockApp


def main():
    """主函数"""
    # 创建主窗口
    root = tk.Tk()
    
    # 初始化时钟应用
    app = ClockApp(root)
    
    # 运行主循环
    try:
        root.mainloop()
    except KeyboardInterrupt:
        # 处理 Ctrl+C
        app.on_close()


if __name__ == "__main__":
    main()
