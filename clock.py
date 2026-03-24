#!/usr/bin/env python3
"""
ClawClock - 图形化时钟应用主入口
================================

一个支持模拟和数字时间显示的 Linux 桌面时钟应用。

功能特性:
    - 模拟时钟和数字时钟双模式
    - 多时区支持
    - 现代深色主题 UI
    - 实时更新（50ms 刷新率）
    - 闹钟功能
    - 秒表功能
    - 倒计时功能（番茄钟、休息时间）
    - 全屏支持
    - 窗口置顶

使用方法:
    python3 clock.py

依赖:
    - Python 3.8+
    - tkinter

作者：ClawClock Development Team
许可证：MIT
版本：1.6.5
"""

# ==================== 导入类型注解 ====================
from typing import Dict, List, Optional, Tuple, Any

# ==================== 版本常量 ====================
__version__ = "1.8.0"
__version_info__: Tuple[int, int, int] = (1, 8, 0)

# ==================== 导入核心模块 ====================
from clock_core import (
    get_version, Alarm, LapRecord, StopwatchState, TimerState,
    ClockCore, NTPMixin
)
from clock_display import ClockDisplayMixin
from clock_alarms import AlarmUIMixin
from clock_events import StopwatchMixin, TimerMixin, WindowEventMixin
from ui_components import UIMixin
from utils.performance import (
    performance_tracker, track_performance, measure_time,
    ClockPerformanceMonitor
)
from utils.ntp_client import NTPResult

import tkinter as tk
from tkinter import ttk
import datetime
import sys


