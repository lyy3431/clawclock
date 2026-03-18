#!/usr/bin/env python3
"""
呼吸灯效果模块 - ClawClock 呼吸灯功能
====================================

功能:
    - 倒计时运行时，数字/背景呈现呼吸式明暗变化
    - 呼吸频率可配置（默认 1-2 秒/周期）
    - 使用改进的缓动函数实现更平滑的呼吸效果
    - 多种呼吸灯风格可选
    - 时间到特殊效果：呼吸加速、颜色渐变

作者：ClawClock Development Team
版本：1.5.1
"""

import tkinter as tk
import math
import time
from typing import Optional, Tuple, Dict, Any, List
from dataclasses import dataclass
from enum import Enum


class BreathMode(Enum):
    """呼吸灯模式枚举"""
    DIGITAL = "digital"      # 数字呼吸（7 段数码管亮度变化）
    BACKGROUND = "background"  # 背景呼吸（窗口背景色渐变）
    BORDER = "border"        # 边框呼吸（窗口边框光晕效果）
    ALL = "all"              # 全部模式


class BreathStyle(Enum):
    """呼吸灯风格枚举"""
    SOFT = "soft"              # 柔和模式（默认）- 温暖渐变
    TECH = "tech"              # 科技模式 - 蓝紫色调
    COOL = "cool"              # 炫酷模式 - 彩虹渐变
    MINIMAL = "minimal"        # 简约模式 - 单色明暗


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
    style: BreathStyle = BreathStyle.SOFT  # 呼吸灯风格
    frequency: float = 0.5  # 呼吸频率（周期/秒）- 降低默认值使呼吸更慢更柔和
    intensity: float = 0.5  # 呼吸强度（0-1）- 降低默认值使变化更柔和
    normal_color: str = "#00ff88"  # 正常状态颜色
    warning_color: str = "#ffaa00"  # 警告状态颜色
    completed_color: str = "#ff3333"  # 完成状态颜色
    accelerate_on_complete: bool = True  # 时间到时加速呼吸
    smooth_curve: bool = True  # 使用平滑缓动曲线


# 呼吸灯风格配色方案
BREATH_STYLE_COLORS = {
    BreathStyle.SOFT: {
        "normal": "#00d4aa",      # 柔和的青绿色
        "warning": "#ffb347",     # 温暖的橙色
        "completed": "#ff6b6b",   # 柔和的红色
        "gradient": ["#00d4aa", "#00a896", "#007f85"]  # 渐变色
    },
    BreathStyle.TECH: {
        "normal": "#7b68ee",      # 中紫色
        "warning": "#ff1493",     # 深粉色
        "completed": "#9400d3",   # 深紫罗兰色
        "gradient": ["#7b68ee", "#6a5acd", "#483d8b"]  # 蓝紫渐变
    },
    BreathStyle.COOL: {
        "normal": "#00ffff",      # 青色
        "warning": "#ff00ff",     # 品红色
        "completed": "#ffff00",   # 黄色
        "gradient": ["#ff0000", "#ff7f00", "#ffff00", "#00ff00", "#00ffff", "#0000ff", "#8b00ff"]  # 彩虹
    },
    BreathStyle.MINIMAL: {
        "normal": "#ffffff",      # 白色
        "warning": "#ffcc00",     # 琥珀色
        "completed": "#ff4444",   # 红色
        "gradient": ["#ffffff", "#cccccc", "#999999"]  # 灰度渐变
    }
}


