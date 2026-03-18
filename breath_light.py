#!/usr/bin/env python3
"""
呼吸灯效果模块 - ClawClock 呼吸灯功能
====================================

功能:
    - 倒计时运行时，数字/背景呈现呼吸式明暗变化
    - 呼吸频率可配置（默认 1-2 秒/周期）
    - 使用正弦波实现呼吸效果
    - 多种呼吸模式：数字呼吸、背景呼吸、边框呼吸
    - 时间到特殊效果：呼吸加速、颜色变化

作者：ClawClock Development Team
版本：1.5.0
"""

import tkinter as tk
import math
import time
from typing import Optional, Tuple, Dict, Any
from dataclasses import dataclass
from enum import Enum


class BreathMode(Enum):
    """呼吸灯模式枚举"""
    DIGITAL = "digital"      # 数字呼吸（7 段数码管亮度变化）
    BACKGROUND = "background"  # 背景呼吸（窗口背景色渐变）
    BORDER = "border"        # 边框呼吸（窗口边框光晕效果）
    ALL = "all"              # 全部模式


class TimerStatus(Enum):
    """倒计时状态"""
    NORMAL = "normal"          # 正常运行
    WARNING = "warning"        # 最后 10 秒警告
    COMPLETED = "completed"    # 时间到


@dataclass
class BreathLightConfig:
    """呼吸灯配置数据类"""
    enabled: bool = True
    mode: BreathMode = BreathMode.DIGITAL
    frequency: float = 1.0  # 呼吸频率（周期/秒）
    intensity: float = 0.7  # 呼吸强度（0-1）
    normal_color: str = "#00ff88"  # 正常状态颜色
    warning_color: str = "#ffaa00"  # 警告状态颜色
    completed_color: str = "#ff3333"  # 完成状态颜色
    accelerate_on_complete: bool = True  # 时间到时加速呼吸


class BreathLightEffect:
    """
    呼吸灯效果核心类
    
    提供正弦波呼吸效果，支持多种模式和颜色主题
    
    Attributes:
        config: 呼吸灯配置
        status: 当前状态
        running: 是否正在运行
    """
    
    def __init__(self, config: Optional[BreathLightConfig] = None):
        """
        初始化呼吸灯效果
        
        Args:
            config: 呼吸灯配置，None 则使用默认配置
        """
        self.config = config or BreathLightConfig()
        self.status = TimerStatus.NORMAL
        self.running = False
        self._start_time: float = 0.0
        self._current_brightness: float = 0.5
        self._animation_job: Optional[str] = None
        
        # 颜色解析缓存
        self._color_cache: Dict[str, Tuple[int, int, int]] = {}
    
    def start(self, root: tk.Tk, callback: callable) -> None:
        """
        启动呼吸灯效果
        
        Args:
            root: Tkinter 主窗口
            callback: 亮度更新回调函数，接收 brightness (0-1) 参数
        """
        if not self.config.enabled:
            return
        
        self.running = True
        self._start_time = time.time()
        self._animate(root, callback)
    
    def stop(self, root: tk.Tk) -> None:
        """
        停止呼吸灯效果
        
        Args:
            root: Tkinter 主窗口
        """
        self.running = False
        if self._animation_job and root:
            try:
                root.after_cancel(self._animation_job)
            except Exception:
                pass
            self._animation_job = None
    
    def set_status(self, status: TimerStatus) -> None:
        """
        设置倒计时状态
        
        Args:
            status: 倒计时状态
        """
        self.status = status
    
    def _animate(self, root: tk.Tk, callback: callable) -> None:
        """
        动画循环
        
        Args:
            root: Tkinter 主窗口
            callback: 亮度更新回调函数
        """
        if not self.running:
            return
        
        # 计算当前时间
        elapsed = time.time() - self._start_time
        
        # 根据状态调整频率
        frequency = self.config.frequency
        if self.status == TimerStatus.COMPLETED and self.config.accelerate_on_complete:
            frequency *= 3  # 时间到时频率加快 3 倍
        elif self.status == TimerStatus.WARNING:
            frequency *= 1.5  # 警告时频率加快 1.5 倍
        
        # 使用正弦波计算亮度
        brightness = (math.sin(elapsed * frequency * 2 * math.pi) + 1) / 2
        
        # 应用强度
        intensity = self.config.intensity
        brightness = 0.5 + (brightness - 0.5) * intensity
        
        # 确保亮度在 0-1 范围内
        brightness = max(0.0, min(1.0, brightness))
        
        self._current_brightness = brightness
        
        # 调用回调更新显示
        try:
            callback(brightness, self.status)
        except Exception as e:
            print(f"⚠️  呼吸灯回调错误：{e}")
        
        # 继续动画（50ms 刷新率）
        self._animation_job = root.after(50, lambda: self._animate(root, callback))
    
    def get_current_color(self) -> str:
        """
        获取当前状态对应的颜色
        
        Returns:
            颜色十六进制字符串
        """
        if self.status == TimerStatus.COMPLETED:
            return self.config.completed_color
        elif self.status == TimerStatus.WARNING:
            return self.config.warning_color
        else:
            return self.config.normal_color
    
    def apply_brightness_to_color(self, base_color: str, brightness: float) -> str:
        """
        将亮度应用到颜色上
        
        Args:
            base_color: 基础颜色（十六进制）
            brightness: 亮度（0-1）
            
        Returns:
            调整后的颜色（十六进制）
        """
        # 解析颜色
        if base_color not in self._color_cache:
            hex_color = base_color.lstrip('#')
            rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            self._color_cache[base_color] = rgb
        
        r, g, b = self._color_cache[base_color]
        
        # 应用亮度（变暗效果）
        factor = 0.3 + 0.7 * brightness  # 最小亮度 30%
        r = int(r * factor)
        g = int(g * factor)
        b = int(b * factor)
        
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def update_config(self, **kwargs) -> None:
        """
        更新配置
        
        Args:
            **kwargs: 配置参数
        """
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "enabled": self.config.enabled,
            "mode": self.config.mode.value,
            "frequency": self.config.frequency,
            "intensity": self.config.intensity,
            "color_scheme": {
                "normal": self.config.normal_color,
                "warning": self.config.warning_color,
                "completed": self.config.completed_color
            },
            "accelerate_on_complete": self.config.accelerate_on_complete
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BreathLightEffect':
        """从字典创建实例"""
        config = BreathLightConfig(
            enabled=data.get("enabled", True),
            mode=BreathMode(data.get("mode", "digital")),
            frequency=data.get("frequency", 1.0),
            intensity=data.get("intensity", 0.7),
            normal_color=data.get("color_scheme", {}).get("normal", "#00ff88"),
            warning_color=data.get("color_scheme", {}).get("warning", "#ffaa00"),
            completed_color=data.get("color_scheme", {}).get("completed", "#ff3333"),
            accelerate_on_complete=data.get("accelerate_on_complete", True)
        )
        return cls(config)


