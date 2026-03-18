#!/usr/bin/env python3
"""
倒计时模块 - ClawClock 倒计时功能
============================

功能:
    - 精确倒计时（毫秒级）
    - 时/分/秒设置
    - 开始/暂停/重置控制
    - 预设时间快捷设置（番茄钟、短休息、长休息）
    - 时间到提醒（声音 + 视觉）
    - 7 段数码管风格显示
    - 呼吸灯效果（v1.5.0 新增）
    - 配置持久化

作者：ClawClock Development Team
版本：1.5.0
"""

import tkinter as tk
from tkinter import ttk, messagebox
import time
import datetime
import json
import os
import threading
import math
from typing import Optional, Callable, Dict, Any
from dataclasses import dataclass
from enum import Enum

# 导入呼吸灯模块
try:
    from breath_light import BreathLightEffect, BreathLightConfig, BreathMode, BreathStyle, TimerStatus
except ImportError:
    # 如果模块不存在，使用占位类
    class BreathLightEffect:
        def __init__(self, config=None): pass
        def start(self, root, callback): pass
        def stop(self, root): pass
        def set_status(self, status): pass
        def get_current_color(self): return "#00ff88"
        def apply_brightness_to_color(self, color, brightness): return color
        @classmethod
        def from_dict(cls, data): return cls()
    
    class BreathLightConfig:
        def __init__(self, **kwargs):
            self.enabled = kwargs.get('enabled', True)
            self.mode = kwargs.get('mode', 'digital')
            self.style = kwargs.get('style', 'soft')
            self.frequency = kwargs.get('frequency', 0.5)
            self.intensity = kwargs.get('intensity', 0.5)
    
    class BreathMode:
        DIGITAL = "digital"
        BACKGROUND = "background"
        BORDER = "border"
        ALL = "all"
    
    class BreathStyle:
        SOFT = "soft"
        TECH = "tech"
        COOL = "cool"
        MINIMAL = "minimal"
    
    class TimerStatus:
        NORMAL = "normal"
        WARNING = "warning"
        COMPLETED = "completed"


class TimerState(Enum):
    """倒计时状态枚举"""
    IDLE = "idle"           # 空闲状态
    RUNNING = "running"     # 运行中
    PAUSED = "paused"       # 已暂停
    COMPLETED = "completed" # 时间到


@dataclass
class PresetTime:
    """预设时间配置"""
    name: str
    hours: int = 0
    minutes: int = 0
    seconds: int = 0
    
    @property
    def total_seconds(self) -> int:
        """获取总秒数"""
        return self.hours * 3600 + self.minutes * 60 + self.seconds
    
    @classmethod
    def from_seconds(cls, name: str, total_seconds: int) -> 'PresetTime':
        """从总秒数创建预设时间"""
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return cls(name=name, hours=hours, minutes=minutes, seconds=seconds)


# 预设时间配置
PRESET_TIMES = [
    PresetTime("番茄钟", minutes=25),
    PresetTime("短休息", minutes=5),
    PresetTime("长休息", minutes=15),
    PresetTime("1 分钟", seconds=60),
    PresetTime("5 分钟", minutes=5),
    PresetTime("10 分钟", minutes=10),
    PresetTime("30 分钟", minutes=30),
    PresetTime("1 小时", hours=1),
]


