#!/usr/bin/env python3
"""
ClawClock 功能示意图生成器
=========================
生成秒表计圈、呼吸灯效果、时区选择器等示意图
"""

from PIL import Image, ImageDraw, ImageFont
import math
import os


def create_stopwatch_lap_diagram():
    """创建秒表计圈功能示意图"""
    print("\n📊 创建秒表计圈功能示意图...")
    
    # 创建图像
    img = Image.new('RGB', (800, 600), color='#1a1a2e')
    draw = ImageDraw.Draw(img)
    
    # 尝试加载字体
    try:
        font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
        font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
        font_mono = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", 36)
    except:
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()
        font_mono = ImageFont.load_default()
    
    # 标题
    draw.text((400, 30), "Stopwatch Lap Function", 
             fill='#00ff88', anchor='mm', font=font_medium)
    
    # 主计时器显示
    draw.rectangle([150, 70, 650, 170], outline='#00ff88', width=3)
    draw.rectangle([152, 72, 648, 168], fill='#0d1117')
    draw.text((400, 120), "12:34.56", 
             fill='#00ff88', anchor='mm', font=font_mono)
    
    # 按钮
    buttons = [
        ('Start', '#00ff88', 180),
        ('Lap', '#4ecdc4', 320),
        ('Reset', '#ff6b6b', 460),
    ]
    
    for label, color, x in buttons:
        # 按钮背景
        draw.rounded_rectangle([x, 200, x+100, 250], radius=8, fill=color)
        # 按钮文字
        draw.text((x+50, 225), label, fill='#1a1a2e', anchor='mm', font=font_small)
    
    # 圈速列表标题
    draw.text((100, 290), "Lap Times:", fill='#ffffff', font=font_medium, anchor='lt')
    
    # 表头
    draw.line([(100, 320), (700, 320)], fill='#3a3a4e', width=2)
    draw.text((120, 330), "Lap", fill='#00ff88', font=font_small, anchor='lt')
    draw.text((300, 330), "Total Time", fill='#ffffff', font=font_small, anchor='lt')
    draw.text((500, 330), "Split", fill='#4ecdc4', font=font_small, anchor='lt')
    draw.line([(100, 350), (700, 350)], fill='#3a3a4e', width=1)
    
    # 圈速数据
    lap_data = [
        ("1", "1:23.45", "+0:00.00", '#ffffff'),
        ("2", "2:45.67", "+1:22.22", '#ffffff'),
        ("3", "4:12.89", "+1:27.22", '#00ff88'),  # 最快圈
        ("4", "5:34.12", "+1:21.23", '#ffffff'),
    ]
    
    y = 370
    for lap_num, total, split, color in lap_data:
        # 背景
        draw.rectangle([100, y-15, 700, y+15], fill='#2a2a3e')
        # 数据
        draw.text((120, y), f"Lap {lap_num}", fill='#00ff88', font=font_small, anchor='lt')
        draw.text((300, y), total, fill=color, font=font_small, anchor='lt')
        draw.text((500, y), split, fill='#4ecdc4', font=font_small, anchor='lt')
        y += 45
    
    # 保存
    output_path = '/home/lenovo/AItest/clawclock/docs/images/stopwatch-lap-diagram.png'
    img.save(output_path, 'PNG', optimize=True)
    print(f"✓ 已保存秒表计圈示意图：{output_path}")


def create_timer_breath_diagram():
    """创建倒计时呼吸灯效果示意图"""
    print("\n📊 创建倒计时呼吸灯效果示意图...")
    
    # 创建图像
    img = Image.new('RGB', (800, 600), color='#0d1117')
    draw = ImageDraw.Draw(img)
    
    # 尝试加载字体
    try:
        font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
        font_time = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", 56)
        font_label = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
    except:
        font_title = ImageFont.load_default()
        font_time = ImageFont.load_default()
        font_label = ImageFont.load_default()
    
    # 标题
    draw.text((400, 30), "Timer Breath Light Effect", 
             fill='#00ff88', anchor='mm', font=font_title)
    
    # 中心点
    center_x, center_y = 400, 280
    
    # 呼吸效果（多个同心圆，模拟呼吸动画）
    breath_frames = [
        (180, 60, '#00ff88'),   # 最外层，最淡
        (160, 100, '#00ff88'),  # 中间层
        (140, 160, '#00ff88'),  # 最内层，最亮
    ]
    
    for radius, alpha, color in breath_frames:
        # 将 alpha 转换为实际颜色
        r, g, b = 0, 255, 136
        actual_alpha = int(255 * (alpha / 160) * 0.4)
        fill_color = (r, g, b, actual_alpha)
        
        # 绘制半透明圆环（简化为实色圆环）
        draw.ellipse([center_x-radius, center_y-radius, 
                      center_x+radius, center_y+radius], 
                    outline=color, width=3)
    
    # 主计时器圆环
    draw.ellipse([center_x-120, center_y-120, 
                  center_x+120, center_y+120], 
                outline='#00ff88', width=5)
    
    # 时间显示
    draw.text((center_x, center_y), "25:00", 
             fill='#00ff88', anchor='mm', font=font_time)
    
    # 状态指示器
    status_y = 450
    statuses = [
        ('#00ff88', 'Normal', 'Running normally'),
        ('#ffaa00', 'Warning', 'Less than 5 minutes'),
        ('#ff6b6b', 'Completed', 'Time is up!'),
    ]
    
    for i, (color, title, desc) in enumerate(statuses):
        y = status_y + i * 50
        
        # 指示灯
        draw.ellipse([250, y-12, 274, y+12], fill=color)
        
        # 文字
        draw.text((290, y-8), title, fill='#ffffff', font=font_label, anchor='lt')
        draw.text((290, y+8), desc, fill='#888888', font=font_label, anchor='lt')
    
    # 保存
    output_path = '/home/lenovo/AItest/clawclock/docs/images/timer-breath-effect.png'
    img.save(output_path, 'PNG', optimize=True)
    print(f"✓ 已保存呼吸灯效果示意图：{output_path}")