class ClockApp(ClockCore, NTPMixin, ClockDisplayMixin, AlarmUIMixin, StopwatchMixin, TimerMixin, WindowEventMixin, UIMixin):
    """
    时钟应用主类

    通过多继承整合所有功能模块：
    - ClockCore: 核心功能（配置、主题、闹钟基础、时区）
    - ClockDisplayMixin: 显示渲染
    - AlarmUIMixin: 闹钟 UI
    - StopwatchMixin: 秒表功能
    - TimerMixin: 倒计时功能
    - WindowEventMixin: 窗口事件处理
    - UIMixin: UI 组件创建
    """

    def __init__(self, root: tk.Tk, enable_performance: bool = False) -> None:
        """初始化时钟应用

        Args:
            root: Tkinter 主窗口
            enable_performance: 是否启用性能监控
        """
        self.root = root
        self.root.title(f"ClawClock v{get_version()} - 图形时钟")

        # 性能监控
        self.performance_enabled = enable_performance
        self.perf_monitor = ClockPerformanceMonitor() if enable_performance else None

        # 加载配置文件（带性能追踪）
        if enable_performance:
            with measure_time("load_config"):
                self.config: Dict[str, Any] = self.load_config()
        else:
            self.config: Dict[str, Any] = self.load_config()

        # 加载主题
        self.themes: Dict[str, Dict[str, Any]] = self.load_themes()

        # 初始化闹钟列表
        self.alarms: List[Alarm] = []
        self.alarm_triggered: bool = False
        self._load_alarms()

        # 初始化秒表状态
        self.stopwatch: StopwatchState = StopwatchState()
        self.stopwatch_job: Optional[str] = None

        # 初始化倒计时状态
        self.timer: TimerState = TimerState()
        self.timer_job: Optional[str] = None
        self.timer_blink_job: Optional[str] = None
        self.timer_is_blinking: bool = False

        # 应用窗口配置
        window_config: Dict[str, Any] = self.config.get("window", {})
        width: int = window_config.get("width", 600)
        height: int = window_config.get("height", 500)
        resizable_raw: Any = window_config.get("resizable", True)
        resizable: bool = bool(resizable_raw) if not isinstance(resizable_raw, bool) else resizable_raw
        x: Optional[int] = self.config.get("window", {}).get("x", None)
        y: Optional[int] = self.config.get("window", {}).get("y", None)
        always_on_top: bool = self.config.get("window", {}).get("always_on_top", False)
        fullscreen: bool = self.config.get("window", {}).get("fullscreen", False)

        # 设置窗口几何信息
        if x is not None and y is not None:
            self.root.geometry(f"{width}x{height}+{x}+{y}")
        else:
            self.root.geometry(f"{width}x{height}")

        # 设置窗口是否可调整大小
        self.root.resizable(resizable, resizable)

        # 窗口置顶
        if always_on_top:
            self.root.attributes("-topmost", True)

        # 全屏模式
        if fullscreen:
            self.root.attributes("-fullscreen", True)

        # 注册窗口关闭事件处理
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # 设置窗口图标
        try:
            self.root.iconname("ClawClock")
        except Exception:
            pass

        # 默认时区
        self.timezone: str = self.config.get("timezone", "Asia/Shanghai")

        # 初始化时区列表
        self._init_timezones()

        # 从配置加载主题名
        theme_name: str = self.config.get("theme", {}).get("name", "dark")

        # 显示模式
        self.display_mode: str = self.config.get("display_mode", "digital")

        # 应用主题
        self.apply_theme(theme_name)

        # 初始化 NTP 时间同步
        self.init_ntp()

        # Setup UI
        self.setup_ui()

        # 初始化动画系统
        self.init_animations()

        # 加载倒计时配置
        self.load_timer_config()

        # Start clock update
        self.update_clock()

        # 启动闹钟检查线程
        self._check_alarms()

        # NTP 状态显示标签
        self.ntp_status_label: Optional[tk.Label] = None

    def update_ntp_status_display(self, result: Optional[NTPResult] = None) -> None:
        """更新 NTP 状态显示

        Args:
            result: NTP 同步结果，None 时从管理器获取状态
        """
        if not hasattr(self, 'ntp_status_label') or self.ntp_status_label is None:
            return

        status = self.get_ntp_status()
        status_text = status.get("status", "NTP")
        
        # 根据状态设置颜色
        if "精确" in status_text or status_text.startswith("✓"):
            color = "#00d4aa"  # 绿色
        elif "⚠" in status_text:
            color = "#ffb347"  # 橙色
        elif "✗" in status_text:
            color = "#ff6b6b"  # 红色
        else:
            color = self.text_color

        self.ntp_status_label.config(text=f"NTP: {status_text}", fg=color)

    def _trigger_alarm(self, alarm: Alarm) -> None:
        """触发闹钟（实现 AlarmManagerMixin 的抽象方法）"""
        label_text: str = f"闹钟时间到！\n\n{alarm.time}"
        if alarm.label:
            label_text += f"\n{alarm.label}"

        # 显示闹钟对话框
        dialog: tk.Toplevel = tk.Toplevel(self.root)
        dialog.title("⏰ 闹钟")
        dialog.geometry("300x200")
        dialog.attributes("-topmost", True)

        # 居中显示
        dialog_x: int = int(self.root.winfo_x() + self.root.winfo_width() / 2 - 150)
        dialog_y: int = int(self.root.winfo_y() + self.root.winfo_height() / 2 - 100)
        dialog.geometry(f"300x200+{dialog_x}+{dialog_y}")

        label: tk.Label = tk.Label(dialog, text=label_text, font=("Arial", 16), pady=20)
        label.pack()

        def stop_alarm() -> None:
            self.alarm_triggered = False
            dialog.destroy()

        btn_frame: tk.Frame = tk.Frame(dialog)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="停止闹钟", command=stop_alarm, width=10).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="稍后提醒",
                  command=lambda: self._snooze_alarm(dialog, alarm), width=10).pack(side=tk.LEFT, padx=10)

        # 渐入铃声：蜂鸣 3 次，每次间隔 1 秒
        for i in range(3):
            try:
                self.root.bell()
            except Exception:
                pass
            if i < 2:
                import time
                time.sleep(1)

        # 发送系统通知
        self.send_notification("⏰ 闹钟提醒", f"{alarm.time} - {alarm.label}" if alarm.label else alarm.time)


def main() -> None:
    """主函数 - 启动时钟应用"""
    import argparse

    parser = argparse.ArgumentParser(description="ClawClock - 图形化时钟应用")
    parser.add_argument(
        '--perf', '--performance',
        action='store_true',
        help='启用性能监控'
    )
    parser.add_argument(
        '--version',
        action='version',
        version=f'ClawClock v{get_version()}'
    )
    args = parser.parse_args()

    print("🕐 启动 ClawClock...")
    print(f"   Python 版本：{sys.version.split()[0]}")
    print(f"   Tkinter 版本：{tk.TkVersion}")
    if args.perf:
        print("   性能监控：已启用")
    print()

    root: tk.Tk = tk.Tk()

    # 设置样式
    style = ttk.Style()
    style.theme_use('clam')

    app = ClockApp(root, enable_performance=args.perf)

    print("✅ ClawClock 已启动")
    print("   提示：关闭窗口退出应用")
    print()

    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\n🚫 用户中断")

    # 打印性能报告
    if args.perf:
        performance_tracker.print_report()

    print("👋 ClawClock 已退出")


if __name__ == "__main__":
    main()
