#!/usr/bin/env python3
"""
ClawClock 界面截图脚本
=====================
用于自动生成应用界面截图，支持多种界面和主题。
"""

import tkinter as tk
from tkinter import ttk
import time
import datetime
import math
import os
import sys
from PIL import Image, ImageGrab

# 添加项目路径
sys.path.insert(0, '/home/lenovo/AItest/clawclock')

# 尝试导入 ClawClock 模块
try:
    from clock import ClockApp
    print("✓ 成功导入 ClockApp")
except ImportError as e:
    print(f"⚠ 无法导入 ClockApp: {e}")
    ClockApp = None

try:
    from timer import TimerApp
    print("✓ 成功导入 TimerApp")
except ImportError as e:
    print(f"⚠ 无法导入 TimerApp: {e}")
    TimerApp = None

try:
    from stopwatch import Stopwatch
    print("✓ 成功导入 Stopwatch")
except ImportError as e:
    print(f"⚠ 无法导入 Stopwatch: {e}")
    Stopwatch = None


def capture_window(root, filename, padding=10):
    """截取窗口并保存为 PNG"""
    # 更新窗口确保完全渲染
    root.update_idletasks()
    
    # 获取窗口位置
    x = root.winfo_rootx()
    y = root.winfo_rooty()
    w = root.winfo_width()
    h = root.winfo_height()
    
    # 截取窗口区域
    screenshot = ImageGrab.grab(bbox=(x-padding, y-padding, 
                                       x+w+padding, y+h+padding))
    
    # 保存截图
    screenshot.save(filename, 'PNG', optimize=True)
    print(f"✓ 已保存截图：{filename}")
    return filename


def create_alarm_screenshot():
    """创建闹钟管理界面截图"""
    print("\n📸 创建闹钟管理界面截图...")
    
    root = tk.Tk()
    root.title("ClawClock - 闹钟管理")
    root.geometry("800x600")
    
    # 设置深色主题
    style = ttk.Style(root)
    style.theme_use('clam')
    
    # 主框架
    main_frame = ttk.Frame(root, padding="20")
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # 标题
    title_label = ttk.Label(main_frame, text="⏰ 闹钟管理", 
                           font=('Arial', 20, 'bold'))
    title_label.pack(pady=(0, 20))
    
    # 闹钟列表框架
    alarm_frame = ttk.LabelFrame(main_frame, text="已设置的闹钟", padding="15")
    alarm_frame.pack(fill=tk.BOTH, expand=True, pady=10)
    
    # 示例闹钟
    alarms = [
        ("07:00", "起床闹钟", "每天", True),
        ("09:00", "晨会提醒", "工作日", True),
        ("12:30", "午餐时间", "每天", False),
        ("23:00", "睡觉提醒", "每天", True),
    ]
    
    for time_str, label, repeat, enabled in alarms:
        alarm_row = ttk.Frame(alarm_frame)
        alarm_row.pack(fill=tk.X, pady=5)
        
        # 时间
        time_label = ttk.Label(alarm_row, text=time_str, 
                              font=('Arial', 16, 'bold'), width=10)
        time_label.pack(side=tk.LEFT, padx=(0, 15))
        
        # 标签
        label_label = ttk.Label(alarm_row, text=label, font=('Arial', 12))
        label_label.pack(side=tk.LEFT, padx=(0, 15))
        
        # 重复周期
        repeat_label = ttk.Label(alarm_row, text=repeat, 
                                font=('Arial', 10), foreground='gray')
        repeat_label.pack(side=tk.LEFT, padx=(0, 15))
        
        # 开关
        var = tk.BooleanVar(value=enabled)
        check = ttk.Checkbutton(alarm_row, variable=var)
        check.pack(side=tk.RIGHT)
    
    # 添加闹钟按钮
    add_btn = ttk.Button(main_frame, text="+ 添加新闹钟")
    add_btn.pack(pady=10)
    
    # 截图
    root.update_idletasks()
    root.after(500, lambda: capture_window(root, 
          '/home/lenovo/AItest/clawclock/screenshots/alarm-management.png'))
    root.after(600, root.destroy)
    root.mainloop()


