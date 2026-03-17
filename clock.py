#!/usr/bin/env python3
"""
ClawClock - 图形化时钟应用
========================

一个支持模拟和数字时间显示的 Linux 桌面时钟应用。

功能特性:
    - 模拟时钟和数字时钟双模式
    - 多时区支持
    - 现代深色主题 UI
    - 实时更新（50ms 刷新率）

使用方法:
    python3 clock.py

依赖:
    - Python 3.8+
    - tkinter

作者：ClawClock Development Team
许可证：MIT
版本：1.0.0
"""

import tkinter as tk
from tkinter import ttk
import time
import datetime
import math
import os
import sys
import json

class ClockApp:
    """
    时钟应用主类
    
    Attributes:
        root: Tkinter 主窗口
        timezone: 当前时区设置
        bg_color: 背景颜色
        face_color: 表盘颜色
        hand_color: 指针颜色
        text_color: 文字颜色
    """
    
    def load_config(self):
        """
        加载配置文件
        
        Returns:
            dict: 配置字典，如果配置文件不存在则返回默认配置
        """
        config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
        default_config = {
            "timezone": "Asia/Shanghai",
            "display_mode": "analog",
            "window": {
                "width": 600,
                "height": 500,
                "resizable": False
            },
            "theme": {
                "name": "dark",
                "colors": {
                    "background": "#1a1a2e",
                    "face": "#16213e",
                    "hand": "#e94560",
                    "text": "#ffffff",
                    "accent": "#0f3460",
                    "segment_on": "#ff3333",
                    "segment_off": "#331111"
                }
            }
        }
        
        try:
            if os.path.exists(config_file):
                with open(config_file, "r", encoding="utf-8") as f:
                    config = json.load(f)
                # 合并配置，确保所有键都存在
                return self.merge_config(default_config, config)
            else:
                # 配置文件不存在，创建默认配置
                self.save_config(default_config, config_file)
                return default_config
        except Exception as e:
            print(f"⚠️  加载配置文件失败：{e}")
            print("   使用默认配置")
            return default_config
    
    def merge_config(self, default, custom):
        """递归合并配置字典"""
        result = default.copy()
        for key, value in custom.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self.merge_config(result[key], value)
            else:
                result[key] = value
        return result
    
    def save_config(self, config, config_file=None):
        """
        保存配置文件
        
        Args:
            config: 配置字典
            config_file: 配置文件路径，默认为 config.json
        """
        if config_file is None:
            config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
        
        try:
            with open(config_file, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"⚠️  保存配置文件失败：{e}")
            return False
    
    def __init__(self, root):
        """初始化时钟应用"""
        self.root = root
        self.root.title("ClawClock - 图形时钟")
        
        # 加载配置文件
        self.config = self.load_config()
        
        # 应用窗口配置
        width = self.config.get("window", {}).get("width", 600)
        height = self.config.get("window", {}).get("height", 500)
        resizable = self.config.get("window", {}).get("resizable", False)
        self.root.geometry(f"{width}x{height}")
        self.root.resizable(resizable, resizable)
        
        # 设置窗口图标（如果有的话）
        try:
            self.root.iconname("ClawClock")
        except:
            pass
        
        # 默认时区（从配置加载）
        self.timezone = self.config.get("timezone", "Asia/Shanghai")
        
        # 时区配置：东西各 12 时区，每区指定代表城市
        self.timezones = [
            # 西区 (UTC-12 到 UTC-1)
            ("UTC-12", "Pacific/Kwajalein", "国际日期变更线西"),
            ("UTC-11", "Pacific/Pago_Pago", "帕果帕果"),
            ("UTC-10", "Pacific/Honolulu", "檀香山"),
            ("UTC-9", "America/Anchorage", "安克雷奇"),
            ("UTC-8", "America/Los_Angeles", "洛杉矶"),
            ("UTC-7", "America/Denver", "丹佛"),
            ("UTC-6", "America/Chicago", "芝加哥"),
            ("UTC-5", "America/New_York", "纽约"),
            ("UTC-4", "America/Halifax", "哈利法克斯"),
            ("UTC-3", "America/Sao_Paulo", "圣保罗"),
            ("UTC-2", "Atlantic/South_Georgia", "南乔治亚"),
            ("UTC-1", "Atlantic/Azores", "亚速尔群岛"),
            # 零时区
            ("UTC+0", "UTC", "协调世界时"),
            # 东区 (UTC+1 到 UTC+12)
            ("UTC+1", "Europe/London", "伦敦"),
            ("UTC+2", "Europe/Paris", "巴黎"),
            ("UTC+3", "Europe/Moscow", "莫斯科"),
            ("UTC+4", "Asia/Dubai", "迪拜"),
            ("UTC+5", "Asia/Karachi", "卡拉奇"),
            ("UTC+6", "Asia/Dhaka", "达卡"),
            ("UTC+7", "Asia/Bangkok", "曼谷"),
            ("UTC+8", "Asia/Shanghai", "上海"),
            ("UTC+9", "Asia/Tokyo", "东京"),
            ("UTC+10", "Australia/Sydney", "悉尼"),
            ("UTC+11", "Pacific/Noumea", "努美阿"),
            ("UTC+12", "Pacific/Auckland", "奥克兰"),
        ]
        
        # 从配置加载颜色
        theme_config = self.config.get("theme", {}).get("colors", {})
        self.bg_color = theme_config.get("background", "#1a1a2e")
        self.face_color = theme_config.get("face", "#16213e")
        self.hand_color = theme_config.get("hand", "#e94560")
        self.text_color = theme_config.get("text", "#ffffff")
        self.accent_color = theme_config.get("accent", "#0f3460")
        # 7 段数码管颜色
        self.seg_color_on = theme_config.get("segment_on", "#ff3333")
        self.seg_color_off = theme_config.get("segment_off", "#331111")
        
        # 显示模式（从配置加载）
        self.display_mode = self.config.get("display_mode", "analog")
        
        # Setup UI
        self.setup_ui()
        
        # Start clock update
        self.update_clock()
        
    def setup_ui(self):
        # Main frame
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Timezone selector - 东西各 12 时区
        tz_frame = tk.Frame(main_frame, bg=self.bg_color)
        tz_frame.pack(pady=(0, 10))
        
        tk.Label(tz_frame, text="时区:", bg=self.bg_color, fg=self.text_color, font=("Arial", 10)).pack(side=tk.LEFT)
        
        # 格式化时区选项显示
        tz_values = [f"{tz[0]} {tz[2]} ({tz[1]})" for tz in self.timezones]
        self.tz_combo = ttk.Combobox(tz_frame, values=tz_values, width=28, state="readonly")
        # 设置默认时区（从配置加载）
        default_tz_display = f"UTC+8 上海 (Asia/Shanghai)"
        for tz_val in tz_values:
            if self.timezone in tz_val:
                default_tz_display = tz_val
                break
        self.tz_combo.set(default_tz_display)
        self.tz_combo.pack(side=tk.LEFT, padx=(5, 0))
        self.tz_combo.bind("<<ComboboxSelected>>", self.on_timezone_change)
        
        # Mode toggle - 只保留 Analog 和 Digital（从配置加载）
        self.mode_var = tk.StringVar(value=self.display_mode)
        mode_frame = tk.Frame(main_frame, bg=self.bg_color)
        mode_frame.pack(pady=(0, 10))
        
        tk.Radiobutton(mode_frame, text="Analog", variable=self.mode_var, value="analog", 
                       bg=self.bg_color, fg=self.text_color, selectcolor=self.accent_color,
                       command=self.update_mode).pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(mode_frame, text="Digital", variable=self.mode_var, value="digital", 
                       bg=self.bg_color, fg=self.text_color, selectcolor=self.accent_color,
                       command=self.update_mode).pack(side=tk.LEFT, padx=5)
        
        # Canvas for analog clock - 居中显示
        self.canvas = tk.Canvas(main_frame, width=300, height=300, bg=self.face_color, highlightthickness=0)
        self.canvas.pack(pady=10)  # 居中显示
        
        # Digital time display - 7 段数码管风格（初始隐藏）
        self.digital_frame = tk.Frame(main_frame, bg=self.bg_color)
        # 不立即 pack，由 update_mode 控制显示
        
        # 7 段数码管画布 - 计算所需宽度
        # 6 个数字 * 35px + 5 个间距 * 10px + 2 个冒号区 * 25px = 210 + 50 + 50 = 310px
        # 额外增加 20px 边距确保不裁剪
        canvas_width = 330
        canvas_height = 80
        self.seg_canvas = tk.Canvas(self.digital_frame, width=canvas_width, height=canvas_height, 
                                     bg=self.bg_color, highlightthickness=0)
        self.seg_canvas.pack(expand=True)
        
        self.date_label = tk.Label(self.digital_frame, text="", font=("Arial", 14), 
                                    bg=self.bg_color, fg=self.text_color)
        self.date_label.pack(pady=10)
        
        # 7 段数码管段定义 (a,b,c,d,e,f,g) - 单个数字的段坐标
        # 每个数字宽 35px, 高 60px
        # 布局：数字 (35) + 间距 (10) + 数字 (35) + 冒号区 (25) + 数字 (35) + 间距 (10) + 数字 (35) + 冒号区 (25) + 数字 (35) + 间距 (10) + 数字 (35)
        self.seg_width = 35
        self.seg_height = 60
        self.seg_thickness = 5
        self.digit_spacing = 10  # 数字之间的间距
        self.colon_space = 25    # 冒号占用的空间（包括间距）
        
        # Draw clock face
        self.draw_clock_face()
        
    def draw_clock_face(self):
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
    
    def draw_segment(self, x1, y1, x2, y2, active):
        """绘制单个段"""
        color = self.seg_color_on if active else self.seg_color_off
        # 绘制梯形段，模拟真实数码管
        thickness = self.seg_thickness
        self.seg_canvas.create_line(x1, y1, x2, y2, fill=color, width=thickness, capstyle=tk.ROUND)
    
    def draw_digit(self, digit, x_offset):
        """绘制 7 段数码管数字"""
        # 数字对应的段 (a,b,c,d,e,f,g)
        digit_segs = {
            0: [1, 1, 1, 1, 1, 1, 0],
            1: [0, 1, 1, 0, 0, 0, 0],
            2: [1, 1, 0, 1, 1, 0, 1],
            3: [1, 1, 1, 1, 0, 0, 1],
            4: [0, 1, 1, 0, 0, 1, 1],
            5: [1, 0, 1, 1, 0, 1, 1],
            6: [1, 0, 1, 1, 1, 1, 1],
            7: [1, 1, 1, 0, 0, 0, 0],
            8: [1, 1, 1, 1, 1, 1, 1],
            9: [1, 1, 1, 1, 0, 1, 1],
        }
        
        segs = digit_segs.get(digit, [0, 0, 0, 0, 0, 0, 0])
        
        # 段坐标定义（相对于数字左上角）
        w = self.seg_width
        h = self.seg_height
        t = self.seg_thickness
        margin = 3  # 数字边缘留白
        
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
    
    def draw_colon(self, x_offset):
        """绘制冒号分隔符"""
        r = 3
        h = self.seg_height
        cx = x_offset
        cy1 = h // 3      # 上圆点垂直位置
        cy2 = h * 2 // 3  # 下圆点垂直位置
        self.seg_canvas.create_oval(cx-r, cy1-r, cx+r, cy1+r, fill=self.seg_color_on)
        self.seg_canvas.create_oval(cx-r, cy2-r, cx+r, cy2+r, fill=self.seg_color_on)
    
    def draw_seven_segment_time(self, time_str):
        """绘制 7 段数码管时间显示"""
        self.seg_canvas.delete("all")
        
        # 解析时间 HH:MM:SS
        parts = time_str.split(":")
        if len(parts) >= 3:
            digits = [int(parts[0][0]), int(parts[0][1]),  # 小时
                      int(parts[1][0]), int(parts[1][1]),  # 分钟
                      int(parts[2][0]), int(parts[2][1])]  # 秒
            
            # 计算每位数字的 x 偏移量
            # 布局：[边距] H [间距] H [冒号区] M [间距] M [冒号区] S [间距] S [边距]
            #            0         1          2         3          4         5
            w = self.seg_width      # 数字宽度 (35px)
            s = self.digit_spacing  # 数字间距 (10px)
            c = self.colon_space    # 冒号区空间 (25px)
            margin = 15             # 左右边距
            
            # 逐步计算每个位置的起始 x 坐标
            x0 = margin                                    # 小时十位
            x1 = x0 + w + s                                # 小时个位
            x2 = x1 + w + s + c                            # 分钟十位（跳过冒号区）
            x3 = x2 + w + s                                # 分钟个位
            x4 = x3 + w + s + c                            # 秒钟十位（跳过冒号区）
            x5 = x4 + w + s                                # 秒钟个位
            
            offsets = [x0, x1, x2, x3, x4, x5]
            
            for i, digit in enumerate(digits):
                self.draw_digit(digit, offsets[i])
            
            # 绘制冒号（在冒号区正中央）
            # 冒号区起始位置：x1 + w 和 x3 + w
            # 冒号区中心：起始位置 + 冒号区宽度 / 2
            colon1_x = x1 + w + c // 2    # 时分之间的冒号
            colon2_x = x3 + w + c // 2    # 分秒之间的冒号
            self.draw_colon(colon1_x)
            self.draw_colon(colon2_x)
        
    def update_clock(self):
        # Get current time in selected timezone
        try:
            tz = datetime.timezone(datetime.timedelta(hours=0))
            if self.timezone != "UTC":
                import zoneinfo
                tz = zoneinfo.ZoneInfo(self.timezone)
            
            now = datetime.datetime.now(tz)
        except:
            now = datetime.datetime.now()
        
        hour = now.hour
        minute = now.minute
        second = now.second
        microsecond = now.microsecond
        
        # Update analog clock
        if self.mode_var.get() == "analog":
            self.draw_analog_clock(hour, minute, second)
        
        # Update digital clock - 7 段数码管显示
        if self.mode_var.get() == "digital":
            time_str = now.strftime("%H:%M:%S")
            self.draw_seven_segment_time(time_str)
            date_str = now.strftime("%Y-%m-%d %A")
            tz_info = next((tz for tz in self.timezones if tz[1] == self.timezone), None)
            tz_display = f"{tz_info[0]} {tz_info[2]}" if tz_info else self.timezone
            self.date_label.config(text=f"{date_str}\n{tz_display}")
        
        # Schedule next update
        self.root.after(50, self.update_clock)
        
    def draw_analog_clock(self, hour, minute, second):
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
        
    def on_timezone_change(self, event):
        # 从显示格式中提取时区 ID
        selected = self.tz_combo.get()
        # 格式："UTC+X 城市名 (timezone.id)"
        try:
            tz_id = selected.split("(")[1].split(")")[0]
            self.timezone = tz_id
        except:
            self.timezone = selected
        
    def update_mode(self):
        mode = self.mode_var.get()
        
        if mode == "analog":
            self.canvas.pack(pady=10)  # 居中显示
            self.digital_frame.pack_forget()
        elif mode == "digital":
            self.canvas.pack_forget()
            self.digital_frame.pack(pady=10)  # 居中显示

def main():
    """主函数 - 启动时钟应用"""
    print("🕐 启动 ClawClock...")
    print(f"   Python 版本：{sys.version.split()[0]}")
    print(f"   Tkinter 版本：{tk.TkVersion}")
    print()
    
    root = tk.Tk()
    
    # 设置样式
    style = ttk.Style()
    style.theme_use('clam')  # 使用现代主题
    
    app = ClockApp(root)
    
    print("✅ ClawClock 已启动")
    print("   提示：关闭窗口退出应用")
    print()
    
    root.mainloop()
    
    print("👋 ClawClock 已退出")


if __name__ == "__main__":
    main()