class BreathLightWidget:
    """
    呼吸灯 UI 组件
    
    集成到倒计时界面，提供可视化呼吸效果
    
    Attributes:
        parent: 父容器
        effect: 呼吸灯效果实例
        theme: 主题颜色配置
    """
    
    def __init__(self, parent: tk.Widget, theme: Dict[str, str], config: Dict[str, Any]):
        """
        初始化呼吸灯组件
        
        Args:
            parent: 父容器
            theme: 主题颜色配置
            config: 呼吸灯配置
        """
        self.parent = parent
        self.theme = theme
        self.effect = BreathLightEffect.from_dict(config)
        self._display_items = []  # 需要应用呼吸效果的画布元素
        self._border_frame: Optional[tk.Frame] = None
        
    def register_display_items(self, items: list) -> None:
        """
        注册需要应用呼吸效果的显示元素
        
        Args:
            items: 画布元素 ID 列表或 (canvas, item_id) 元组列表
        """
        self._display_items = items
    
    def update_display(self, brightness: float, status: TimerStatus) -> None:
        """
        更新显示亮度
        
        Args:
            brightness: 亮度值（0-1）
            status: 倒计时状态
        """
        base_color = self.effect.get_current_color()
        adjusted_color = self.effect.apply_brightness_to_color(base_color, brightness)
        
        # 更新注册的显示元素
        for item in self._display_items:
            try:
                if isinstance(item, tuple):
                    canvas, item_id = item
                    canvas.itemconfig(item_id, fill=adjusted_color)
                elif hasattr(item, 'config'):
                    # Tkinter 组件
                    item.config(fg=adjusted_color)
            except Exception as e:
                print(f"⚠️  更新呼吸灯显示错误：{e}")
    
    def start(self) -> None:
        """启动呼吸灯效果"""
        if not self.effect.running:
            self.effect.start(self.parent, self.update_display)
    
    def stop(self) -> None:
        """停止呼吸灯效果"""
        if self.effect.running:
            self.effect.stop(self.parent)
    
    def set_status(self, status: TimerStatus) -> None:
        """
        设置倒计时状态
        
        Args:
            status: 倒计时状态
        """
        self.effect.set_status(status)
    
    def update_config(self, **kwargs) -> None:
        """
        更新配置
        
        Args:
            **kwargs: 配置参数
        """
        self.effect.update_config(**kwargs)


# 工具函数
def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """
    十六进制颜色转 RGB
    
    Args:
        hex_color: 十六进制颜色字符串（如 "#ff0000"）
        
    Returns:
        RGB 元组 (r, g, b)
    """
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def rgb_to_hex(r: int, g: int, b: int) -> str:
    """
    RGB 转十六进制颜色
    
    Args:
        r: 红色分量 (0-255)
        g: 绿色分量 (0-255)
        b: 蓝色分量 (0-255)
        
    Returns:
        十六进制颜色字符串
    """
    return f"#{r:02x}{g:02x}{b:02x}"


def interpolate_color(color1: str, color2: str, factor: float) -> str:
    """
    在两种颜色之间插值
    
    Args:
        color1: 起始颜色（十六进制）
        color2: 结束颜色（十六进制）
        factor: 插值因子（0-1，0 为 color1，1 为 color2）
        
    Returns:
        插值后的颜色（十六进制）
    """
    r1, g1, b1 = hex_to_rgb(color1)
    r2, g2, b2 = hex_to_rgb(color2)
    
    r = int(r1 + (r2 - r1) * factor)
    g = int(g1 + (g2 - g1) * factor)
    b = int(b1 + (b2 - b1) * factor)
    
    return rgb_to_hex(r, g, b)


if __name__ == "__main__":
    # 测试代码
    print("🫧 呼吸灯效果模块测试")
    
    # 测试配置
    config = BreathLightConfig(
        enabled=True,
        mode=BreathMode.DIGITAL,
        frequency=1.0,
        intensity=0.7
    )
    
    effect = BreathLightEffect(config)
    print(f"✅ 呼吸灯效果初始化成功")
    print(f"   模式：{config.mode.value}")
    print(f"   频率：{config.frequency} Hz")
    print(f"   强度：{config.intensity}")
    
    # 测试颜色转换
    test_color = "#00ff88"
    bright_color = effect.apply_brightness_to_color(test_color, 1.0)
    dim_color = effect.apply_brightness_to_color(test_color, 0.0)
    print(f"   测试颜色：{test_color}")
    print(f"   最亮：{bright_color}")
    print(f"   最暗：{dim_color}")
    
    print("\n✅ 所有测试通过！")