def create_timer_screenshot():
    """创建倒计时自定义输入界面截图"""
    print("\n📸 创建倒计时自定义输入界面截图...")
    
    root = tk.Tk()
    root.title("ClawClock - 倒计时")
    root.geometry("700x550")
    
    # 主框架
    main_frame = ttk.Frame(root, padding="30")
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # 标题
    title_label = ttk.Label(main_frame, text="⏱️ 倒计时", 
                           font=('Arial', 20, 'bold'))
    title_label.pack(pady=(0, 20))
    
    # 时间显示
    time_frame = ttk.Frame(main_frame)
    time_frame.pack(pady=20)
    
    def create_time_input(frame, label_text):
        """创建时间输入组件"""
        col = ttk.Frame(frame)
        col.pack(side=tk.LEFT, padx=10)
        
        label = ttk.Label(col, text=label_text, font=('Arial', 12))
        label.pack()
        
        entry = ttk.Entry(col, font=('Arial', 24), width=4, justify='center')
        entry.pack(pady=5)
        entry.insert(0, "00")
        
        return entry
    
    hour_entry = create_time_input(time_frame, "小时")
    min_entry = create_time_input(time_frame, "分钟")
    sec_entry = create_time_input(time_frame, "秒")
    
    # 预设时间按钮
    preset_frame = ttk.LabelFrame(main_frame, text="预设时间", padding="15")
    preset_frame.pack(fill=tk.X, pady=20)
    
    presets = [
        ("🍅 番茄钟", "25:00"),
        ("☕ 短休息", "5:00"),
        ("🍽️ 长休息", "15:00"),
        ("🧘 冥想", "10:00"),
    ]
    
    for name, time_val in presets:
        btn = ttk.Button(preset_frame, text=name, width=15)
        btn.pack(side=tk.LEFT, padx=5, pady=5)
    
    # 控制按钮
    control_frame = ttk.Frame(main_frame)
    control_frame.pack(pady=20)
    
    start_btn = ttk.Button(control_frame, text="▶ 开始", width=15)
    start_btn.pack(side=tk.LEFT, padx=10)
    
    pause_btn = ttk.Button(control_frame, text="⏸ 暂停", width=15)
    pause_btn.pack(side=tk.LEFT, padx=10)
    
    reset_btn = ttk.Button(control_frame, text="↺ 重置", width=15)
    reset_btn.pack(side=tk.LEFT, padx=10)
    
    # 截图
    root.update_idletasks()
    root.after(500, lambda: capture_window(root, 
          '/home/lenovo/AItest/clawclock/screenshots/timer-custom.png'))
    root.after(600, root.destroy)
    root.mainloop()


def create_shortcuts_screenshot():
    """创建键盘快捷键提示界面截图"""
    print("\n📸 创建键盘快捷键提示界面截图...")
    
    root = tk.Tk()
    root.title("ClawClock - 快捷键")
    root.geometry("650x500")
    
    # 主框架
    main_frame = ttk.Frame(root, padding="30")
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # 标题
    title_label = ttk.Label(main_frame, text="⌨️ 键盘快捷键", 
                           font=('Arial', 20, 'bold'))
    title_label.pack(pady=(0, 20))
    
    # 快捷键列表
    shortcuts_frame = ttk.LabelFrame(main_frame, text="全局快捷键", padding="20")
    shortcuts_frame.pack(fill=tk.BOTH, expand=True, pady=10)
    
    shortcuts = [
        ("Ctrl + N", "新建闹钟"),
        ("Ctrl + T", "打开倒计时"),
        ("Ctrl + S", "打开秒表"),
        ("Ctrl + W", "关闭当前窗口"),
        ("F5", "刷新时间"),
        ("F11", "全屏模式"),
        ("Esc", "退出全屏"),
    ]
    
    for i, (keys, desc) in enumerate(shortcuts):
        row = ttk.Frame(shortcuts_frame)
        row.pack(fill=tk.X, pady=8)
        
        # 快捷键
        keys_label = ttk.Label(row, text=keys, 
                              font=('Consolas', 14, 'bold'), 
                              foreground='#00ff88', width=15, anchor='w')
        keys_label.pack(side=tk.LEFT, padx=(0, 20))
        
        # 描述
        desc_label = ttk.Label(row, text=desc, font=('Arial', 12))
        desc_label.pack(side=tk.LEFT)
    
    # 底部提示
    tip_label = ttk.Label(main_frame, 
                         text="💡 提示：可在设置中自定义快捷键",
                         font=('Arial', 10), foreground='gray')
    tip_label.pack(pady=(20, 0))
    
    # 截图
    root.update_idletasks()
    root.after(500, lambda: capture_window(root, 
          '/home/lenovo/AItest/clawclock/screenshots/keyboard-shortcuts.png'))
    root.after(600, root.destroy)
    root.mainloop()


