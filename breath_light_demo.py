#!/usr/bin/env python3
"""
呼吸灯效果演示 - ClawClock 呼吸灯功能独立演示
============================================

运行此脚本以独立展示呼吸灯效果，无需启动完整应用。

使用方法:
    python3 breath_light_demo.py

作者：ClawClock Development Team
版本：1.5.0
"""

import tkinter as tk
import math
import time
from typing import Optional

# 导入呼吸灯模块
try:
    from breath_light import BreathLightEffect, BreathLightConfig, BreathMode, TimerStatus
except ImportError:
    print("❌ 无法导入呼吸灯模块")
    print("   请确保 breath_light.py 在同一目录下")
    import sys
    sys.exit(1)


class BreathLightDemo:
    """呼吸灯效果演示应用"""
    
    def __init__(self):
        """初始化演示应用"""
        self.root = tk.Tk()
        self.root.title("🫧 ClawClock 呼吸灯效果演示")
        self.root.geometry("600x400")
        self.root.configure(bg="#1a1a2e")
        
        # 创建呼吸灯效果
        config = BreathLightConfig(
            enabled=True,
            mode=BreathMode.DIGITAL,
            frequency=1.0,
            intensity=0.7,
            normal_color="#00ff88",
            warning_color="#ffaa00",
            completed_color="#ff3333",
            accelerate_on_complete=True
        )
        self.effect = BreathLightEffect(config)
        
        # UI 元素
        self._setup_ui()
        
        # 状态切换按钮
        self.current_status_idx = 0
        self.statuses = [TimerStatus.NORMAL, TimerStatus.WARNING, TimerStatus.COMPLETED]
    
    def _setup_ui(self):
        """设置用户界面"""
        # 标题
        title_label = tk.Label(
            self.root,
            text="🫧 呼吸灯效果演示",
            font=("Arial", 24, "bold"),
            bg="#1a1a2e",
            fg="#ffffff"
        )
        title_label.pack(pady=20)
        
        # 演示区域
        demo_frame = tk.Frame(self.root, bg="#16213e", padx=50, pady=50)
        demo_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 数字显示（模拟 7 段数码管）
        self.demo_label = tk.Label(
            demo_frame,
            text="25:00",
            font=("Courier New", 72, "bold"),
            bg="#16213e",
            fg="#00ff88"
        )
        self.demo_label.pack(pady=20)
        
        # 状态标签
        self.status_label = tk.Label(
            demo_frame,
            text="状态：正常运行",
            font=("Arial", 16),
            bg="#16213e",
            fg="#ffffff"
        )
        self.status_label.pack(pady=10)
        
        # 控制按钮
        btn_frame = tk.Frame(self.root, bg="#1a1a2e")
        btn_frame.pack(pady=20)
        
        # 状态切换按钮
        self.switch_btn = tk.Button(
            btn_frame,
            text="切换状态",
            font=("Arial", 14),
            bg="#0f3460",
            fg="#ffffff",
            command=self._switch_status,
            width=15
        )
        self.switch_btn.pack(side=tk.LEFT, padx=10)
        
        # 开始/停止按钮
        self.start_stop_btn = tk.Button(
            btn_frame,
            text="▶ 开始",
            font=("Arial", 14),
            bg="#28a745",
            fg="#ffffff",
            command=self._toggle_start_stop,
            width=15
        )
        self.start_stop_btn.pack(side=tk.LEFT, padx=10)
        
        # 配置说明
        info_text = """
        📖 配置说明:
        • 呼吸频率：1.0 Hz (1 秒/周期)
        • 呼吸强度：0.7 (70%)
        • 正常状态：绿色 (#00ff88)
        • 警告状态：橙色 (#ffaa00) - 最后 10 秒
        • 完成状态：红色 (#ff3333) - 时间到，加速呼吸
        """
        info_label = tk.Label(
            self.root,
            text=info_text,
            font=("Arial", 10),
            bg="#1a1a2e",
            fg="#aaaaaa",
            justify=tk.LEFT
        )
        info_label.pack(pady=10)
        
        self._running = False
    
    def _update_display(self, brightness: float, status: TimerStatus):
        """
        更新显示
        
        Args:
            brightness: 亮度值（0-1）
            status: 倒计时状态
        """
        base_color = self.effect.get_current_color()
        adjusted_color = self.effect.apply_brightness_to_color(base_color, brightness)
        self.demo_label.config(fg=adjusted_color)
    
    def _switch_status(self):
        """切换状态"""
        self.current_status_idx = (self.current_status_idx + 1) % len(self.statuses)
        new_status = self.statuses[self.current_status_idx]
        self.effect.set_status(new_status)
        
        status_text = {
            TimerStatus.NORMAL: "正常运行",
            TimerStatus.WARNING: "警告（最后 10 秒）",
            TimerStatus.COMPLETED: "完成（时间到）"
        }
        self.status_label.config(text=f"状态：{status_text[new_status]}")
        
        # 改变演示文本
        if new_status == TimerStatus.NORMAL:
            self.demo_label.config(text="25:00")
        elif new_status == TimerStatus.WARNING:
            self.demo_label.config(text="00:10")
        else:  # COMPLETED
            self.demo_label.config(text="00:00")
    
    def _toggle_start_stop(self):
        """切换开始/停止"""
        if self._running:
            self._stop()
        else:
            self._start()
    
    def _start(self):
        """启动呼吸灯"""
        self._running = True
        self.start_stop_btn.config(text="⏹ 停止", bg="#dc3545")
        self.effect.start(self.root, self._update_display)
    
    def _stop(self):
        """停止呼吸灯"""
        self._running = False
        self.start_stop_btn.config(text="▶ 开始", bg="#28a745")
        self.effect.stop(self.root)
    
    def run(self):
        """运行应用"""
        # 自动启动
        self._start()
        
        # 5 秒后切换到警告状态
        self.root.after(5000, lambda: self._auto_switch(TimerStatus.WARNING))
        # 10 秒后切换到完成状态
        self.root.after(10000, lambda: self._auto_switch(TimerStatus.COMPLETED))
        
        self.root.mainloop()
    
    def _auto_switch(self, status: TimerStatus):
        """自动切换状态（仅用于演示）"""
        if status == TimerStatus.WARNING:
            self.current_status_idx = 1
            self.effect.set_status(status)
            self.status_label.config(text="状态：警告（最后 10 秒）")
            self.demo_label.config(text="00:10")
        elif status == TimerStatus.COMPLETED:
            self.current_status_idx = 2
            self.effect.set_status(status)
            self.status_label.config(text="状态：完成（时间到）")
            self.demo_label.config(text="00:00")


def main():
    """主函数"""
    print("🫧 " + "="*60)
    print("🫧 ClawClock 呼吸灯效果演示")
    print("🫧 " + "="*60)
    print()
    print("📖 使用说明:")
    print("   • 点击 '切换状态' 按钮手动切换状态")
    print("   • 点击 '开始/停止' 按钮控制呼吸效果")
    print("   • 程序会自动演示三种状态（5 秒间隔）")
    print()
    print("🎨 状态说明:")
    print("   🟢 正常状态：绿色呼吸")
    print("   🟡 警告状态：橙色呼吸（最后 10 秒）")
    print("   🔴 完成状态：红色加速呼吸（时间到）")
    print()
    
    demo = BreathLightDemo()
    demo.run()


if __name__ == "__main__":
    main()
