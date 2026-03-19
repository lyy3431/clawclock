#!/usr/bin/env python3
"""
ClawClock 界面截图生成器（PIL 版本）
=================================
使用 PIL 模拟生成界面截图，无需实际运行 GUI
"""

from PIL import Image, ImageDraw, ImageFont
import os


def create_alarm_management_screenshot():
    """创建闹钟管理界面截图"""
    print("\n📸 创建闹钟管理界面截图...")
    
    # 创建图像
    img = Image.new('RGB', (800, 600), color='#1a1a2e')
    draw = ImageDraw.Draw(img)
    
    # 加载字体
    try:
        font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
        font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
        font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
        font_mono = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", 28)
    except:
        font_title = ImageFont.load_default()
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()
        font_mono = ImageFont.load_default()
    
    # 窗口边框
    draw.rectangle([0, 0, 799, 599], outline='#3a3a4e', width=2)
    
    # 标题栏
    draw.rectangle([0, 0, 800, 50], fill='#16213e')
    draw.text((20, 25), "⏰ ClawClock - Alarm Management", 
             fill='#ffffff', anchor='lm', font=font_medium)
    
    # 主标题
    draw.text((400, 90), "闹钟管理", 
             fill='#00ff88', anchor='mm', font=font_title)
    
    # 闹钟列表框架
    list_y = 140
    draw.rectangle([50, list_y, 750, 480], fill='#16213e', outline='#3a3a4e', width=2)
    draw.text((70, list_y+15), "已设置的闹钟", 
             fill='#ffffff', anchor='lm', font=font_medium)
    
    # 分隔线
    draw.line([(50, list_y+40), (750, list_y+40)], fill='#3a3a4e', width=1)
    
    # 闹钟项
    alarms = [
        ("07:00", "起床闹钟", "每天", True),
        ("09:00", "晨会提醒", "工作日", True),
        ("12:30", "午餐时间", "每天", False),
        ("23:00", "睡觉提醒", "每天", True),
    ]
    
    row_y = list_y + 60
    row_height = 60
    
    for time_str, label, repeat, enabled in alarms:
        # 行背景
        row_color = '#1a1a2e' if enabled else '#0f0f1a'
        draw.rectangle([60, row_y, 740, row_y+row_height-10], fill=row_color)
        
        # 时间
        draw.text((80, row_y+30), time_str, 
                 fill='#00ff88', anchor='lm', font=font_mono)
        
        # 标签
        draw.text((200, row_y+30), label, 
                 fill='#ffffff', anchor='lm', font=font_medium)
        
        # 重复周期
        draw.text((380, row_y+30), f"重复：{repeat}", 
                 fill='#888888', anchor='lm', font=font_small)
        
        # 开关
        switch_x = 680
        switch_y = row_y + 30
        if enabled:
            draw.rectangle([switch_x, switch_y-12, switch_x+50, switch_y+12], 
                          fill='#00ff88', outline='#00ff88')
            draw.ellipse([switch_x+28, switch_y-10, switch_x+48, switch_y+10], 
                       fill='#ffffff')
        else:
            draw.rectangle([switch_x, switch_y-12, switch_x+50, switch_y+12], 
                          fill='#3a3a4e', outline='#5a5a6e')
            draw.ellipse([switch_x+2, switch_y-10, switch_x+22, switch_y+10], 
                       fill='#888888')
        
        row_y += row_height
    
    # 添加按钮
    btn_y = 510
    draw.rounded_rectangle([300, btn_y, 500, btn_y+50], radius=10, fill='#00ff88')
    draw.text((400, btn_y+25), "+ 添加新闹钟", 
             fill='#1a1a2e', anchor='mm', font=font_medium)
    
    # 保存
    output_path = '/home/lenovo/AItest/clawclock/screenshots/alarm-management.png'
    img.save(output_path, 'PNG', optimize=True)
    print(f"✓ 已保存闹钟管理界面：{output_path}")