def create_theme_preview(theme_name, bg_color, fg_color, accent_color):
    """创建主题预览图"""
    print(f"\n🎨 创建 {theme_name} 主题预览...")
    
    root = tk.Tk()
    root.title(f"ClawClock - {theme_name} Theme")
    root.geometry("800x600")
    root.configure(bg=bg_color)
    
    # 主框架
    main_frame = tk.Frame(root, bg=bg_color, padx=30, pady=30)
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # 标题
    title_label = tk.Label(main_frame, text="ClawClock", 
                          font=('Arial', 28, 'bold'),
                          bg=bg_color, fg=fg_color)
    title_label.pack(pady=(0, 10))
    
    subtitle = tk.Label(main_frame, text=f"{theme_name} Theme Preview",
                       font=('Arial', 14), bg=bg_color, fg=fg_color)
    subtitle.pack(pady=(0, 30))
    
    # 时钟显示示例
    clock_frame = tk.Frame(main_frame, bg=bg_color)
    clock_frame.pack(pady=20)
    
    time_label = tk.Label(clock_frame, text="14:30:45",
                         font=('Consolas', 48, 'bold'),
                         bg=bg_color, fg=accent_color)
    time_label.pack()
    
    date_label = tk.Label(clock_frame, text="2026-03-19 Thursday",
                         font=('Arial', 14),
                         bg=bg_color, fg=fg_color)
    date_label.pack(pady=(10, 0))
    
    # 功能按钮示例
    btn_frame = tk.Frame(main_frame, bg=bg_color)
    btn_frame.pack(pady=20)
    
    buttons = ["⏰ Alarm", "⏱️ Timer", "🕐 Stopwatch", "⚙️ Settings"]
    for btn_text in buttons:
        btn = tk.Button(btn_frame, text=btn_text,
                       font=('Arial', 12),
                       bg=accent_color, fg=bg_color,
                       activebackground=fg_color,
                       activeforeground=bg_color,
                       relief='flat', padx=20, pady=10)
        btn.pack(side=tk.LEFT, padx=10)
    
    # 截图
    root.update_idletasks()
    filename = f'/home/lenovo/AItest/clawclock/screenshots/themes/{theme_name.lower()}-theme.png'
    root.after(500, lambda: capture_window(root, filename))
    root.after(600, root.destroy)
    root.mainloop()


def create_stopwatch_lap_diagram():
    """创建秒表计圈功能示意图"""
    print("\n📊 创建秒表计圈功能示意图...")
    
    # 使用 PIL 创建示意图
    img = Image.new('RGB', (800, 600), color='#1a1a2e')
    draw = ImageDraw.Draw(img)
    
    # 标题
    draw.text((400, 40), "Stopwatch Lap Function", 
             fill='#00ff88', anchor='center',
             font_size=24)
    
    # 主计时器显示
    draw.rectangle([200, 80, 600, 180], outline='#00ff88', width=3)
    draw.text((400, 130), "12:34.56", 
             fill='#00ff88', anchor='center',
             font_size=48)
    
    # 按钮
    button_colors = ['#00ff88', '#ff6b6b', '#4ecdc4']
    button_labels = ['Start', 'Lap', 'Reset']
    
    for i, (label, color) in enumerate(zip(button_labels, button_colors)):
        x1, y1 = 200 + i*140, 220
        x2, y2 = x1 + 120, y2 + 60 if i > 0 else 280
        draw.rounded_rectangle([x1, 220, x1+120, 280], radius=10, fill=color)
        draw.text((x1+60, 250), label, fill='#1a1a2e', anchor='center',
                 font_size=16)
    
    # 圈速列表
    draw.text((100, 320), "Lap Times:", fill='#ffffff',
             font_size=18)
    
    lap_data = [
        ("Lap 1", "1:23.45", "+0:00.00"),
        ("Lap 2", "2:45.67", "+1:22.22"),
        ("Lap 3", "4:12.89", "+1:27.22"),
        ("Lap 4", "5:34.12", "+1:21.23"),
    ]
    
    y = 360
    for lap, total, split in lap_data:
        draw.rectangle([100, y-20, 700, y+20], fill='#2a2a3e', outline='#3a3a4e')
        draw.text((120, y), lap, fill='#00ff88', font_size=14)
        draw.text((300, y), total, fill='#ffffff', font_size=14)
        draw.text((500, y), split, fill='#4ecdc4', font_size=14)
        y += 50
    
    # 保存
    img.save('/home/lenovo/AItest/clawclock/docs/images/stopwatch-lap-diagram.png', 
             'PNG', optimize=True)
    print("✓ 已保存秒表计圈示意图")