def create_timezone_flowchart():
    """创建时区选择器使用流程图"""
    print("\n📊 创建时区选择器流程图...")
    
    # 创建图像
    img = Image.new('RGB', (900, 700), color='#1a1a2e')
    draw = ImageDraw.Draw(img)
    
    # 尝试加载字体
    try:
        font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
        font_node = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
        font_tz = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
    except:
        font_title = ImageFont.load_default()
        font_node = ImageFont.load_default()
        font_tz = ImageFont.load_default()
    
    # 标题
    draw.text((450, 30), "Timezone Selector Flow", 
             fill='#00ff88', anchor='mm', font=font_title)
    
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
        draw.rounded_rectangle([x-140, y-30, x+140, y+30], 
                              radius=15, outline=color, width=3)
        # 节点文字
        draw.text((x, y), text, fill='#ffffff', anchor='mm', font=font_node)
        
        # 连线
        if i < len(nodes) - 1:
            next_y = nodes[i+1][1]
            # 垂直线
            draw.line([(x, y+30), (x, next_y-30)], fill='#4ecdc4', width=2)
            # 箭头
            arrow_y = next_y - 30
            draw.polygon([
                (x-8, arrow_y-15),
                (x+8, arrow_y-15),
                (x, arrow_y)
            ], fill='#4ecdc4')
    
    # 时区列表示例
    list_x, list_y = 650, 250
    draw.rectangle([list_x, list_y, list_x+200, list_y+180], 
                  fill='#2a2a3e', outline='#3a3a4e', width=2)
    
    # 列表标题
    draw.rectangle([list_x, list_y, list_x+200, list_y+30], fill='#3a3a4e')
    draw.text((list_x+100, list_y+15), "Available Timezones", 
             fill='#ffffff', anchor='mm', font=font_node)
    
    # 时区项
    timezones = [
        ("UTC+8", "Beijing", True),
        ("UTC+0", "London", False),
        ("UTC-5", "New York", False),
        ("UTC+9", "Tokyo", False),
    ]
    
    for i, (utc, city, selected) in enumerate(timezones):
        y = list_y + 45 + i * 35
        bg_color = '#4a4a5e' if selected else '#2a2a3e'
        draw.rectangle([list_x+5, y-12, list_x+195, y+12], fill=bg_color)
        
        if selected:
            draw.line([(list_x+10, y), (list_x+25, y)], fill='#00ff88', width=2)
            draw.line([(list_x+15, y-5), (list_x+20, y+5)], fill='#00ff88', width=2)
            draw.line([(list_x+20, y-5), (list_x+25, y+5)], fill='#00ff88', width=2)
        
        draw.text((list_x+35 if selected else list_x+10, y), 
                 f"{utc} {city}", fill='#ffffff', anchor='lt', font=font_tz)
    
    # 保存
    output_path = '/home/lenovo/AItest/clawclock/docs/images/timezone-flowchart.png'
    img.save(output_path, 'PNG', optimize=True)
    print(f"✓ 已保存时区选择器流程图：{output_path}")


def main():
    """主函数"""
    print("=" * 60)
    print("ClawClock 功能示意图生成器")
    print("=" * 60)
    
    # 确保输出目录存在
    os.makedirs('/home/lenovo/AItest/clawclock/docs/images', exist_ok=True)
    
    # 生成所有示意图
    create_stopwatch_lap_diagram()
    create_timer_breath_diagram()
    create_timezone_flowchart()
    
    print("\n" + "=" * 60)
    print("✅ 所有示意图生成完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
