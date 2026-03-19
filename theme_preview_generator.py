#!/usr/bin/env python3
"""
ClawClock 主题预览生成器
=======================
生成 4 种主题的预览图（Dark/Light/Green/Cyberpunk）
"""

from PIL import Image, ImageDraw, ImageFont
import os


def create_theme_preview(theme_name, colors):
    """
    创建主题预览图
    
    Args:
        theme_name: 主题名称
        colors: 颜色配置字典
            - background: 背景色
            - surface: 表面色（卡片、面板）
            - primary: 主色调
            - secondary: 辅助色
            - text_primary: 主文字色
            - text_secondary: 辅助文字色
    """
    print(f"\n🎨 创建 {theme_name} 主题预览...")
    
    # 创建图像
    img = Image.new('RGB', (800, 600), color=colors['background'])
    draw = ImageDraw.Draw(img)
    
    # 尝试加载字体
    try:
        font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
        font_subtitle = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
        font_time = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", 56)
        font_date = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
        font_button = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
    except:
        font_title = ImageFont.load_default()
        font_subtitle = ImageFont.load_default()
        font_time = ImageFont.load_default()
        font_date = ImageFont.load_default()
        font_button = ImageFont.load_default()
    
    # 主标题
    draw.text((400, 40), "ClawClock", 
             fill=colors['text_primary'], anchor='mm', font=font_title)
    draw.text((400, 75), f"{theme_name} Theme", 
             fill=colors['text_secondary'], anchor='mm', font=font_subtitle)
    
    # 时钟显示区域
    clock_x, clock_y = 400, 180
    clock_width, clock_height = 500, 150
    
    # 时钟背景
    draw.rounded_rectangle([clock_x-clock_width//2, clock_y-clock_height//2,
                           clock_x+clock_width//2, clock_y+clock_height//2],
                          radius=15, fill=colors['surface'], outline=colors['primary'], width=2)
    
    # 时间显示
    draw.text((clock_x, clock_y-10), "14:30:45", 
             fill=colors['primary'], anchor='mm', font=font_time)
    
    # 日期显示
    draw.text((clock_x, clock_y+50), "2026-03-19 Thursday", 
             fill=colors['text_secondary'], anchor='mm', font=font_date)
    
    # 功能按钮区域
    button_y = 320
    buttons = [
        ("⏰ Alarm", colors['primary']),
        ("⏱️ Timer", colors['secondary']),
        ("🕐 Stopwatch", colors['primary']),
        ("⚙️ Settings", colors['secondary']),
    ]
    
    button_width = 160
    button_height = 60
    spacing = 20
    total_width = button_width * 4 + spacing * 3
    start_x = (800 - total_width) // 2
    
    for i, (label, btn_color) in enumerate(buttons):
        x = start_x + i * (button_width + spacing)
        
        # 按钮背景
        draw.rounded_rectangle([x, button_y, x+button_width, button_y+button_height],
                              radius=10, fill=btn_color)
        
        # 按钮文字
        draw.text((x+button_width//2, button_y+button_height//2), 
                 label, fill=colors['background'], anchor='mm', font=font_button)
    
    # 功能特性列表
    features_y = 420
    draw.text((80, features_y), "✨ Features:", 
             fill=colors['text_primary'], anchor='lt', font=font_subtitle)
    
    features = [
        "• Multiple timezone support",
        "• Customizable alarms with repeat schedules",
        "• Pomodoro timer with breath light effects",
        "• Precise stopwatch with lap recording",
    ]
    
    for i, feature in enumerate(features):
        y = features_y + 40 + i * 30
        draw.text((80, y), feature, 
                 fill=colors['text_secondary'], anchor='lt', font=font_date)
    
    # 主题色卡展示
    color_swatches_y = 540
    swatch_size = 40
    swatch_spacing = 15
    swatch_start_x = (800 - (5*swatch_size + 4*swatch_spacing)) // 2
    
    color_names = ['Background', 'Surface', 'Primary', 'Secondary', 'Text']
    color_values = [
        colors['background'],
        colors['surface'],
        colors['primary'],
        colors['secondary'],
        colors['text_primary']
    ]
    
    for i, (name, color) in enumerate(zip(color_names, color_values)):
        x = swatch_start_x + i * (swatch_size + swatch_spacing)
        
        # 色块
        draw.rectangle([x, color_swatches_y, x+swatch_size, color_swatches_y+swatch_size],
                      fill=color, outline=colors['text_secondary'] if name == 'Background' else None)
        
        # 色块名称
        draw.text((x+swatch_size//2, color_swatches_y+swatch_size+15), 
                 name, fill=colors['text_secondary'], anchor='mt', font=ImageFont.load_default())
    
    # 保存
    filename = f'/home/lenovo/AItest/clawclock/screenshots/themes/{theme_name.lower()}-theme.png'
    img.save(filename, 'PNG', optimize=True)
    print(f"✓ 已保存 {theme_name} 主题预览：{filename}")


def main():
    """主函数"""
    print("=" * 60)
    print("ClawClock 主题预览生成器")
    print("=" * 60)
    
    # 确保输出目录存在
    os.makedirs('/home/lenovo/AItest/clawclock/screenshots/themes', exist_ok=True)
    
    # 定义 4 种主题配色
    themes = {
        'Dark': {
            'background': '#1a1a2e',
            'surface': '#16213e',
            'primary': '#00ff88',
            'secondary': '#4ecdc4',
            'text_primary': '#ffffff',
            'text_secondary': '#a0a0a0',
        },
        'Light': {
            'background': '#f5f5f5',
            'surface': '#ffffff',
            'primary': '#0066cc',
            'secondary': '#00aa88',
            'text_primary': '#333333',
            'text_secondary': '#666666',
        },
        'Green': {
            'background': '#0d1f14',
            'surface': '#1a3a2a',
            'primary': '#00ff88',
            'secondary': '#88ffaa',
            'text_primary': '#e0ffe0',
            'text_secondary': '#88cc99',
        },
        'Cyberpunk': {
            'background': '#0d0d1a',
            'surface': '#1a1a2e',
            'primary': '#ff00ff',
            'secondary': '#00ffff',
            'text_primary': '#ff00ff',
            'text_secondary': '#00ffff',
        },
    }
    
    # 生成所有主题预览
    for theme_name, colors in themes.items():
        create_theme_preview(theme_name, colors)
    
    print("\n" + "=" * 60)
    print("✅ 所有主题预览生成完成！")
    print("=" * 60)
    
    # 列出生成的文件
    output_dir = '/home/lenovo/AItest/clawclock/screenshots/themes'
    print(f"\n生成的主题文件:")
    for f in sorted(os.listdir(output_dir)):
        filepath = os.path.join(output_dir, f)
        file_size = os.path.getsize(filepath)
        print(f"  {f:25s} ({file_size:,} bytes)")


if __name__ == "__main__":
    main()
