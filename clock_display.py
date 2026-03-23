#!/usr/bin/env python3
"""
ClawClock - 显示渲染模块
========================

负责时钟的显示渲染：
- 模拟时钟绘制
- 数字时钟绘制（7 段数码管）
- 模式切换
- 时区/主题事件处理
"""

import math
import datetime
from typing import Dict, List, Optional, Tuple, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from clock import ClockApp

import tkinter as tk


class ClockDisplayMixin:
    """时钟显示渲染混入类"""

    # 段宽度（像素）
    seg_width: int = 80
    # 段高度（像素）
    seg_height: int = 130
    # 段厚度（像素）
    seg_thickness: int = 8
    # 数字间距（像素）
    digit_spacing: int = 15

    def draw_clock_face(self) -> None:
        """绘制时钟表盘"""
        self.canvas.delete("all")
        cx, cy, r = 150, 150, 130

        # Clock face circle
        self.canvas.create_oval(cx-r, cy-r, cx+r, cy+r, outline=self.hand_color, width=3)

        # Hour marks
        for i in range(12):
            angle = math.radians(i * 30 - 90)
            x1 = cx + (r - 15) * math.cos(angle)
            y1 = cy + (r - 15) * math.sin(angle)
            x2 = cx + (r - 5) * math.cos(angle)
            y2 = cy + (r - 5) * math.sin(angle)
            self.canvas.create_line(x1, y1, x2, y2, fill=self.text_color, width=2)

        # Minute marks
        for i in range(60):
            if i % 5 != 0:
                angle = math.radians(i * 6 - 90)
                x1 = cx + (r - 10) * math.cos(angle)
                y1 = cy + (r - 10) * math.sin(angle)
                x2 = cx + (r - 5) * math.cos(angle)
                y2 = cy + (r - 5) * math.sin(angle)
                self.canvas.create_line(x1, y1, x2, y2, fill=self.text_color, width=1)

        # Center dot
        self.canvas.create_oval(cx-5, cy-5, cx+5, cy+5, fill=self.hand_color)

    def draw_segment(self, x1: float, y1: float, x2: float, y2: float, active: bool) -> None:
        """绘制单个段（带轻微发光效果）"""
        color = self.seg_color_on if active else self.seg_color_off
        thickness = self.seg_thickness + 2 if active else self.seg_thickness

        self.seg_canvas.create_line(x1, y1, x2, y2, fill=color, width=thickness,
                                    capstyle=tk.ROUND, joinstyle=tk.ROUND)

    def draw_digit(self, digit: int, x_offset: float) -> None:
        """绘制 7 段数码管数字"""
        # 数字对应的段 (a,b,c,d,e,f,g)
        digit_segs: Dict[int, List[bool]] = {
            0: [True, True, True, True, True, True, False],
            1: [False, True, True, False, False, False, False],
            2: [True, True, False, True, True, False, True],
            3: [True, True, True, True, False, False, True],
            4: [False, True, True, False, False, True, True],
            5: [True, False, True, True, False, True, True],
            6: [True, False, True, True, True, True, True],
            7: [True, True, True, False, False, False, False],
            8: [True, True, True, True, True, True, True],
            9: [True, True, True, True, False, True, True],
        }

        segs = digit_segs.get(digit, [False, False, False, False, False, False, False])

        # 段坐标定义（相对于数字左上角）
        w = self.seg_width
        h = self.seg_height
        t = self.seg_thickness
        margin = 5

        # a: 上横
        self.draw_segment(x_offset + margin + t, margin, x_offset + w - margin - t, margin, segs[0])
        # b: 右上竖
        self.draw_segment(x_offset + w - margin, margin + t, x_offset + w - margin, h // 2 - t, segs[1])
        # c: 右下竖
        self.draw_segment(x_offset + w - margin, h // 2 + t, x_offset + w - margin, h - margin - t, segs[2])
        # d: 下横
        self.draw_segment(x_offset + margin + t, h - margin, x_offset + w - margin - t, h - margin, segs[3])
        # e: 左下竖
        self.draw_segment(x_offset + margin, h // 2 + t, x_offset + margin, h - margin - t, segs[4])
        # f: 左上竖
        self.draw_segment(x_offset + margin, margin + t, x_offset + margin, h // 2 - t, segs[5])
        # g: 中横
        self.draw_segment(x_offset + margin + t, h // 2, x_offset + w - margin - t, h // 2, segs[6])

    def draw_colon(self, x_offset: float) -> None:
        """绘制冒号分隔符"""
        r = self.seg_thickness // 2
        h = self.seg_height
        cx = x_offset
        cy1 = h // 3
        cy2 = h * 2 // 3
        self.seg_canvas.create_oval(cx-r, cy1-r, cx+r, cy1+r, fill=self.seg_color_on)
        self.seg_canvas.create_oval(cx-r, cy2-r, cx+r, cy2+r, fill=self.seg_color_on)

    def draw_seven_segment_time(self, time_str: str) -> None:
        """绘制 7 段数码管时间显示"""
        self.seg_canvas.delete("all")

        parts = time_str.split(":")
        if len(parts) >= 3:
            digits: List[int] = [int(parts[0][0]), int(parts[0][1]),
                      int(parts[1][0]), int(parts[1][1]),
                      int(parts[2][0]), int(parts[2][1])]

            w = self.seg_width
            s = self.digit_spacing
            c = w
            margin = 15

            x0: float = margin
            x1: float = x0 + w + s
            x2: float = x1 + w + s + c
            x3: float = x2 + w + s
            x4: float = x3 + w + s + c
            x5: float = x4 + w + s

            offsets: List[float] = [x0, x1, x2, x3, x4, x5]

            for i, digit in enumerate(digits):
                self.draw_digit(digit, offsets[i])

            colon1_x = x1 + w + s + c // 2
            colon2_x = x3 + w + s + c // 2
            self.draw_colon(colon1_x)
            self.draw_colon(colon2_x)

    def update_clock(self) -> None:
        """更新时钟显示（带性能监控）"""
        try:
            tz: datetime.timezone | datetime.tzinfo = datetime.timezone(datetime.timedelta(hours=0))
            if self.timezone != "UTC":
                import zoneinfo
                tz = zoneinfo.ZoneInfo(self.timezone)
            now: datetime.datetime = datetime.datetime.now(tz)
        except Exception:
            now = datetime.datetime.now()

        hour: int = now.hour
        minute: int = now.minute
        second: int = now.second
        microsecond: int = now.microsecond

        # 性能监控：帧开始
        if hasattr(self, 'perf_monitor') and self.perf_monitor:
            self.perf_monitor.start_frame()

        # Update analog clock
        if self.mode_var.get() == "analog":
            self.draw_analog_clock(hour, minute, second)

        # Update digital clock
        if self.mode_var.get() == "digital":
            time_str: str = now.strftime("%H:%M:%S")
            self.draw_seven_segment_time(time_str)
            date_str: str = now.strftime("%Y-%m-%d %A")
            tz_info: Optional[Tuple[str, str, str]] = next((tz for tz in self.timezones if tz[1] == self.timezone), None)
            tz_display: str = f"{tz_info[0]} {tz_info[2]}" if tz_info else self.timezone
            self.date_label.config(text=f"{date_str}\n{tz_display}")

        # 性能监控：帧结束
        if hasattr(self, 'perf_monitor') and self.perf_monitor:
            self.perf_monitor.end_frame()

        # Schedule next update
        self.root.after(50, self.update_clock)

    def draw_analog_clock(self, hour: int, minute: int, second: int) -> None:
        """绘制模拟时钟"""
        cx, cy, r = 150, 150, 130

        # Clear previous hands
        self.canvas.delete("hands")

        # Second hand
        sec_angle = math.radians(second * 6 - 90)
        sec_len = r - 20
        x2 = cx + sec_len * math.cos(sec_angle)
        y2 = cy + sec_len * math.sin(sec_angle)
        self.canvas.create_line(cx, cy, x2, y2, fill="#ff6b6b", width=2, tags="hands")

        # Minute hand
        min_angle = math.radians(minute * 6 - 90)
        min_len = r - 30
        x2 = cx + min_len * math.cos(min_angle)
        y2 = cy + min_len * math.sin(min_angle)
        self.canvas.create_line(cx, cy, x2, y2, fill=self.text_color, width=4, tags="hands")

        # Hour hand
        hour_angle = math.radians((hour % 12 + minute / 60) * 30 - 90)
        hour_len = r - 60
        x2 = cx + hour_len * math.cos(hour_angle)
        y2 = cy + hour_len * math.sin(hour_angle)
        self.canvas.create_line(cx, cy, x2, y2, fill=self.hand_color, width=6, tags="hands")

    def on_timezone_change(self, event: tk.Event) -> None:
        """时区切换事件处理"""
        selected = self.tz_combo.get()
        try:
            tz_id = selected.split("(")[1].split(")")[0]
            self.timezone = tz_id
            self.config["timezone"] = tz_id
            self.save_config()
        except Exception:
            self.timezone = selected
            self.config["timezone"] = selected
            self.save_config()

    def on_theme_change(self, event: tk.Event) -> None:
        """主题切换事件处理"""
        selected = self.theme_combo.get()
        theme_name = self.theme_display_to_name.get(selected, "dark")
        self.apply_theme(theme_name)

    def update_mode(self) -> None:
        """切换显示模式"""
        mode = self.mode_var.get()

        if mode == "analog":
            self.canvas.pack(pady=10)
            self.digital_frame.pack_forget()
            self.stopwatch_frame.pack_forget()
            self.timer_frame.pack_forget()
        elif mode == "digital":
            self.canvas.pack_forget()
            self.digital_frame.pack(pady=10)
            self.stopwatch_frame.pack_forget()
            self.timer_frame.pack_forget()
        elif mode == "stopwatch":
            self.canvas.pack_forget()
            self.digital_frame.pack_forget()
            self.stopwatch_frame.pack(pady=10)
            self.timer_frame.pack_forget()
            self._update_stopwatch_display()
        elif mode == "timer":
            self.canvas.pack_forget()
            self.digital_frame.pack_forget()
            self.stopwatch_frame.pack_forget()
            self.timer_frame.pack(pady=10)
            self.update_timer_display()

        # 更新配置并保存
        self.config["display_mode"] = mode
        self.save_config()

    def _refresh_ui(self) -> None:
        """刷新 UI（供 ClockCore 调用）"""
        if hasattr(self, 'canvas'):
            self.draw_clock_face()
        if hasattr(self, 'seg_canvas'):
            time_str = datetime.datetime.now().strftime("%H:%M:%S")
            self.draw_seven_segment_time(time_str)