class Timer:
    """
    倒计时核心类
    
    提供精确的倒计时功能，支持开始、暂停、重置和时间到提醒
    
    Attributes:
        total_duration: 总时长（秒）
        remaining_time: 剩余时间（秒）
        state: 当前状态
        on_complete: 时间到回调函数
    """
    
    def __init__(self, hours: int = 0, minutes: int = 0, seconds: int = 0):
        """
        初始化倒计时
        
        Args:
            hours: 小时数
            minutes: 分钟数
            seconds: 秒数
        """
        self.total_duration: float = hours * 3600 + minutes * 60 + seconds
        self.remaining_time: float = self.total_duration
        self.state: TimerState = TimerState.IDLE
        self.on_complete: Optional[Callable] = None
        
        self._start_time: Optional[float] = None
        self._paused_remaining: float = self.total_duration
        self._lock = threading.Lock()
    
    def set_time(self, hours: int = 0, minutes: int = 0, seconds: int = 0) -> None:
        """
        设置倒计时时间
        
        Args:
            hours: 小时数
            minutes: 分钟数
            seconds: 秒数
        """
        with self._lock:
            if self.state == TimerState.RUNNING:
                self.stop()
            
            self.total_duration = hours * 3600 + minutes * 60 + seconds
            self.remaining_time = self.total_duration
            self._paused_remaining = self.total_duration
            self.state = TimerState.IDLE
    
    def set_preset(self, preset: PresetTime) -> None:
        """
        使用预设时间设置
        
        Args:
            preset: 预设时间配置
        """
        self.set_time(preset.hours, preset.minutes, preset.seconds)
    
    def start(self) -> bool:
        """
        开始倒计时
        
        Returns:
            是否成功开始
        """
        with self._lock:
            if self.state == TimerState.RUNNING:
                return False
            
            if self.remaining_time <= 0:
                return False
            
            self._start_time = time.time()
            self.state = TimerState.RUNNING
            return True
    
    def stop(self) -> None:
        """暂停倒计时"""
        with self._lock:
            if self.state == TimerState.RUNNING and self._start_time:
                elapsed = time.time() - self._start_time
                self.remaining_time = max(0, self.remaining_time - elapsed)
                self._paused_remaining = self.remaining_time
                self.state = TimerState.PAUSED
    
    def reset(self) -> None:
        """重置倒计时"""
        with self._lock:
            self.state = TimerState.IDLE
            self.remaining_time = self.total_duration
            self._start_time = None
            self._paused_remaining = self.total_duration
    
    def pause(self) -> None:
        """暂停倒计时（别名）"""
        self.stop()
    
    def get_remaining(self) -> float:
        """
        获取剩余时间
        
        Returns:
            剩余时间（秒）
        """
        with self._lock:
            if self.state == TimerState.RUNNING and self._start_time:
                elapsed = time.time() - self._start_time
                remaining = self.remaining_time - elapsed
                if remaining <= 0:
                    self.remaining_time = 0
                    self.state = TimerState.COMPLETED
                    self._trigger_complete()
                    return 0
                return remaining
            return self.remaining_time
    
    def is_running(self) -> bool:
        """检查是否正在运行"""
        return self.state == TimerState.RUNNING
    
    def is_completed(self) -> bool:
        """检查是否已完成"""
        return self.state == TimerState.COMPLETED
    
    def _trigger_complete(self) -> None:
        """触发完成回调"""
        if self.on_complete:
            try:
                self.on_complete()
            except Exception as e:
                print(f"Timer completion callback error: {e}")
    
    def format_time(self, seconds: Optional[float] = None) -> str:
        """
        格式化时间为显示字符串
        
        Args:
            seconds: 要格式化的时间（秒），None 则使用剩余时间
            
        Returns:
            格式化后的时间字符串 (HH:MM:SS)
        """
        if seconds is None:
            seconds = self.get_remaining()
        
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    
    def format_time_detailed(self, seconds: Optional[float] = None) -> str:
        """
        格式化时间为详细显示字符串（包含毫秒）
        
        Args:
            seconds: 要格式化的时间（秒）
            
        Returns:
            格式化后的时间字符串 (HH:MM:SS.ms)
        """
        if seconds is None:
            seconds = self.get_remaining()
        
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        ms = int((seconds % 1) * 100)
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}.{ms:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}.{ms:02d}"
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "total_duration": self.total_duration,
            "remaining_time": self.remaining_time,
            "state": self.state.value
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Timer':
        """从字典创建实例"""
        timer = cls()
        timer.total_duration = data.get("total_duration", 0)
        timer.remaining_time = data.get("remaining_time", 0)
        timer.state = TimerState(data.get("state", "idle"))
        timer._paused_remaining = timer.remaining_time
        return timer


