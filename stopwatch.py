#!/usr/bin/env python3
"""
秒表模块 - ClawClock 秒表功能
============================

功能:
    - 精确计时（毫秒级）
    - 开始/暂停/重置控制
    - 圈速记录
    - 主题支持

作者：ClawClock Development Team
版本：1.2.0
"""

import tkinter as tk
from tkinter import ttk
import time
import datetime
from typing import List, Optional, Callable
from dataclasses import dataclass, field


@dataclass
class LapRecord:
    """圈速记录数据类"""
    lap_number: int
    total_time: float  # 总时间（秒）
    lap_time: float    # 单圈时间（秒）
    timestamp: float   # 时间戳


class Stopwatch:
    """
    秒表类
    
    提供精确的计时功能，支持开始、暂停、重置和圈速记录
    
    Attributes:
        start_time: 开始时间戳
        elapsed_time: 累计经过的时间（秒）
        is_running: 是否正在运行
        laps: 圈速记录列表
    """
    
    def __init__(self):
        """初始化秒表"""
        self.start_time: Optional[float] = None
        self.elapsed_time: float = 0.0
        self.is_running: bool = False
        self.laps: List[LapRecord] = []
        self._lap_counter: int = 0
    
    def start(self) -> None:
        """开始计时"""
        if not self.is_running:
            self.start_time = time.time() - self.elapsed_time
            self.is_running = True
    
    def stop(self) -> None:
        """暂停计时"""
        if self.is_running:
            self.elapsed_time = time.time() - self.start_time
            self.is_running = False
    
    def reset(self) -> None:
        """重置秒表"""
        self.start_time = None
        self.elapsed_time = 0.0
        self.is_running = False
        self.laps = []
        self._lap_counter = 0
    
    def get_time(self) -> float:
        """
        获取当前时间
        
        Returns:
            当前经过的时间（秒）
        """
        if self.is_running and self.start_time:
            return time.time() - self.start_time
        return self.elapsed_time
    
    def record_lap(self) -> Optional[LapRecord]:
        """
        记录当前圈速
        
        Returns:
            圈速记录，如果秒表未运行则返回 None
        """
        if not self.is_running:
            return None
        
        current_time = self.get_time()
        self._lap_counter += 1
        
        # 计算单圈时间
        if self.laps:
            lap_time = current_time - self.laps[-1].total_time
        else:
            lap_time = current_time
        
        lap = LapRecord(
            lap_number=self._lap_counter,
            total_time=current_time,
            lap_time=lap_time,
            timestamp=time.time()
        )
        self.laps.append(lap)
        return lap
    
    def format_time(self, seconds: Optional[float] = None, show_ms: bool = True) -> str:
        """
        格式化时间为显示字符串
        
        Args:
            seconds: 要格式化的时间（秒），None 则使用当前时间
            show_ms: 是否显示毫秒
            
        Returns:
            格式化后的时间字符串 (HH:MM:SS 或 HH:MM:SS.ms)
        """
        if seconds is None:
            seconds = self.get_time()
        
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        ms = int((seconds % 1) * 100)
        
        if hours > 0:
            if show_ms:
                return f"{hours:02d}:{minutes:02d}:{secs:02d}.{ms:02d}"
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            if show_ms:
                return f"{minutes:02d}:{secs:02d}.{ms:02d}"
            return f"{minutes:02d}:{secs:02d}"
    
    def format_lap_time(self, lap_time: float) -> str:
        """
        格式化圈速时间
        
        Args:
            lap_time: 圈速时间（秒）
            
        Returns:
            格式化后的圈速字符串
        """
        return self.format_time(lap_time, show_ms=True)


