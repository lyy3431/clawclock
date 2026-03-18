# ClawClock 动画系统模块
"""
提供通用动画效果
"""
import math
from typing import Callable, Any, Dict, Optional


class Animation:
    """基础动画类"""
    
    def __init__(self, duration: float = 1.0, 
                 easing: str = "linear",
                 on_complete: Optional[Callable[[], None]] = None):
        """
        初始化动画
        
        Args:
            duration: 动画持续时间（秒）
            easing: 缓动函数名称
            on_complete: 完成时的回调
        """
        self.duration = duration
        self.easing = easing
        self.on_complete = on_complete
        self._elapsed = 0.0
        self._running = False
        self._value = 0.0
    
    def start(self) -> None:
        """开始动画"""
        self._running = True
        self._elapsed = 0.0
        self._value = self._evaluate(0.0)
    
    def stop(self) -> None:
        """停止动画"""
        self._running = False
        self._value = self._evaluate(1.0) if self._elapsed >= self.duration else 0.0
    
    def reset(self) -> None:
        """重置动画"""
        self._running = False
        self._elapsed = 0.0
        self._value = 0.0
    
    def update(self, dt: float) -> float:
        """
        更新动画
        
        Args:
            dt: 时间增量（秒）
            
        Returns:
            当前动画值（0-1）
        """
        if not self._running:
            return self._value
        
        self._elapsed += dt
        
        if self._elapsed >= self.duration:
            self._running = False
            self._value = self._evaluate(1.0)
            if self.on_complete:
                self.on_complete()
        else:
            t = self._elapsed / self.duration
            self._value = self._evaluate(t)
        
        return self._value
    
    def _evaluate(self, t: float) -> float:
        """评估动画值"""
        easing_funcs = {
            "linear": self._linear,
            "ease_in": self._ease_in,
            "ease_out": self._ease_out,
            "ease_in_out": self._ease_in_out,
            "bounce": self._bounce,
            "elastic": self._elastic
        }
        
        func = easing_funcs.get(self.easing, self._linear)
        return func(t)
    
    def _linear(self, t: float) -> float:
        """线性缓动"""
        return t
    
    def _ease_in(self, t: float) -> float:
        """缓入"""
        return t * t
    
    def _ease_out(self, t: float) -> float:
        """缓出"""
        return t * (2 - t)
    
    def _ease_in_out(self, t: float) -> float:
        """缓入缓出"""
        if t < 0.5:
            return 2 * t * t
        return 1 - math.pow(-2 * t + 2, 2) / 2
    
    def _bounce(self, t: float) -> float:
        """反弹效果"""
        n1 = 7.5625
        d1 = 2.75
        
        if t < 1 / d1:
            return n1 * t * t
        elif t < 2 / d1:
            t -= 1.5 / d1
            return n1 * t * t + 0.75
        elif t < 2.5 / d1:
            t -= 2.25 / d1
            return n1 * t * t + 0.9375
        else:
            t -= 2.625 / d1
            return n1 * t * t + 0.984375
    
    def _elastic(self, t: float) -> float:
        """弹性效果"""
        c4 = (2 * math.pi) / 3
        
        if t == 0:
            return 0
        elif t == 1:
            return 1
        else:
            return -math.pow(2, 10 * t - 10) * math.sin((t * 10 - 10.75) * c4)


class FadeAnimation:
    """淡入淡出动画"""
    
    def __init__(self, start: float = 0.0, end: float = 1.0, 
                 duration: float = 1.0, easing: str = "ease_out"):
        """
        初始化淡入淡出动画
        
        Args:
            start: 起始透明度
            end: 结束透明度
            duration: 持续时间（秒）
            easing: 缓动函数
        """
        self.start = start
        self.end = end
        self.animation = Animation(duration, easing)
        self._current = start
    
    def start(self) -> None:
        """开始动画"""
        self.animation.start()
    
    def update(self, dt: float) -> float:
        """
        更新动画
        
        Args:
            dt: 时间增量（秒）
            
        Returns:
            当前透明度
        """
        t = self.animation.update(dt)
        self._current = self.start + (self.end - self.start) * t
        return self._current
    
    def get_value(self) -> float:
        """获取当前值"""
        return self._current


class ColorAnimation:
    """颜色渐变动画"""
    
    def __init__(self, colors: list, duration: float = 2.0, 
                 easing: str = "linear"):
        """
        初始化颜色渐变动画
        
        Args:
            colors: 颜色列表
            duration: 完整循环持续时间（秒）
            easing: 缓动函数
        """
        self.colors = colors
        self.duration = duration
        self.animation = Animation(duration, easing)
        self._current_color = colors[0] if colors else "#ffffff"
    
    def start(self) -> None:
        """开始动画"""
        self.animation.start()
    
    def update(self, dt: float) -> str:
        """
        更新动画
        
        Args:
            dt: 时间增量（秒）
            
        Returns:
            当前颜色
        """
        t = self.animation.update(dt)
        
        # 计算当前区间
        num_colors = len(self.colors)
        segment = 1.0 / (num_colors - 1) if num_colors > 1 else 1.0
        
        index = min(int(t / segment), num_colors - 2)
        segment_t = (t - index * segment) / segment
        
        color1 = self.colors[index]
        color2 = self.colors[index + 1]
        
        self._current_color = self._interpolate_color(color1, color2, segment_t)
        
        return self._current_color
    
    def _interpolate_color(self, color1: str, color2: str, factor: float) -> str:
        """颜色插值"""
        def hex_to_rgb(hex_color: str) -> tuple:
            hex_color = hex_color.lstrip('#')
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        def rgb_to_hex(r: int, g: int, b: int) -> str:
            return '#{:02x}{:02x}{:02x}'.format(
                max(0, min(255, r)),
                max(0, min(255, g)),
                max(0, min(255, b))
            )
        
        r1, g1, b1 = hex_to_rgb(color1)
        r2, g2, b2 = hex_to_rgb(color2)
        
        r = int(r1 + (r2 - r1) * factor)
        g = int(g1 + (g2 - g1) * factor)
        b = int(b1 + (b2 - b1) * factor)
        
        return rgb_to_hex(r, g, b)
    
    def get_value(self) -> str:
        """获取当前颜色"""
        return self._current_color


def create_breath_animation(duration: float = 2.0, easing: str = "ease_in_out") -> Animation:
    """
    创建呼吸动画
    
    Args:
        duration: 完整周期持续时间（秒）
        easing: 缓动函数
        
    Returns:
        Animation 实例
    """
    return Animation(duration / 2, easing)