def create_timer_breath_diagram():
    """创建倒计时呼吸灯效果示意图"""
    print("\n📊 创建倒计时呼吸灯效果示意图...")
    
    # 使用 PIL 创建示意图
    img = Image.new('RGB', (800, 600), color='#0d1117')
    draw = ImageDraw.Draw(img)
    
    # 标题
    draw.text((400, 40), "Timer Breath Light Effect", 
             fill='#00ff88', anchor='center',
             font_size=24)
    
    # 中心计时器
    draw.ellipse([250, 100, 550, 400], outline='#00ff88', width=5)
    draw.text((400, 250), "25:00", 
             fill='#00ff88', anchor='center',
             font_size=56)
    
    # 呼吸效果示意（多个同心圆）
    for i in range(3, 0, -1):
        alpha = int(255 * (i / 3) * 0.3)
        color = f'#{0:02x}{255:02x}{136:02x}'
        offset = i * 20
        draw.ellipse([250-offset, 100-offset, 550+offset, 400+offset], 
                    outline=color, width=2)
    
    # 状态指示
    status_colors = [
        ('#00ff88', 'Normal'),
        ('#ffaa00', 'Warning (<5min)'),
        ('#ff6b6b', 'Completed'),
    ]
    
    y = 450
    for color, label in status_colors:
        draw.ellipse([200, y-15, 230, y+15], fill=color)
        draw.text((250, y), label, fill='#ffffff', font_size=16)
        y += 40
    
    # 保存
    img.save('/home/lenovo/AItest/clawclock/docs/images/timer-breath-effect.png', 
             'PNG', optimize=True)
    print("✓ 已保存呼吸灯效果示意图")


def create_timezone_flowchart():
    """创建时区选择器使用流程图"""
    print("\n📊 创建时区选择器流程图...")
    
    # 使用 PIL 创建流程图
    img = Image.new('RGB', (900, 700), color='#1a1a2e')
    draw = ImageDraw.Draw(img)
    
    # 标题
    draw.text((450, 30), "Timezone Selector Flow", 
             fill='#00ff88', anchor='center',
             font_size=24)
    
    # 流程图节点
    nodes = [
        (450, 100, "Open Settings", '#00ff88'),
        (450, 200, "Click Timezone", '#4ecdc4'),
        (450, 300, "Search City", '#4ecdc4'),
        (450, 400, "Select Result", '#4ecdc4'),
        (450, 500, "Timezone Applied", '#00ff88'),
    ]
    
    # 绘制节点和连线
    for i, (x, y, text, color) in enumerate(nodes):
        # 节点框
        draw.rounded_rectangle([x-150, y-30, x+150, y+30], 
                              radius=15, outline=color, width=3)
        draw.text((x, y), text, fill='#ffffff', anchor='center',
                 font_size=16)
        
        # 连线
        if i < len(nodes) - 1:
            next_y = nodes[i+1][1]
            draw.line([(x, y+30), (x, next_y-30)], 
                     fill='#4ecdc4', width=2)
            # 箭头
            arrow_y = next_y - 30
            draw.polygon([(x-10, arrow_y-10), (x+10, arrow_y-10), 
                         (x, arrow_y)], fill='#4ecdc4')
    
    # 示例时区列表
    draw.rectangle([650, 250, 850, 450], fill='#2a2a3e', outline='#3a3a4e')
    timezones = ["UTC+8 Beijing", "UTC+0 London", "UTC-5 New York", "UTC+9 Tokyo"]
    for i, tz in enumerate(timezones):
        y = 270 + i*40
        draw.text((670, y), tz, fill='#ffffff', font_size=14)
    
    # 保存
    img.save('/home/lenovo/AItest/clawclock/docs/images/timezone-flowchart.png', 
             'PNG', optimize=True)
    print("✓ 已保存时区选择器流程图")


def main():
    """主函数"""
    print("=" * 60)
    print("ClawClock 截图生成工具")
    print("=" * 60)
    
    # 确保输出目录存在
    os.makedirs('/home/lenovo/AItest/clawclock/screenshots', exist_ok=True)
    os.makedirs('/home/lenovo/AItest/clawclock/screenshots/themes', exist_ok=True)
    os.makedirs('/home/lenovo/AItest/clawclock/docs/images', exist_ok=True)
    
    # P0: 界面截图
    print("\n🎯 P0: 生成界面截图...")
    create_alarm_screenshot()
    create_timer_screenshot()
    create_shortcuts_screenshot()
    
    # P2: 主题预览
    print("\n🎯 P2: 生成主题预览...")
    themes = [
        ("Dark", '#1a1a2e', '#ffffff', '#00ff88'),
        ("Light", '#f5f5f5', '#333333', '#0066cc'),
        ("Green", '#0d1f14', '#e0ffe0', '#00ff88'),
        ("Cyberpunk", '#0d0d1a', '#ff00ff', '#00ffff'),
    ]
    
    for theme_name, bg, fg, accent in themes:
        create_theme_preview(theme_name, bg, fg, accent)
    
    # P3: 功能示意图
    print("\n🎯 P3: 生成功能示意图...")
    create_stopwatch_lap_diagram()
    create_timer_breath_diagram()
    create_timezone_flowchart()
    
    print("\n" + "=" * 60)
    print("✅ 所有截图生成完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
