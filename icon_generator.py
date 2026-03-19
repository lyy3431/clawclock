#!/usr/bin/env python3
"""
ClawClock 应用图标生成器
=======================
生成多尺寸的应用图标，风格：简约现代，时钟元素
"""

from PIL import Image, ImageDraw, ImageFont
import math
import os


def create_clock_icon(size, output_path):
    """
    创建时钟图标
    
    Args:
        size: 图标尺寸（整数，如 256）
        output_path: 输出路径
    """
    # 创建图像
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 计算中心点和半径
    center = size // 2
    radius = int(size * 0.4)
    
    # 渐变色背景圆
    # 外圈光晕
    glow_radius = int(radius * 1.15)
    for i in range(glow_radius, radius, -1):
        alpha = int(50 * (1 - (i - radius) / (glow_radius - radius)))
        color = (0, 255, 136, alpha)
        draw.ellipse([center-i, center-i, center+i, center+i], fill=color)
    
    # 主表盘背景
    gradient_start = (26, 26, 46)  # #1a1a2e
    gradient_end = (42, 42, 62)    # #2a2a3e
    
    # 绘制渐变圆（简化版：多层同心圆）
    for i in range(radius, 0, -2):
        ratio = i / radius
        r = int(gradient_start[0] + (gradient_end[0] - gradient_start[0]) * ratio)
        g = int(gradient_start[1] + (gradient_end[1] - gradient_start[1]) * ratio)
        b = int(gradient_start[2] + (gradient_end[2] - gradient_start[2]) * ratio)
        draw.ellipse([center-i, center-i, center+i, center+i], fill=(r, g, b))
    
    # 表盘边框
    border_color = (0, 255, 136, 200)
    draw.ellipse([center-radius, center-radius, 
                  center+radius, center+radius], 
                 outline=border_color, width=max(2, size // 64))
    
    # 刻度
    tick_color = (255, 255, 255, 180)
    for hour in range(12):
        angle = math.radians(hour * 30 - 90)  # 从 12 点开始
        inner_r = int(radius * 0.85)
        outer_r = int(radius * 0.95)
        
        x1 = int(center + inner_r * math.cos(angle))
        y1 = int(center + inner_r * math.sin(angle))
        x2 = int(center + outer_r * math.cos(angle))
        y2 = int(center + outer_r * math.sin(angle))
        
        tick_width = max(1, size // 128) if hour % 3 == 0 else max(1, size // 256)
        draw.line([(x1, y1), (x2, y2)], fill=tick_color, width=tick_width)
    
    # 时针（指向 10 点）
    hour_angle = math.radians(10 * 30 - 90)
    hour_length = int(radius * 0.5)
    hour_x = int(center + hour_length * math.cos(hour_angle))
    hour_y = int(center + hour_length * math.sin(hour_angle))
    draw.line([(center, center), (hour_x, hour_y)], 
             fill=(255, 255, 255), 
             width=max(3, size // 42))
    
    # 分针（指向 2 点）
    minute_angle = math.radians(2 * 30 - 90)
    minute_length = int(radius * 0.7)
    minute_x = int(center + minute_length * math.cos(minute_angle))
    minute_y = int(center + minute_length * math.sin(minute_angle))
    draw.line([(center, center), (minute_x, minute_y)], 
             fill=(0, 255, 136), 
             width=max(2, size // 56))
    
    # 秒针（指向 6 点）
    second_angle = math.radians(6 * 30 - 90)
    second_length = int(radius * 0.8)
    second_x = int(center + second_length * math.cos(second_angle))
    second_y = int(center + second_length * math.sin(second_angle))
    draw.line([(center, center), (second_x, second_y)], 
             fill=(255, 107, 107), 
             width=max(1, size // 85))
    
    # 中心点
    center_dot_radius = max(3, size // 32)
    draw.ellipse([center-center_dot_radius, center-center_dot_radius,
                  center+center_dot_radius, center+center_dot_radius],
                 fill=(255, 255, 255))
    
    # 添加"Claw"字样（小尺寸时省略）
    if size >= 64:
        try:
            # 尝试使用系统字体
            font_size = max(10, size // 16)
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
        except:
            font = ImageFont.load_default()
        
        text = "Claw"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_x = center - text_width // 2
        text_y = center + int(radius * 0.65)
        draw.text((text_x, text_y), text, fill=(0, 255, 136), font=font)
    
    # 保存图标
    img.save(output_path, 'PNG', optimize=True)
    print(f"✓ 已生成 {size}x{size} 图标：{output_path}")


def generate_all_sizes():
    """生成所有尺寸的图标"""
    print("=" * 60)
    print("ClawClock 图标生成器")
    print("=" * 60)
    
    # 确保输出目录存在
    output_dir = '/home/lenovo/AItest/clawclock/icons'
    os.makedirs(output_dir, exist_ok=True)
    
    # 生成多种尺寸
    sizes = [16, 32, 64, 128, 256]
    
    for size in sizes:
        output_path = os.path.join(output_dir, f'icon-{size}x{size}.png')
        create_clock_icon(size, output_path)
    
    # 生成标准命名版本（用于应用）
    standard_sizes = {
        'icon.png': 256,
        'icon-128.png': 128,
        'icon-64.png': 64,
        'icon-32.png': 32,
        'icon-16.png': 16,
    }
    
    for filename, size in standard_sizes.items():
        output_path = os.path.join(output_dir, filename)
        create_clock_icon(size, output_path)
    
    print("\n" + "=" * 60)
    print("✅ 所有图标生成完成！")
    print("=" * 60)
    
    # 列出所有生成的文件
    print("\n生成的图标文件:")
    for f in sorted(os.listdir(output_dir)):
        filepath = os.path.join(output_dir, f)
        file_size = os.path.getsize(filepath)
        print(f"  {f:20s} ({file_size:,} bytes)")


if __name__ == "__main__":
    generate_all_sizes()