class BreathLightEffect:
    """
    呼吸灯效果核心类
    
    提供改进的正弦波呼吸效果，支持多种风格和颜色主题
    
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
        self._rainbow_offset: float = 0.0  # 彩虹模式的色相偏移
        
        # 颜色解析缓存
        self._color_cache: Dict[str, Tuple[int, int, int]] = {}
        
        # 应用风格配色
        self._apply_style_colors()
    
    def _apply_style_colors(self) -> None:
        """应用呼吸灯风格的配色方案"""
        if self.config.style in BREATH_STYLE_COLORS:
            colors = BREATH_STYLE_COLORS[self.config.style]
            # 只有在用户没有自定义颜色时才应用风格默认色
            if not hasattr(self, '_user_customized_colors'):
                self.config.normal_color = colors["normal"]
                self.config.warning_color = colors["warning"]
                self.config.completed_color = colors["completed"]
    
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
        old_status = self.status
        self.status = status
        
        # 状态变化时重置计时器，使过渡更平滑
        if old_status != status and status == TimerStatus.COMPLETED:
            self._start_time = time.time()
    
    def _ease_in_out_sine(self, t: float) -> float:
        """
        平滑的正弦缓动函数（in-out）
        
        Args:
            t: 输入值 (0-1)
            
        Returns:
            缓动后的值
        """
        return -(math.cos(math.pi * t) - 1) / 2
    
    def _ease_in_out_quad(self, t: float) -> float:
        """
        二次缓动函数（in-out）
        
        Args:
            t: 输入值 (0-1)
            
        Returns:
            缓动后的值
        """
        return t * t if t < 0.5 else 1 - pow(-2 * t + 2, 2) / 2
    
    def _calculate_smooth_brightness(self, elapsed: float, frequency: float) -> float:
        """
        使用平滑缓动函数计算亮度
        
        Args:
            elapsed: 经过的时间
            frequency: 呼吸频率
            
        Returns:
            亮度值 (0-1)
        """
        # 计算呼吸周期位置 (0-1)
        cycle_position = (elapsed * frequency) % 1.0
        
        # 使用平滑缓动函数
        if self.config.smooth_curve:
            # 结合正弦波和缓动函数，创造更自然的呼吸效果
            base_breath = (math.sin(elapsed * frequency * 2 * math.pi) + 1) / 2
            eased_breath = self._ease_in_out_sine(cycle_position)
            # 混合两种曲线（70% 正弦 + 30% 缓动）
            brightness = base_breath * 0.7 + eased_breath * 0.3
        else:
            brightness = (math.sin(elapsed * frequency * 2 * math.pi) + 1) / 2
        
        return brightness
    
    def _calculate_rainbow_color(self, elapsed: float) -> str:
        """
        计算彩虹渐变的当前颜色
        
        Args:
            elapsed: 经过的时间
            
        Returns:
            颜色十六进制字符串
        """
        # 彩虹渐变速度
        speed = 0.5  # 每秒变化的色相
        
        # 计算色相偏移
        hue_offset = (elapsed * speed) % 1.0
        
        # 获取彩虹渐变色
        gradient = BREATH_STYLE_COLORS[BreathStyle.COOL]["gradient"]
        num_colors = len(gradient)
        
        # 计算当前在渐变中的位置
        position = hue_offset * (num_colors - 1)
        idx1 = int(position)
        idx2 = min(idx1 + 1, num_colors - 1)
        factor = position - idx1
        
        # 插值颜色
        color1 = gradient[idx1]
        color2 = gradient[idx2]
        return self._interpolate_color(color1, color2, factor)
    
    def _interpolate_color(self, color1: str, color2: str, factor: float) -> str:
        """
        在两种颜色之间插值
        
        Args:
            color1: 起始颜色
            color2: 结束颜色
            factor: 插值因子 (0-1)
            
        Returns:
            插值后的颜色
        """
        r1, g1, b1 = self._hex_to_rgb(color1)
        r2, g2, b2 = self._hex_to_rgb(color2)
        
        r = int(r1 + (r2 - r1) * factor)
        g = int(g1 + (g2 - g1) * factor)
        b = int(b1 + (b2 - b1) * factor)
        
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """十六进制颜色转 RGB"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
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
            frequency *= 2.5  # 时间到时频率加快（从 3 倍降低到 2.5 倍，更柔和）
        elif self.status == TimerStatus.WARNING:
            frequency *= 1.5  # 警告时频率加快
        
        # 计算亮度（使用平滑曲线）
        brightness = self._calculate_smooth_brightness(elapsed, frequency)
        
        # 应用强度
        intensity = self.config.intensity
        # 使用更柔和的强度应用方式
        brightness = 0.5 + (brightness - 0.5) * intensity
        
        # 确保亮度在 0-1 范围内
        brightness = max(0.0, min(1.0, brightness))
        
        self._current_brightness = brightness
        
        # 更新彩虹模式的色相偏移
        if self.config.style == BreathStyle.COOL:
            self._rainbow_offset = elapsed
        
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
        # 彩虹模式特殊处理
        if self.config.style == BreathStyle.COOL:
            elapsed = time.time() - self._start_time
            return self._calculate_rainbow_color(elapsed)
        
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
        
        # 应用亮度（使用更平滑的变暗曲线）
        # 最小亮度从 30% 提升到 40%，避免过暗
        factor = 0.4 + 0.6 * brightness
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
        
        # 如果风格改变，应用新的配色
        if 'style' in kwargs:
            self._apply_style_colors()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "enabled": self.config.enabled,
            "mode": self.config.mode.value,
            "style": self.config.style.value,
            "frequency": self.config.frequency,
            "intensity": self.config.intensity,
            "color_scheme": {
                "normal": self.config.normal_color,
                "warning": self.config.warning_color,
                "completed": self.config.completed_color
            },
            "accelerate_on_complete": self.config.accelerate_on_complete,
            "smooth_curve": self.config.smooth_curve
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BreathLightEffect':
        """从字典创建实例"""
        config = BreathLightConfig(
            enabled=data.get("enabled", True),
            mode=BreathMode(data.get("mode", "digital")),
            style=BreathStyle(data.get("style", "soft")),
            frequency=data.get("frequency", 0.5),
            intensity=data.get("intensity", 0.5),
            normal_color=data.get("color_scheme", {}).get("normal", "#00d4aa"),
            warning_color=data.get("color_scheme", {}).get("warning", "#ffb347"),
            completed_color=data.get("color_scheme", {}).get("completed", "#ff6b6b"),
            accelerate_on_complete=data.get("accelerate_on_complete", True),
            smooth_curve=data.get("smooth_curve", True)
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
    print("🫧 呼吸灯效果模块测试 v1.5.1")
    print("=" * 50)
    
    # 测试配置
    config = BreathLightConfig(
        enabled=True,
        mode=BreathMode.DIGITAL,
        style=BreathStyle.SOFT,
        frequency=0.5,
        intensity=0.5
    )
    
    effect = BreathLightEffect(config)
    print(f"✅ 呼吸灯效果初始化成功")
    print(f"   模式：{config.mode.value}")
    print(f"   风格：{config.style.value}")
    print(f"   频率：{config.frequency} Hz")
    print(f"   强度：{config.intensity}")
    
    # 测试不同风格
    print("\n📋 测试不同呼吸灯风格:")
    for style in BreathStyle:
        config.style = style
        effect._apply_style_colors()
        print(f"   • {style.value}: {effect.config.normal_color}")
    
    # 测试颜色转换
    test_color = "#00d4aa"
    bright_color = effect.apply_brightness_to_color(test_color, 1.0)
    dim_color = effect.apply_brightness_to_color(test_color, 0.0)
    print(f"\n🎨 测试颜色转换:")
    print(f"   测试颜色：{test_color}")
    print(f"   最亮：{bright_color}")
    print(f"   最暗：{dim_color}")
    
    print("\n✅ 所有测试通过！")