class StopwatchWidget:
    """
    秒表 UI 组件
    
    提供秒表的图形界面，包括时间显示、控制按钮和圈速列表
    
    Attributes:
        parent: 父容器
        stopwatch: 秒表实例
        update_callback: 更新回调函数
    """
    
    def __init__(self, parent: tk.Widget, theme_colors: dict):
        """
        初始化秒表组件
        
        Args:
            parent: 父容器
            theme_colors: 主题颜色配置
        """
        self.parent = parent
        self.theme = theme_colors
        self.stopwatch = Stopwatch()
        self.update_callback: Optional[Callable] = None
        self._update_job: Optional[str] = None
        
        self._setup_ui()
    
    def _setup_ui(self) -> None:
        """设置 UI 组件"""
        # 主框架
        self.main_frame = tk.Frame(self.parent, bg=self.theme['background'])
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 时间显示区域
        self._create_display_frame()
        
        # 控制按钮区域
        self._create_control_frame()
        
        # 圈速记录区域
        self._create_lap_frame()
    
    def _create_display_frame(self) -> None:
        """创建时间显示区域"""
        display_frame = tk.Frame(self.main_frame, bg=self.theme['background'])
        display_frame.pack(pady=30)
        
        # 时间标签 - 使用大字体显示
        self.time_label = tk.Label(
            display_frame,
            text="00:00.00",
            font=("Courier New", 72, "bold"),
            fg=self.theme['text'],
            bg=self.theme['background']
        )
        self.time_label.pack()
    
    def _create_control_frame(self) -> None:
        """创建控制按钮区域"""
        control_frame = tk.Frame(self.main_frame, bg=self.theme['background'])
        control_frame.pack(pady=20)
        
        # 按钮样式
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
        
        # 圈速按钮
        self.lap_btn = tk.Button(
            control_frame,
            text="🏁 圈速",
            font=("Arial", 14),
            width=btn_width,
            bg=self.theme['face'],
            fg=self.theme['text'],
            activebackground=self.theme['accent'],
            activeforeground=self.theme['text'],
            command=self._record_lap
        )
        self.lap_btn.pack(side=tk.LEFT, padx=btn_padx)
    
    def _create_lap_frame(self) -> None:
        """创建圈速记录区域"""
        lap_frame = tk.Frame(self.main_frame, bg=self.theme['background'])
        lap_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # 标题
        tk.Label(
            lap_frame,
            text="圈速记录",
            font=("Arial", 12, "bold"),
            fg=self.theme['text'],
            bg=self.theme['background']
        ).pack(pady=5)
        
        # 圈速列表框架
        list_container = tk.Frame(lap_frame, bg=self.theme['background'])
        list_container.pack(fill=tk.BOTH, expand=True)
        
        # 创建带滚动条的列表框
        scrollbar = tk.Scrollbar(list_container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.lap_listbox = tk.Listbox(
            list_container,
            font=("Courier New", 11),
            fg=self.theme['text'],
            bg=self.theme['face'],
            selectbackground=self.theme['accent'],
            selectforeground=self.theme['text'],
            yscrollcommand=scrollbar.set
        )
        self.lap_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.lap_listbox.yview)
        
        # 列标题
        self.lap_listbox.insert(tk.END, f"{'圈数':<6} {'单圈时间':<12} {'总时间':<12}")
        self.lap_listbox.insert(tk.END, "─" * 32)
    
    def _toggle_start_stop(self) -> None:
        """切换开始/暂停状态"""
        if self.stopwatch.is_running:
            self.stopwatch.stop()
            self.start_stop_btn.config(text="▶ 开始")
            self.lap_btn.config(state=tk.DISABLED)
        else:
            self.stopwatch.start()
            self.start_stop_btn.config(text="⏸ 暂停")
            self.lap_btn.config(state=tk.NORMAL)
            self._start_update_loop()
    
    def _reset(self) -> None:
        """重置秒表"""
        self.stopwatch.reset()
        self.time_label.config(text="00:00.00")
        self.start_stop_btn.config(text="▶ 开始")
        self.lap_btn.config(state=tk.DISABLED)
        
        # 清空圈速列表
        self.lap_listbox.delete(0, tk.END)
        self.lap_listbox.insert(tk.END, f"{'圈数':<6} {'单圈时间':<12} {'总时间':<12}")
        self.lap_listbox.insert(tk.END, "─" * 32)
        
        # 停止更新循环
        if self._update_job:
            self.parent.after_cancel(self._update_job)
            self._update_job = None
    
    def _record_lap(self) -> None:
        """记录圈速"""
        lap = self.stopwatch.record_lap()
        if lap:
            lap_str = f"#{lap.lap_number:<5} {self.stopwatch.format_lap_time(lap.lap_time):<12} {self.stopwatch.format_lap_time(lap.total_time):<12}"
            self.lap_listbox.insert(tk.END, lap_str)
            # 滚动到最新记录
            self.lap_listbox.yview(tk.END)
    
    def _start_update_loop(self) -> None:
        """启动时间更新循环"""
        self._update_display()
    
    def _update_display(self) -> None:
        """更新时间显示"""
        if self.stopwatch.is_running:
            current_time = self.stopwatch.format_time()
            self.time_label.config(text=current_time)
            # 每 10ms 更新一次（100Hz）
            self._update_job = self.parent.after(10, self._update_display)
    
    def get_stopwatch(self) -> Stopwatch:
        """获取秒表实例"""
        return self.stopwatch