def create_timer_custom_screenshot():
    """创建倒计时自定义输入界面截图"""
    print("\n📸 创建倒计时自定义输入界面截图...")
    
    # 创建图像
    img = Image.new('RGB', (700, 550), color='#1a1a2e')
    draw = ImageDraw.Draw(img)
    
    # 加载字体
    try:
        font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
        font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
        font_time = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", 42)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
    except:
        font_title = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_time = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # 窗口边框
    draw.rectangle([0, 0, 699, 549], outline='#3a3a4e', width=2)
    
    # 标题栏
    draw.rectangle([0, 0, 700, 50], fill='#16213e')
    draw.text((20, 25), "⏱️ ClawClock - Timer", 
             fill='#ffffff', anchor='lm', font=font_medium)
    
    # 主标题
    draw.text((350, 90), "倒计时", 
             fill='#00ff88', anchor='mm', font=font_title)
    
    # 时间输入
    time_y = 150
    inputs = [
        (150, "小时", "00"),
        (300, "分钟", "25"),
        (450, "秒", "00"),
    ]
    
    for x, label, value in inputs:
        # 标签
        draw.text((x, time_y), label, 
                 fill='#888888', anchor='mm', font=font_small)
        
        # 输入框
        draw.rectangle([x-40, time_y+20, x+40, time_y+70], 
                      fill='#16213e', outline='#00ff88', width=2)
        draw.text((x, time_y+45), value, 
                 fill='#00ff88', anchor='mm', font=font_time)
    
    # 预设时间框架
    preset_y = 260
    draw.rectangle([50, preset_y, 650, 360], fill='#16213e', outline='#3a3a4e', width=2)
    draw.text((70, preset_y+20), "预设时间", 
             fill='#ffffff', anchor='lm', font=font_medium)
    
    # 预设按钮
    presets = [
        ("🍅 番茄钟", 150),
        ("☕ 短休息", 300),
        ("🍽️ 长休息", 450),
        ("🧘 冥想", 600),
    ]
    
    for label, x in presets:
        draw.rounded_rectangle([x-80, preset_y+50, x+80, preset_y+90], 
                              radius=8, fill='#4ecdc4')
        draw.text((x, preset_y+70), label, 
                 fill='#1a1a2e', anchor='mm', font=font_medium)
    
    # 控制按钮
    btn_y = 400
    buttons = [
        ("▶ 开始", '#00ff88', 200),
        ("⏸ 暂停", '#ffaa00', 350),
        ("↺ 重置", '#ff6b6b', 500),
    ]
    
    for label, color, x in buttons:
        draw.rounded_rectangle([x-80, btn_y, x+80, btn_y+50], 
                              radius=10, fill=color)
        draw.text((x, btn_y+25), label, 
                 fill='#1a1a2e', anchor='mm', font=font_medium)
    
    # 保存
    output_path = '/home/lenovo/AItest/clawclock/screenshots/timer-custom.png'
    img.save(output_path, 'PNG', optimize=True)
    print(f"✓ 已保存倒计时界面：{output_path}")


def create_keyboard_shortcuts_screenshot():
    """创建键盘快捷键提示界面截图"""
    print("\n📸 创建键盘快捷键提示界面截图...")
    
    # 创建图像
    img = Image.new('RGB', (650, 500), color='#1a1a2e')
    draw = ImageDraw.Draw(img)
    
    # 加载字体
    try:
        font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
        font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
        font_mono = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", 18)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
    except:
        font_title = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_mono = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # 窗口边框
    draw.rectangle([0, 0, 649, 499], outline='#3a3a4e', width=2)
    
    # 标题栏
    draw.rectangle([0, 0, 650, 50], fill='#16213e')
    draw.text((20, 25), "⌨️ ClawClock - Shortcuts", 
             fill='#ffffff', anchor='lm', font=font_medium)
    
    # 主标题
    draw.text((325, 90), "键盘快捷键", 
             fill='#00ff88', anchor='mm', font=font_title)
    
    # 快捷键列表框架
    list_y = 140
    draw.rectangle([50, list_y, 600, 420], fill='#16213e', outline='#3a3a4e', width=2)
    draw.text((70, list_y+20), "全局快捷键", 
             fill='#ffffff', anchor='lm', font=font_medium)
    
    # 快捷键项
    shortcuts = [
        ("Ctrl + N", "新建闹钟"),
        ("Ctrl + T", "打开倒计时"),
        ("Ctrl + S", "打开秒表"),
        ("Ctrl + W", "关闭当前窗口"),
        ("F5", "刷新时间"),
        ("F11", "全屏模式"),
        ("Esc", "退出全屏"),
    ]
    
    row_y = list_y + 50
    row_height = 45
    
    for keys, desc in shortcuts:
        # 行背景
        draw.rectangle([60, row_y, 590, row_y+row_height-5], fill='#1a1a2e')
        
        # 快捷键
        draw.text((80, row_y+22), keys, 
                 fill='#00ff88', anchor='lm', font=font_mono)
        
        # 描述
        draw.text((280, row_y+22), desc, 
                 fill='#ffffff', anchor='lm', font=font_medium)
        
        row_y += row_height
    
    # 底部提示
    draw.text((325, 455), "💡 提示：可在设置中自定义快捷键", 
             fill='#888888', anchor='mm', font=font_small)
    
    # 保存
    output_path = '/home/lenovo/AItest/clawclock/screenshots/keyboard-shortcuts.png'
    img.save(output_path, 'PNG', optimize=True)
    print(f"✓ 已保存快捷键界面：{output_path}")


def main():
    """主函数"""
    print("=" * 60)
    print("ClawClock 界面截图生成器（PIL 版本）")
    print("=" * 60)
    
    # 确保输出目录存在
    os.makedirs('/home/lenovo/AItest/clawclock/screenshots', exist_ok=True)
    
    # 生成所有界面截图
    create_alarm_management_screenshot()
    create_timer_custom_screenshot()
    create_keyboard_shortcuts_screenshot()
    
    print("\n" + "=" * 60)
    print("✅ 所有界面截图生成完成！")
    print("=" * 60)
    
    # 列出生成的文件
    output_dir = '/home/lenovo/AItest/clawclock/screenshots'
    print(f"\n生成的截图文件:")
    for f in sorted(os.listdir(output_dir)):
        filepath = os.path.join(output_dir, f)
        file_size = os.path.getsize(filepath)
        print(f"  {f:30s} ({file_size:,} bytes)")


if __name__ == "__main__":
    main()