class SevenSegmentDisplay(tk.Canvas):
    """
    7 段数码管显示组件
    
    模拟电子数码管的显示效果
    """
    
    def __init__(self, parent: tk.Widget, digits: int = 6, **kwargs):
        """
        初始化数码管显示
        
        Args:
            parent: 父容器
            digits: 数字位数（默认 6 位：HHMMSS）
        """
        super().__init__(parent, **kwargs)
        self.digits = digits
        self.segment_width = 40
        self.segment_height = 80
        self.gap = 10
        self.colon_width = 20
        
        self._segments = []
        self._colons = []
        self._setup_display()
    
    def _setup_display(self) -> None:
        """设置显示组件"""
        self._create_segments()
    
    def _create_segments(self) -> None:
        """创建数码管段"""
        self._segments = []
        self._colons = []
        
        x_offset = 50
        y_offset = 50
        
        # 创建数字段（6 位数字：HH:MM:SS）
        digit_positions = [
            (0, 1),  # 小时十位
            (2, 3),  # 小时个位
            (4, 5),  # 分钟十位
            (6, 7),  # 分钟个位
            (8, 9),  # 秒钟十位
            (10, 11) # 秒钟个位
        ]
        
        for i, (start_idx, end_idx) in enumerate(digit_positions):
            x = x_offset + i * (self.segment_width + self.gap)
            if i >= 2:  # 在小时和分钟之间添加冒号
                x += self.colon_width
            if i >= 4:  # 在分钟和秒钟之间添加冒号
                x += self.colon_width
            
            # 创建数字的 7 个段
            segments = self._create_digit(x, y_offset)
            self._segments.append(segments)
        
        # 创建冒号
        self._create_colons()
    
    def _create_digit(self, x: float, y: float) -> list:
        """
        创建单个数字的 7 个段
        
        Returns:
            7 个段的 ID 列表
        """
        w = self.segment_width
        h = self.segment_height
        thickness = 8
        
        segments = []
        
        # 段 A (顶部横)
        seg_a = self.create_polygon(
            x, y,
            x + w, y,
            x + w - thickness, y + thickness,
            x + thickness, y + thickness,
            fill="#331111",
            tags="seg"
        )
        segments.append(seg_a)
        
        # 段 B (右上竖)
        seg_b = self.create_polygon(
            x + w, y,
            x + w, y + h/2,
            x + w - thickness, y + h/2 - thickness,
            x + w - thickness, y + thickness,
            fill="#331111",
            tags="seg"
        )
        segments.append(seg_b)
        
        # 段 C (右下竖)
        seg_c = self.create_polygon(
            x + w, y + h/2,
            x + w, y + h,
            x + w - thickness, y + h - thickness,
            x + w - thickness, y + h/2 + thickness,
            fill="#331111",
            tags="seg"
        )
        segments.append(seg_c)
        
        # 段 D (底部横)
        seg_d = self.create_polygon(
            x, y + h,
            x + w, y + h,
            x + w - thickness, y + h - thickness,
            x + thickness, y + h - thickness,
            fill="#331111",
            tags="seg"
        )
        segments.append(seg_d)
        
        # 段 E (左下竖)
        seg_e = self.create_polygon(
            x, y + h/2,
            x, y + h,
            x + thickness, y + h - thickness,
            x + thickness, y + h/2 + thickness,
            fill="#331111",
            tags="seg"
        )
        segments.append(seg_e)
        
        # 段 F (左上竖)
        seg_f = self.create_polygon(
            x, y,
            x, y + h/2,
            x + thickness, y + h/2 - thickness,
            x + thickness, y + thickness,
            fill="#331111",
            tags="seg"
        )
        segments.append(seg_f)
        
        # 段 G (中间横)
        seg_g = self.create_polygon(
            x, y + h/2,
            x + w, y + h/2,
            x + w - thickness, y + h/2 - thickness,
            x + thickness, y + h/2 - thickness,
            fill="#331111",
            tags="seg"
        )
        segments.append(seg_g)
        
        return segments
    
    def _create_colons(self) -> None:
        """创建冒号分隔符"""
        # 小时和分钟之间的冒号
        x1 = 50 + 2 * (self.segment_width + self.gap) + self.colon_width // 2
        y_center = 50 + self.segment_height // 2
        
        dot1 = self.create_oval(
            x1 - 5, y_center - 25,
            x1 + 5, y_center - 15,
            fill="#ff3333"
        )
        dot2 = self.create_oval(
            x1 - 5, y_center + 15,
            x1 + 5, y_center + 25,
            fill="#ff3333"
        )
        self._colons.append((dot1, dot2))
        
        # 分钟和秒钟之间的冒号
        x2 = 50 + 4 * (self.segment_width + self.gap) + self.colon_width * 1.5
        dot3 = self.create_oval(
            x2 - 5, y_center - 25,
            x2 + 5, y_center - 15,
            fill="#ff3333"
        )
        dot4 = self.create_oval(
            x2 - 5, y_center + 15,
            x2 + 5, y_center + 25,
            fill="#ff3333"
        )
        self._colons.append((dot3, dot4))
    
    def display_time(self, hours: int, minutes: int, seconds: int) -> None:
        """
        显示时间
        
        Args:
            hours: 小时 (0-99)
            minutes: 分钟 (0-59)
            seconds: 秒钟 (0-59)
        """
        digits = [
            hours // 10, hours % 10,
            minutes // 10, minutes % 10,
            seconds // 10, seconds % 10
        ]
        
        for i, digit in enumerate(digits):
            self._display_digit(i, digit)
    
    def _display_digit(self, position: int, digit: int) -> None:
        """
        显示单个数字
        
        Args:
            position: 位置索引 (0-5)
            digit: 数字 (0-9)
        """
        if position >= len(self._segments):
            return
        
        segments = self._segments[position]
        # 7 段数码管的段映射：A=0, B=1, C=2, D=3, E=4, F=5, G=6
        segment_map = {
            0: [1, 1, 1, 1, 1, 1, 0],  # 0: ABCDEF
            1: [0, 1, 1, 0, 0, 0, 0],  # 1: BC
            2: [1, 1, 0, 1, 1, 0, 1],  # 2: ABDEG
            3: [1, 1, 1, 1, 0, 0, 1],  # 3: ABCDG
            4: [0, 1, 1, 0, 0, 1, 1],  # 4: BCFG
            5: [1, 0, 1, 1, 0, 1, 1],  # 5: ACDFG
            6: [1, 0, 1, 1, 1, 1, 1],  # 6: ACDEFG
            7: [1, 1, 1, 0, 0, 0, 0],  # 7: ABC
            8: [1, 1, 1, 1, 1, 1, 1],  # 8: ABCDEFG
            9: [1, 1, 1, 1, 0, 1, 1],  # 9: ABCDFG
        }
        
        pattern = segment_map.get(digit, [0] * 7)
        on_color = "#ff3333"
        off_color = "#331111"
        
        for i, seg_id in enumerate(segments):
            color = on_color if pattern[i] else off_color
            self.itemconfig(seg_id, fill=color)
    
    def set_colors(self, on_color: str = "#ff3333", off_color: str = "#331111") -> None:
        """设置颜色"""
        for segments in self._segments:
            for seg_id in segments:
                self.itemconfig(seg_id, fill=off_color)


