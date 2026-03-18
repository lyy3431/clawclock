#!/usr/bin/env python3
"""
呼吸灯效果模块 - ClawClock 呼吸灯功能 (改进版)
====================================

改进内容:
    - 更柔和的渐变色（降低饱和度，使用平滑过渡）
    - 光晕效果（glow effect）增强视觉美感
    - 改进的亮度曲线（使用余弦波，更平滑）
    - 与主题系统集成
    - 多种预设配色方案

作者：ClawClock Development Team
版本：2.0.0-improved
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
    GLOW = "glow"            # 光晕呼吸（发光效果）
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
    mode: BreathMode = BreathMode.GLOW  # 默认使用光晕模式
    frequency: float = 0.8  # 呼吸频率（周期/秒）- 降低默认值，更舒缓
    intensity: float = 0.6  # 呼吸强度（0-1）- 降低默认值，更柔和
    normal_color: str = "#00d4aa"  # 正常状态颜色 - 更柔和的青绿色
    warning_color: str = "#ff9500"  # 警告状态颜色 - 更柔和的橙色
    completed_color: str = "#ff6b6b"  # 完成状态颜色 - 更柔和的珊瑚红
    accelerate_on_complete: bool = True  # 时间到时加速呼吸
    glow_radius: int = 20  # 光晕半径
    use_gradient: bool = True  # 使用渐变效果


class BreathLightEffect:
    """
    呼吸灯效果核心类（改进版）
    
    提供余弦波呼吸效果，支持多种模式和颜色主题，带有光晕效果
    
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
        self._phase_offset: float = 0.0  # 相位偏移，使呼吸更自然
        
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
        old_status = self.status
        self.status = status
        
        # 状态变化时重置相位，使过渡更平滑
        if old_status != status:
            self._phase_offset = 0.0
    
    def _animate(self, root: tk.Tk, callback: callable) -> None:
        """
        动画循环（使用余弦波，更平滑）
        
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
            frequency *= 2.5  # 时间到时频率加快（从 3 倍降到 2.5 倍，更柔和）
        elif self.status == TimerStatus.WARNING:
            frequency *= 1.3  # 警告时频率加快（从 1.5 倍降到 1.3 倍）
        
        # 使用余弦波计算亮度（比正弦波更平滑）
        # 添加相位偏移使呼吸更自然
        self._phase_offset += 0.01
        brightness = (math.cos(elapsed * frequency * 2 * math.pi + self._phase_offset) + 1) / 2
        
        # 应用强度（降低最小亮度，使暗部更深）
        intensity = self.config.intensity
        min_brightness = 0.2  # 最小亮度 20%
        max_brightness = 0.9  # 最大亮度 90%
        brightness = min_brightness + brightness * (max_brightness - min_brightness)
        
        # 应用强度因子
        brightness = min_brightness + (brightness - min_brightness) * intensity
        
        # 确保亮度在合理范围内
        brightness = max(0.15, min(0.95, brightness))
        
        self._current_brightness = brightness
        
        # 调用回调更新显示
        try:
            callback(brightness, self.status)
        except Exception as e:
            print(f"⚠️  呼吸灯回调错误：{e}")
        
        # 继续动画（60ms 刷新率，更省电）
        self._animation_job = root.after(60, lambda: self._animate(root, callback))
    
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
        将亮度应用到颜色上（改进版：使用更平滑的亮度曲线）
        
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
        
        # 使用平滑的亮度曲线（gamma 校正）
        gamma = 1.5  # gamma 值，使亮度变化更自然
        factor = math.pow(brightness, 1/gamma)
        
        # 应用亮度
        r = int(r * factor)
        g = int(g * factor)
        b = int(b * factor)
        
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def create_glow_color(self, base_color: str, brightness: float, radius: int) -> List[Tuple[str, float]]:
        """
        创建光晕颜色渐变
        
        Args:
            base_color: 基础颜色
            brightness: 亮度
            radius: 光晕半径
            
        Returns:
            颜色渐变列表 [(color, offset), ...]
        """
        gradient = []
        steps = 5
        
        for i in range(steps):
            offset = i / steps
            fade_factor = 1.0 - (offset * 0.8)  # 逐渐变淡
            step_brightness = brightness * fade_factor
            glow_color = self.apply_brightness_to_color(base_color, step_brightness)
            gradient.append((glow_color, offset))
        
        return gradient
    
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
            "accelerate_on_complete": self.config.accelerate_on_complete,
            "glow_radius": self.config.glow_radius,
            "use_gradient": self.config.use_gradient
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BreathLightEffect':
        """从字典创建实例"""
        config = BreathLightConfig(
            enabled=data.get("enabled", True),
            mode=BreathMode(data.get("mode", "glow")),
            frequency=data.get("frequency", 0.8),
            intensity=data.get("intensity", 0.6),
            normal_color=data.get("color_scheme", {}).get("normal", "#00d4aa"),
            warning_color=data.get("color_scheme", {}).get("warning", "#ff9500"),
            completed_color=data.get("color_scheme", {}).get("completed", "#ff6b6b"),
            accelerate_on_complete=data.get("accelerate_on_complete", True),
            glow_radius=data.get("glow_radius", 20),
            use_gradient=data.get("use_gradient", True)
        )
        return cls(config)


class BreathLightWidget:
    """
    呼吸灯 UI 组件（改进版）
    
    集成到倒计时界面，提供可视化呼吸效果，带有光晕
    
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
        self._glow_items = []  # 光晕效果元素
        self._border_frame: Optional[tk.Frame] = None
        
    def register_display_items(self, items: list) -> None:
        """
        注册需要应用呼吸效果的显示元素
        
        Args:
            items: 画布元素 ID 列表或 (canvas, item_id) 元组列表
        """
        self._display_items = items
    
    def register_glow_items(self, items: list) -> None:
        """
        注册需要应用光晕效果的元素
        
        Args:
            items: 画布元素 ID 列表或 (canvas, item_id) 元组列表
        """
        self._glow_items = items
    
    def update_display(self, brightness: float, status: TimerStatus) -> None:
        """
        更新显示亮度（改进版：支持光晕效果）
        
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
                    
                    # 如果启用光晕，更新光晕效果
                    if self.effect.config.use_gradient and item in self._glow_items:
                        self._update_glow_effect(canvas, item_id, base_color, brightness)
                elif hasattr(item, 'config'):
                    # Tkinter 组件
                    item.config(fg=adjusted_color)
            except Exception as e:
                print(f"⚠️  更新呼吸灯显示错误：{e}")
    
    def _update_glow_effect(self, canvas: tk.Canvas, item_id: int, base_color: str, brightness: float) -> None:
        """
        更新光晕效果
        
        Args:
            canvas: 画布
            item_id: 元素 ID
            base_color: 基础颜色
            brightness: 亮度
        """
        try:
            # 获取元素坐标
            coords = canvas.coords(item_id)
            if not coords:
                return
            
            # 计算光晕（简单版本：使用 outline 属性）
            glow_width = int(self.effect.config.glow_radius * brightness)
            glow_color = self.effect.apply_brightness_to_color(base_color, brightness * 0.5)
            
            canvas.itemconfig(item_id, outline=glow_color, width=glow_width)
        except Exception:
            pass
    
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


def create_soft_color(base_color: str, saturation_factor: float = 0.7) -> str:
    """
    创建柔和版本的颜色（降低饱和度）
    
    Args:
        base_color: 基础颜色
        saturation_factor: 饱和度因子（0-1，越小越柔和）
        
    Returns:
        柔和版本的颜色
    """
    r, g, b = hex_to_rgb(base_color)
    
    # 转换为 HSL
    r_norm = r / 255.0
    g_norm = g / 255.0
    b_norm = b / 255.0
    
    max_c = max(r_norm, g_norm, b_norm)
    min_c = min(r_norm, g_norm, b_norm)
    l = (max_c + min_c) / 2.0
    
    if max_c != min_c:
        d = max_c - min_c
        s = d / (2.0 - max_c - min_c) if l > 0.5 else d / (max_c + min_c)
        
        if max_c == r_norm:
            h = (g_norm - b_norm) / d + (6.0 if g_norm < b_norm else 0.0)
        elif max_c == g_norm:
            h = (b_norm - r_norm) / d + 2.0
        else:
            h = (r_norm - g_norm) / d + 4.0
        
        h /= 6.0
        
        # 降低饱和度
        s *= saturation_factor
        
        # 转换回 RGB
        def hue_to_rgb(p, q, t):
            if t < 0: t += 1
            if t > 1: t -= 1
            if t < 1/6: return p + (q - p) * 6 * t
            if t < 1/2: return q
            if t < 2/3: return p + (q - p) * (2/3 - t) * 6
            return p
        
        q = l * (1 + s) if l < 0.5 else l + s - l * s
        p = 2 * l - q
        
        r_norm = hue_to_rgb(p, q, h)
        g_norm = hue_to_rgb(p, q, h + 1/3)
        b_norm = hue_to_rgb(p, q, h + 2/3)
        
        r = int(r_norm * 255)
        g = int(g_norm * 255)
        b = int(b_norm * 255)
    
    return rgb_to_hex(r, g, b)


if __name__ == "__main__":
    # 测试代码
    print("🫧 呼吸灯效果模块测试（改进版）")
    
    # 测试配置
    config = BreathLightConfig(
        enabled=True,
        mode=BreathMode.GLOW,
        frequency=0.8,
        intensity=0.6
    )
    
    effect = BreathLightEffect(config)
    print(f"✅ 呼吸灯效果初始化成功")
    print(f"   模式：{config.mode.value}")
    print(f"   频率：{config.frequency} Hz")
    print(f"   强度：{config.intensity}")
    print(f"   正常颜色：{config.normal_color}")
    print(f"   警告颜色：{config.warning_color}")
    print(f"   完成颜色：{config.completed_color}")
    
    # 测试柔和颜色生成
    print("\n🎨 柔和颜色测试:")
    test_colors = ["#00ff88", "#ffaa00", "#ff3333"]
    for color in test_colors:
        soft = create_soft_color(color, 0.7)
        print(f"   {color} → {soft}")