class TimerWidget:
    """
    倒计时 UI 组件
    
    提供倒计时的图形界面，包括时间显示、控制按钮和预设时间选择
    
    Attributes:
        parent: 父容器
        timer: 倒计时实例
        theme_colors: 主题颜色配置
        sound_enabled: 是否启用声音提醒
    """
    
    def __init__(self, parent: tk.Widget, theme_colors: dict, config_path: str = "config.json"):
        """
        初始化倒计时组件
        
        Args:
            parent: 父容器
            theme_colors: 主题颜色配置
            config_path: 配置文件路径
        """
        self.parent = parent
        self.theme = theme_colors
        self.config_path = config_path
        self.timer = Timer()
        self.sound_enabled = True
        self._update_job: Optional[str] = None
        self._blink_job: Optional[str] = None
        self._is_blinking = False
        
        # 呼吸灯效果（v1.5.0 新增）
        self.breath_light: Optional[BreathLightEffect] = None
        self._breath_display_items = []  # 需要应用呼吸效果的元素
        self._breath_enabled = False
        
        self._setup_ui()
        self._load_config()
    
    def _setup_ui(self) -> None:
        """设置 UI 组件"""
        # 主框架
        self.main_frame = tk.Frame(self.parent, bg=self.theme['background'])
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 时间显示区域
        self._create_display_frame()
        
        # 预设时间选择区域
        self._create_preset_frame()
        
        # 时间设置区域
        self._create_time_input_frame()
        
        # 控制按钮区域
        self._create_control_frame()
    
    def _create_display_frame(self) -> None:
        """创建时间显示区域"""
        display_frame = tk.Frame(self.main_frame, bg=self.theme['background'])
        display_frame.pack(pady=20)
        
        # 7 段数码管显示
        self.seven_segment = SevenSegmentDisplay(
            display_frame,
            digits=6,
            width=500,
            height=150,
            bg=self.theme['background']
        )
        self.seven_segment.pack()
        
        # 备用文本显示（更清晰）
        self.time_label = tk.Label(
            display_frame,
            text="00:00:00",
            font=("Courier New", 48, "bold"),
            fg=self.theme['text'],
            bg=self.theme['background']
        )
        self.time_label.pack(pady=10)
        
        # 状态标签
        self.status_label = tk.Label(
            display_frame,
            text="准备就绪",
            font=("Arial", 14),
            fg=self.theme['text'],
            bg=self.theme['background']
        )
        self.status_label.pack()
    
    def _create_preset_frame(self) -> None:
        """创建预设时间选择区域"""
        preset_frame = tk.LabelFrame(
            self.main_frame,
            text="⏱️ 预设时间",
            font=("Arial", 12, "bold"),
            fg=self.theme['text'],
            bg=self.theme['background']
        )
        preset_frame.pack(fill=tk.X, pady=10)
        
        # 预设按钮网格
        buttons_per_row = 4
        for i, preset in enumerate(PRESET_TIMES):
            row = i // buttons_per_row
            col = i % buttons_per_row
            
            btn = tk.Button(
                preset_frame,
                text=f"{preset.name}\n({preset.total_seconds // 60}分钟)" if preset.total_seconds >= 60 else f"{preset.name}\n({preset.total_seconds}秒)",
                font=("Arial", 10),
                width=12,
                height=2,
                bg=self.theme['face'],
                fg=self.theme['text'],
                activebackground=self.theme['accent'],
                activeforeground=self.theme['text'],
                command=lambda p=preset: self._set_preset_time(p)
            )
            btn.grid(row=row, column=col, padx=5, pady=5)
        
        # 自定义按钮
        custom_btn = tk.Button(
            preset_frame,
            text="🔧 自定义",
            font=("Arial", 10),
            width=12,
            height=2,
            bg=self.theme['accent'],
            fg=self.theme['text'],
            activebackground=self.theme['hand'],
            activeforeground=self.theme['text'],
            command=self._show_custom_time_dialog
        )
        custom_btn.grid(row=len(PRESET_TIMES) // buttons_per_row, column=len(PRESET_TIMES) % buttons_per_row, padx=5, pady=5)
    
    def _create_time_input_frame(self) -> None:
        """创建时间输入区域"""
        input_frame = tk.Frame(self.main_frame, bg=self.theme['background'])
        input_frame.pack(pady=10)
        
        tk.Label(
            input_frame,
            text="时:",
            font=("Arial", 12),
            fg=self.theme['text'],
            bg=self.theme['background']
        ).pack(side=tk.LEFT, padx=5)
        
        self.hours_var = tk.StringVar(value="00")
        self.hours_entry = tk.Spinbox(
            input_frame,
            from_=0,
            to=99,
            width=3,
            font=("Arial", 14),
            textvariable=self.hours_var,
            bg=self.theme['face'],
            fg=self.theme['text']
        )
        self.hours_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Label(
            input_frame,
            text="分:",
            font=("Arial", 12),
            fg=self.theme['text'],
            bg=self.theme['background']
        ).pack(side=tk.LEFT, padx=5)
        
        self.minutes_var = tk.StringVar(value="00")
        self.minutes_entry = tk.Spinbox(
            input_frame,
            from_=0,
            to=59,
            width=3,
            font=("Arial", 14),
            textvariable=self.minutes_var,
            bg=self.theme['face'],
            fg=self.theme['text']
        )
        self.minutes_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Label(
            input_frame,
            text="秒:",
            font=("Arial", 12),
            fg=self.theme['text'],
            bg=self.theme['background']
        ).pack(side=tk.LEFT, padx=5)
        
        self.seconds_var = tk.StringVar(value="00")
        self.seconds_entry = tk.Spinbox(
            input_frame,
            from_=0,
            to=59,
            width=3,
            font=("Arial", 14),
            textvariable=self.seconds_var,
            bg=self.theme['face'],
            fg=self.theme['text']
        )
        self.seconds_entry.pack(side=tk.LEFT, padx=5)
        
        # 设置按钮
        set_btn = tk.Button(
            input_frame,
            text="⏰ 设置",
            font=("Arial", 12),
            bg=self.theme['accent'],
            fg=self.theme['text'],
            command=self._apply_time_input
        )
        set_btn.pack(side=tk.LEFT, padx=15)
    
    def _create_control_frame(self) -> None:
        """创建控制按钮区域"""
        control_frame = tk.Frame(self.main_frame, bg=self.theme['background'])
        control_frame.pack(pady=20)
        
        btn_width = 12
        btn_padx = 10
        
        # 开始/暂停按钮
        self.start_stop_btn = tk.Button(
            control_frame,
            text="▶ 开始",
            font=("Arial", 14, "bold"),
            width=btn_width,
            bg=self.theme['accent'],
            fg=self.theme['text'],
            activebackground=self.theme['hand'],
            activeforeground=self.theme['text'],
            command=self._toggle_start_stop
        )
        self.start_stop_btn.pack(side=tk.LEFT, padx=btn_padx)
        
        # 重置按钮
        self.reset_btn = tk.Button(
            control_frame,
            text="🔄 重置",
            font=("Arial", 14),
            width=btn_width,
            bg=self.theme['face'],
            fg=self.theme['text'],
            activebackground=self.theme['accent'],
            activeforeground=self.theme['text'],
            command=self._reset
        )
        self.reset_btn.pack(side=tk.LEFT, padx=btn_padx)
        
        # 声音开关
        self.sound_var = tk.BooleanVar(value=True)
        self.sound_btn = tk.Checkbutton(
            control_frame,
            text="🔊 声音提醒",
            font=("Arial", 12),
            variable=self.sound_var,
            fg=self.theme['text'],
            bg=self.theme['background'],
            selectcolor=self.theme['face'],
            command=self._toggle_sound
        )
        self.sound_btn.pack(side=tk.LEFT, padx=btn_padx)
    
    def _set_preset_time(self, preset: PresetTime) -> None:
        """设置预设时间"""
        self.timer.set_preset(preset)
        self.hours_var.set(f"{preset.hours:02d}")
        self.minutes_var.set(f"{preset.minutes:02d}")
        self.seconds_var.set(f"{preset.seconds:02d}")
        self._update_display()
        self.status_label.config(text=f"已设置：{preset.name}")
        self._save_config()
    
    def _show_custom_time_dialog(self) -> None:
        """显示自定义时间对话框"""
        dialog = tk.Toplevel(self.parent)
        dialog.title("自定义时间")
        dialog.geometry("300x200")
        dialog.configure(bg=self.theme['background'])
        
        tk.Label(
            dialog,
            text="设置倒计时时间",
            font=("Arial", 16, "bold"),
            fg=self.theme['text'],
            bg=self.theme['background']
        ).pack(pady=20)
        
        input_frame = tk.Frame(dialog, bg=self.theme['background'])
        input_frame.pack(pady=10)
        
        # 小时
        tk.Label(
            input_frame,
            text="小时 (0-99):",
            font=("Arial", 12),
            fg=self.theme['text'],
            bg=self.theme['background']
        ).grid(row=0, column=0, padx=10, pady=5)
        
        custom_hours = tk.Spinbox(
            input_frame,
            from_=0,
            to=99,
            width=5,
            font=("Arial", 14),
            bg=self.theme['face'],
            fg=self.theme['text']
        )
        custom_hours.grid(row=0, column=1, padx=10, pady=5)
        
        # 分钟
        tk.Label(
            input_frame,
            text="分钟 (0-59):",
            font=("Arial", 12),
            fg=self.theme['text'],
            bg=self.theme['background']
        ).grid(row=1, column=0, padx=10, pady=5)
        
        custom_minutes = tk.Spinbox(
            input_frame,
            from_=0,
            to=59,
            width=5,
            font=("Arial", 14),
            bg=self.theme['face'],
            fg=self.theme['text']
        )
        custom_minutes.grid(row=1, column=1, padx=10, pady=5)
        
        # 秒钟
        tk.Label(
            input_frame,
            text="秒钟 (0-59):",
            font=("Arial", 12),
            fg=self.theme['text'],
            bg=self.theme['background']
        ).grid(row=2, column=0, padx=10, pady=5)
        
        custom_seconds = tk.Spinbox(
            input_frame,
            from_=0,
            to=59,
            width=5,
            font=("Arial", 14),
            bg=self.theme['face'],
            fg=self.theme['text']
        )
        custom_seconds.grid(row=2, column=1, padx=10, pady=5)
        
        def apply_custom():
            try:
                h = int(custom_hours.get())
                m = int(custom_minutes.get())
                s = int(custom_seconds.get())
                self.timer.set_time(h, m, s)
                self.hours_var.set(f"{h:02d}")
                self.minutes_var.set(f"{m:02d}")
                self.seconds_var.set(f"{s:02d}")
                self._update_display()
                self.status_label.config(text=f"已设置自定义时间：{h}小时{m}分{s}秒")
                self._save_config()
                dialog.destroy()
            except ValueError:
                messagebox.showerror("错误", "请输入有效的数字")
        
        tk.Button(
            dialog,
            text="确定",
            font=("Arial", 12),
            bg=self.theme['accent'],
            fg=self.theme['text'],
            command=apply_custom
        ).pack(pady=20)
    
    def _apply_time_input(self) -> None:
        """应用时间输入"""
        try:
            h = int(self.hours_var.get())
            m = int(self.minutes_var.get())
            s = int(self.seconds_var.get())
            self.timer.set_time(h, m, s)
            self._update_display()
            self.status_label.config(text="已设置时间")
            self._save_config()
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字")
    
    def _toggle_start_stop(self) -> None:
        """切换开始/暂停状态"""
        if self.timer.is_running():
            self.timer.stop()
            self.start_stop_btn.config(text="▶ 开始")
            self.status_label.config(text="已暂停")
            if self._update_job:
                self.parent.after_cancel(self._update_job)
                self._update_job = None
            # 暂停呼吸灯
            if self._breath_enabled:
                self._stop_breath_light()
        else:
            if self.timer.start():
                self.start_stop_btn.config(text="⏸ 暂停")
                self.status_label.config(text="倒计时中...")
                # 启动呼吸灯
                if self._breath_enabled:
                    self._start_breath_light()
                self._start_update_loop()
    
    def _reset(self) -> None:
        """重置倒计时"""
        self.timer.reset()
        self._update_display()
        self.start_stop_btn.config(text="▶ 开始")
        self.status_label.config(text="准备就绪")
        self._stop_blink()
        # 停止呼吸灯
        if self._breath_enabled:
            self._stop_breath_light()
        self._save_config()
    
    def _toggle_sound(self) -> None:
        """切换声音开关"""
        self.sound_enabled = self.sound_var.get()
        self._save_config()
    
    def _start_update_loop(self) -> None:
        """启动时间更新循环"""
        self._update_display()
    
    def _update_display(self) -> None:
        """更新时间显示"""
        remaining = self.timer.get_remaining()
        
        # 更新 7 段数码管
        hours = int(remaining // 3600)
        minutes = int((remaining % 3600) // 60)
        seconds = int(remaining % 60)
        self.seven_segment.display_time(hours, minutes, seconds)
        
        # 更新文本显示
        self.time_label.config(text=self.timer.format_time(remaining))
        
        # 更新呼吸灯状态
        if self._breath_enabled and self.breath_light:
            self._update_breath_status(remaining)
        
        # 检查是否完成
        if self.timer.is_completed():
            self._on_timer_complete()
        elif self.timer.is_running():
            # 继续更新
            self._update_job = self.parent.after(100, self._update_display)
    
    def _on_timer_complete(self) -> None:
        """倒计时完成处理"""
        self.status_label.config(text="⏰ 时间到！")
        self.start_stop_btn.config(text="▶ 开始")
        
        # 更新呼吸灯状态为完成
        if self._breath_enabled and self.breath_light:
            self.breath_light.set_status(TimerStatus.COMPLETED)
        
        # 视觉提醒：闪烁
        self._start_blink()
        
        # 声音提醒
        if self.sound_enabled:
            self._play_alarm()
    
    def _start_blink(self) -> None:
        """开始闪烁提醒"""
        self._is_blinking = True
        self._blink_state = True
        self._blink_loop()
    
    def _blink_loop(self) -> None:
        """闪烁循环"""
        if not self._is_blinking:
            return
        
        self._blink_state = not self._blink_state
        if self._blink_state:
            self.time_label.config(fg="#ff0000")
            self.main_frame.config(bg="#330000")
        else:
            self.time_label.config(fg=self.theme['text'])
            self.main_frame.config(bg=self.theme['background'])
        
        self._blink_job = self.parent.after(500, self._blink_loop)
    
    def _stop_blink(self) -> None:
        """停止闪烁"""
        self._is_blinking = False
        if self._blink_job:
            self.parent.after_cancel(self._blink_job)
            self._blink_job = None
        self.time_label.config(fg=self.theme['text'])
        self.main_frame.config(bg=self.theme['background'])
    
    def _play_alarm(self) -> None:
        """播放提示音"""
        try:
            # 使用系统蜂鸣声
            self.parent.bell()
        except Exception as e:
            print(f"Alarm sound error: {e}")
    
    def _load_config(self) -> None:
        """加载配置"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                timer_config = config.get('timer', {})
                if timer_config:
                    remaining = timer_config.get('remaining_time', 0)
                    if remaining > 0:
                        self.timer.remaining_time = remaining
                        self.timer.total_duration = timer_config.get('total_duration', remaining)
                        self._update_display()
                
                self.sound_enabled = timer_config.get('sound_enabled', True)
                self.sound_var.set(self.sound_enabled)
                
                # 初始化呼吸灯效果（v1.5.0）
                self._init_breath_light(config)
        except Exception as e:
            print(f"Load timer config error: {e}")
    
    def _save_config(self) -> None:
        """保存配置"""
        try:
            config = {}
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            
            config['timer'] = {
                'total_duration': self.timer.total_duration,
                'remaining_time': self.timer.remaining_time,
                'sound_enabled': self.sound_enabled
            }
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Save timer config error: {e}")
    
    # ========== 呼吸灯效果方法（v1.5.0 新增）==========
    
    def _init_breath_light(self, config_data: dict) -> None:
        """
        初始化呼吸灯效果
        
        Args:
            config_data: 配置数据
        """
        breath_config = config_data.get('breath_light', {})
        
        if not breath_config.get('enabled', True):
            self._breath_enabled = False
            return
        
        self._breath_enabled = True
        
        # 创建呼吸灯配置
        breath_light_config = BreathLightConfig(
            enabled=breath_config.get('enabled', True),
            mode=BreathMode(breath_config.get('mode', 'digital')),
            style=BreathStyle(breath_config.get('style', 'soft')),
            frequency=breath_config.get('frequency', 0.5),
            intensity=breath_config.get('intensity', 0.5),
            normal_color=breath_config.get('color_scheme', {}).get('normal', '#00d4aa'),
            warning_color=breath_config.get('color_scheme', {}).get('warning', '#ffb347'),
            completed_color=breath_config.get('color_scheme', {}).get('completed', '#ff6b6b'),
            accelerate_on_complete=breath_config.get('accelerate_on_complete', True),
            smooth_curve=breath_config.get('smooth_curve', True)
        )
        
        self.breath_light = BreathLightEffect(breath_light_config)
        
        # 注册需要应用呼吸效果的元素
        self._register_breath_items()
    
    def _register_breath_items(self) -> None:
        """注册需要应用呼吸效果的显示元素"""
        self._breath_display_items = []
        
        # 注册 7 段数码管的所有段
        if hasattr(self.seven_segment, '_segments'):
            for digit_segments in self.seven_segment._segments:
                for seg_id in digit_segments:
                    self._breath_display_items.append((self.seven_segment, seg_id))
        
        # 注册文本标签
        self._breath_display_items.append(self.time_label)
        self._breath_display_items.append(self.status_label)
    
    def _start_breath_light(self) -> None:
        """启动呼吸灯效果"""
        if self._breath_enabled and self.breath_light:
            self.breath_light.set_status(TimerStatus.NORMAL)
            self.breath_light.start(self.parent, self._update_breath_display)
    
    def _stop_breath_light(self) -> None:
        """停止呼吸灯效果"""
        if self.breath_light:
            self.breath_light.stop(self.parent)
    
    def _update_breath_display(self, brightness: float, status: TimerStatus) -> None:
        """
        更新呼吸灯显示
        
        Args:
            brightness: 亮度值（0-1）
            status: 倒计时状态
        """
        if not self.breath_light:
            return
        
        base_color = self.breath_light.get_current_color()
        adjusted_color = self.breath_light.apply_brightness_to_color(base_color, brightness)
        
        # 更新注册的显示元素
        for item in self._breath_display_items:
            try:
                if isinstance(item, tuple):
                    canvas, item_id = item
                    canvas.itemconfig(item_id, fill=adjusted_color)
                elif hasattr(item, 'config'):
                    # Tkinter 组件（Label 等）
                    item.config(fg=adjusted_color)
            except Exception as e:
                print(f"⚠️  更新呼吸灯显示错误：{e}")
    
    def _update_breath_status(self, remaining_time: float) -> None:
        """
        根据剩余时间更新呼吸灯状态
        
        Args:
            remaining_time: 剩余时间（秒）
        """
        if not self.breath_light:
            return
        
        # 最后 10 秒进入警告状态
        if remaining_time <= 10 and remaining_time > 0:
            self.breath_light.set_status(TimerStatus.WARNING)
        elif remaining_time <= 0:
            self.breath_light.set_status(TimerStatus.COMPLETED)
        else:
            self.breath_light.set_status(TimerStatus.NORMAL)
    
    # ========== 呼吸灯效果方法结束 ==========
    
    def get_timer(self) -> Timer:
        """获取计时器实例"""
        return self.timer


def create_timer_window(theme_colors: dict = None):
    """
    创建独立的倒计时窗口
    
    Args:
        theme_colors: 主题颜色配置
        
    Returns:
        主窗口实例
    """
    if theme_colors is None:
        theme_colors = {
            'background': '#1a1a2e',
            'face': '#16213e',
            'accent': '#0f3460',
            'hand': '#e94560',
            'text': '#ffffff'
        }
    
    root = tk.Tk()
    root.title("🕐 ClawClock - 倒计时")
    root.geometry("600x700")
    root.configure(bg=theme_colors['background'])
    
    widget = TimerWidget(root, theme_colors)
    widget.main_frame.pack(fill=tk.BOTH, expand=True)
    
    return root


if __name__ == "__main__":
    # 测试运行
    root = create_timer_window()
    root.mainloop()
