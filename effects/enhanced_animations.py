#!/usr/bin/env python3
"""
ClawClock - 增强动画效果模块
============================

提供高级动画效果：
- 整点报时动画
- 模式切换过渡动画
- 主题切换淡入淡出
- 秒针平滑移动
- 数字翻页效果
"""

import math
import time
from typing import Callable, Optional, Tuple, List, Any, Dict
from dataclasses import dataclass, field
import tkinter as tk


# ==================== 缓动函数 ====================

class Easing:
    """缓动函数集合"""
    
    @staticmethod
    def linear(t: float) -> float:
        """线性"""
        return t
    
    @staticmethod
    def ease_in_quad(t: float) -> float:
        """二次缓入"""
        return t * t
    
    @staticmethod
    def ease_out_quad(t: float) -> float:
        """二次缓出"""
        return t * (2 - t)
    
    @staticmethod
    def ease_in_out_quad(t: float) -> float:
        """二次缓入缓出"""
        if t < 0.5:
            return 2 * t * t
        return -1 + (4 - 2 * t) * t
    
    @staticmethod
    def ease_in_cubic(t: float) -> float:
        """三次缓入"""
        return t * t * t
    
    @staticmethod
    def ease_out_cubic(t: float) -> float:
        """三次缓出"""
        return 1 - pow(1 - t, 3)
    
    @staticmethod
    def ease_in_out_cubic(t: float) -> float:
        """三次缓入缓出"""
        if t < 0.5:
            return 4 * t * t * t
        return 1 - pow(-2 * t + 2, 3) / 2
    
    @staticmethod
    def ease_out_bounce(t: float) -> float:
        """弹跳缓出"""
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
    
    @staticmethod
    def ease_in_out_sine(t: float) -> float:
        """正弦缓入缓出"""
        return -(math.cos(math.pi * t) - 1) / 2
    
    @staticmethod
    def ease_out_elastic(t: float) -> float:
        """弹性缓出"""
        if t == 0:
            return 0
        if t == 1:
            return 1
        c4 = (2 * math.pi) / 3
        return pow(2, -10 * t) * math.sin((t * 10 - 0.75) * c4) + 1


# ==================== 动画数据类 ====================

@dataclass
class AnimationState:
    """动画状态"""
    running: bool = False
    progress: float = 0.0  # 0.0 - 1.0
    value: float = 0.0
    start_time: float = 0.0
    duration: float = 1.0
    easing: str = "linear"
    on_complete: Optional[Callable] = None
    on_update: Optional[Callable[[float], None]] = None


@dataclass
class HourChimeEffect:
    """整点报时效果数据"""
    enabled: bool = True
    scale_factor: float = 1.0
    glow_intensity: float = 0.0
    particle_count: int = 20
    particles: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class TransitionEffect:
    """过渡效果数据"""
    from_mode: str = ""
    to_mode: str = ""
    progress: float = 0.0
    fade_alpha: float = 1.0


@dataclass
class FlipAnimation:
    """翻页动画数据"""
    current_digit: str = "0"
    next_digit: str = "0"
    flip_progress: float = 0.0  # 0.0 - 1.0
    flip_angle: float = 0.0  # 弧度
    is_flipping: bool = False


# ==================== 动画管理器 ====================

class AnimationManager:
    """动画管理器"""
    
    def __init__(self):
        self.animations: Dict[str, AnimationState] = {}
        self.active_effects: Dict[str, Any] = {}
    
    def create_animation(self, name: str, duration: float = 1.0,
                        easing: str = "linear",
                        on_complete: Optional[Callable] = None,
                        on_update: Optional[Callable[[float], None]] = None) -> AnimationState:
        """创建动画"""
        anim = AnimationState(
            running=False,
            progress=0.0,
            value=0.0,
            duration=duration,
            easing=easing,
            on_complete=on_complete,
            on_update=on_update
        )
        self.animations[name] = anim
        return anim
    
    def start_animation(self, name: str) -> None:
        """启动动画"""
        if name not in self.animations:
            return
        anim = self.animations[name]
        anim.running = True
        anim.progress = 0.0
        anim.start_time = time.time()
    
    def update_animation(self, name: str) -> Optional[float]:
        """更新动画"""
        if name not in self.animations:
            return None
        
        anim = self.animations[name]
        if not anim.running:
            return anim.value
        
        # 计算进度
        elapsed = time.time() - anim.start_time
        anim.progress = min(elapsed / anim.duration, 1.0)
        
        # 应用缓动
        t = anim.progress
        if anim.easing == "linear":
            anim.value = Easing.linear(t)
        elif anim.easing == "ease_in_quad":
            anim.value = Easing.ease_in_quad(t)
        elif anim.easing == "ease_out_quad":
            anim.value = Easing.ease_out_quad(t)
        elif anim.easing == "ease_in_out_quad":
            anim.value = Easing.ease_in_out_quad(t)
        elif anim.easing == "ease_out_bounce":
            anim.value = Easing.ease_out_bounce(t)
        elif anim.easing == "ease_in_out_sine":
            anim.value = Easing.ease_in_out_sine(t)
        else:
            anim.value = t
        
        # 回调
        if anim.on_update:
            anim.on_update(anim.value)
        
        # 完成检查
        if anim.progress >= 1.0:
            anim.running = False
            if anim.on_complete:
                anim.on_complete()
        
        return anim.value
    
    def is_animation_running(self, name: str) -> bool:
        """检查动画是否运行中"""
        return name in self.animations and self.animations[name].running


# ==================== 整点报时动画 ====================

class HourChimeAnimation:
    """整点报时动画"""
    
    def __init__(self, canvas: tk.Canvas, center_x: int = 150, center_y: int = 150):
        self.canvas = canvas
        self.center_x = center_x
        self.center_y = center_y
        self.manager = AnimationManager()
        self.effect = HourChimeEffect()
        
        # 创建动画
        self.manager.create_animation(
            "scale",
            duration=0.5,
            easing="ease_out_quad",
            on_update=self._on_scale_update
        )
        self.manager.create_animation(
            "glow",
            duration=1.0,
            easing="ease_in_out_sine",
            on_update=self._on_glow_update
        )
        self.manager.create_animation(
            "particles",
            duration=1.5,
            easing="ease_out_quad",
            on_update=self._on_particles_update
        )
        
        # 粒子系统
        self.particles = []
    
    def trigger(self, hour: int) -> None:
        """触发整点报时动画"""
        if not self.effect.enabled:
            return
        
        # 启动所有动画
        self.manager.start_animation("scale")
        self.manager.start_animation("glow")
        self.manager.start_animation("particles")
        
        # 创建粒子
        self._create_particles()
    
    def _create_particles(self) -> None:
        """创建粒子"""
        self.particles = []
        for i in range(self.effect.particle_count):
            angle = (2 * math.pi * i) / self.effect.particle_count
            self.particles.append({
                "angle": angle,
                "distance": 0,
                "speed": 50 + i * 2,
                "size": 2 + (i % 3),
                "color": f"#ff{hex(i * 8)[2:]}6b"
            })
    
    def _on_scale_update(self, value: float) -> None:
        """缩放更新回调"""
        self.effect.scale_factor = 1.0 + 0.2 * (1 - value)
    
    def _on_glow_update(self, value: float) -> None:
        """辉光更新回调"""
        self.effect.glow_intensity = value * 0.5
    
    def _on_particles_update(self, value: float) -> None:
        """粒子更新回调"""
        for particle in self.particles:
            particle["distance"] += particle["speed"] * 0.016
    
    def update(self) -> None:
        """更新动画"""
        self.manager.update_animation("scale")
        self.manager.update_animation("glow")
        self.manager.update_animation("particles")
    
    def is_active(self) -> bool:
        """检查是否有动画运行"""
        return (self.manager.is_animation_running("scale") or
                self.manager.is_animation_running("glow") or
                self.manager.is_animation_running("particles"))
    
    def draw(self, radius: float = 120) -> None:
        """绘制报时效果"""
        if not self.is_active():
            return
        
        # 绘制辉光
        if self.effect.glow_intensity > 0.01:
            glow_radius = radius * (1 + self.effect.glow_intensity)
            self.canvas.create_oval(
                self.center_x - glow_radius,
                self.center_y - glow_radius,
                self.center_x + glow_radius,
                self.center_y + glow_radius,
                outline=f"#ff6b6b{int(self.effect.glow_intensity * 255):02x}",
                width=3
            )
        
        # 绘制粒子
        for particle in self.particles:
            if particle["distance"] > radius * 2:
                continue
            
            x = self.center_x + math.cos(particle["angle"]) * particle["distance"]
            y = self.center_y + math.sin(particle["angle"]) * particle["distance"]
            
            self.canvas.create_oval(
                x - particle["size"],
                y - particle["size"],
                x + particle["size"],
                y + particle["size"],
                fill=particle["color"],
                outline=""
            )


# ==================== 模式切换动画 ====================

class ModeTransitionAnimation:
    """模式切换过渡动画"""
    
    def __init__(self, canvas: tk.Canvas, width: int = 600, height: int = 500):
        self.canvas = canvas
        self.width = width
        self.height = height
        self.manager = AnimationManager()
        self.transition = TransitionEffect()
        
        # 创建动画
        self.manager.create_animation(
            "fade",
            duration=0.3,
            easing="ease_in_out_quad"
        )
        self.manager.create_animation(
            "slide",
            duration=0.4,
            easing="ease_out_cubic"
        )
    
    def start_transition(self, from_mode: str, to_mode: str) -> None:
        """开始模式切换"""
        self.transition.from_mode = from_mode
        self.transition.to_mode = to_mode
        self.transition.progress = 0.0
        self.transition.fade_alpha = 1.0
        
        self.manager.start_animation("fade")
        self.manager.start_animation("slide")
    
    def update(self) -> float:
        """更新动画"""
        self.manager.update_animation("fade")
        slide_value = self.manager.update_animation("slide") or 0.0
        
        # 计算淡入淡出
        fade_anim = self.manager.animations.get("fade")
        if fade_anim:
            if fade_anim.progress < 0.5:
                self.transition.fade_alpha = 1.0 - fade_anim.value * 2
            else:
                self.transition.fade_alpha = (fade_anim.value - 0.5) * 2
        
        self.transition.progress = slide_value
        return slide_value
    
    def is_active(self) -> bool:
        """检查是否正在切换"""
        return (self.manager.is_animation_running("fade") or
                self.manager.is_animation_running("slide"))
    
    def draw_overlay(self) -> Optional[int]:
        """绘制过渡遮罩"""
        if not self.is_active():
            return None
        
        alpha = int(self.transition.fade_alpha * 255)
        if alpha > 0:
            return self.canvas.create_rectangle(
                0, 0, self.width, self.height,
                fill=f"#000000{alpha:02x}",
                outline=""
            )
        return None


# ==================== 主题切换动画 ====================

class ThemeTransitionAnimation:
    """主题切换淡入淡出动画"""
    
    def __init__(self, canvas: tk.Canvas, width: int = 600, height: int = 500):
        self.canvas = canvas
        self.width = width
        self.height = height
        self.manager = AnimationManager()
        
        # 创建动画
        self.manager.create_animation(
            "theme_fade",
            duration=0.4,
            easing="ease_in_out_sine"
        )
        
        self.current_alpha = 0.0
    
    def start_transition(self) -> None:
        """开始主题切换"""
        self.manager.start_animation("theme_fade")
        self.current_alpha = 0.0
    
    def update(self) -> float:
        """更新动画"""
        value = self.manager.update_animation("theme_fade")
        if value is not None:
            # 先淡出再淡入
            if self.manager.animations["theme_fade"].progress < 0.5:
                self.current_alpha = value * 2
            else:
                self.current_alpha = 2 - value * 2
        return self.current_alpha
    
    def is_active(self) -> bool:
        """检查是否正在切换"""
        return self.manager.is_animation_running("theme_fade")
    
    def draw_overlay(self) -> Optional[int]:
        """绘制过渡遮罩"""
        if not self.is_active():
            return None
        
        alpha = int(self.current_alpha * 255)
        if alpha > 0:
            return self.canvas.create_rectangle(
                0, 0, self.width, self.height,
                fill=f"#000000{alpha:02x}",
                outline=""
            )
        return None


# ==================== 秒针平滑动画 ====================

class SmoothSecondHandAnimation:
    """秒针平滑移动动画"""
    
    def __init__(self):
        self.manager = AnimationManager()
        self.current_second = 0
        self.target_second = 0
        self.smooth_angle = 0.0
        self.target_angle = 0.0
        
        # 创建动画
        self.manager.create_animation(
            "smooth_second",
            duration=0.1,  # 100ms 平滑
            easing="ease_out_quad"
        )
    
    def set_target(self, second: int, include_milliseconds: bool = True) -> None:
        """设置目标位置"""
        self.target_second = second
        self.target_angle = second * 6  # 每秒 6 度
        
        if include_milliseconds:
            # 更平滑的连续移动
            self.manager.start_animation("smooth_second")
        else:
            # 跳秒模式
            self.smooth_angle = self.target_angle
            self.manager.animations["smooth_second"].running = False
    
    def update(self, dt: float = 0.05) -> float:
        """更新动画"""
        if self.manager.is_animation_running("smooth_second"):
            value = self.manager.update_animation("smooth_second") or 0.0
            self.smooth_angle = self._lerp_angle(
                self.smooth_angle,
                self.target_angle,
                value
            )
        else:
            # 连续平滑
            self.smooth_angle = self._lerp_angle(
                self.smooth_angle,
                self.target_angle,
                0.3  # 平滑因子
            )
        
        return self.smooth_angle
    
    def _lerp_angle(self, from_angle: float, to_angle: float, t: float) -> float:
        """角度插值（处理 360 度环绕）"""
        # 确保走最短路径
        diff = to_angle - from_angle
        while diff > 180:
            diff -= 360
        while diff < -180:
            diff += 360
        
        return from_angle + diff * t


# ==================== 数字翻页动画 ====================

class DigitFlipAnimation:
    """数字翻页动画"""
    
    def __init__(self, canvas: tk.Canvas, x: int = 100, y: int = 100,
                 digit_width: int = 60, digit_height: int = 100):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.digit_width = digit_width
        self.digit_height = digit_height
        self.manager = AnimationManager()
        self.flip = FlipAnimation()
        
        # 创建动画
        self.manager.create_animation(
            "flip",
            duration=0.3,
            easing="ease_in_out_sine"
        )
    
    def flip_digit(self, from_digit: str, to_digit: str) -> None:
        """触发翻页"""
        if from_digit == to_digit:
            return
        
        self.flip.current_digit = from_digit
        self.flip.next_digit = to_digit
        self.flip.is_flipping = True
        self.flip.flip_progress = 0.0
        self.flip.flip_angle = 0.0
        
        self.manager.start_animation("flip")
    
    def update(self) -> float:
        """更新动画"""
        value = self.manager.update_animation("flip")
        if value is not None:
            self.flip.flip_progress = value
            self.flip.flip_angle = value * math.pi  # 0 到 180 度
            
            if value >= 1.0:
                self.flip.is_flipping = False
                self.flip.current_digit = self.flip.next_digit
        
        return value or 0.0
    
    def is_flipping(self) -> bool:
        """检查是否正在翻页"""
        return self.manager.is_animation_running("flip")
    
    def draw(self, font_color: str = "#0088ff", 
             bg_color: str = "#1a1a2e") -> None:
        """绘制翻页效果"""
        w = self.digit_width
        h = self.digit_height
        x = self.x
        y = self.y
        
        if self.flip.is_flipping:
            # 绘制翻页效果
            progress = self.flip.flip_progress
            angle = self.flip.flip_angle
            
            # 上半部分（当前数字）
            if progress < 0.5:
                self._draw_digit_half(
                    x, y, w, h,
                    self.flip.current_digit,
                    font_color, bg_color,
                    top=True,
                    fold_progress=progress * 2
                )
            
            # 下半部分（下一个数字）
            if progress > 0:
                self._draw_digit_half(
                    x, y, w, h,
                    self.flip.next_digit,
                    font_color, bg_color,
                    top=False,
                    fold_progress=(1 - progress) * 2
                )
        else:
            # 正常绘制
            self._draw_digit_full(x, y, w, h, self.flip.current_digit, font_color, bg_color)
    
    def _draw_digit_half(self, x: int, y: int, w: int, h: int,
                         digit: str, color: str, bg: str,
                         top: bool = True, fold_progress: float = 0.0) -> None:
        """绘制半张数字（带折叠效果）"""
        # 简化实现：绘制矩形区域
        if top:
            y2 = y + h // 2
            # 绘制上半部分
            self.canvas.create_rectangle(
                x, y, x + w, y2,
                fill=bg, outline=""
            )
            # 绘制数字上半部分（简化）
            self.canvas.create_text(
                x + w // 2, y + h // 4,
                text=digit[0] if digit else "0",
                font=("Arial", h // 2, "bold"),
                fill=color
            )
        else:
            y1 = y + h // 2
            # 绘制下半部分
            self.canvas.create_rectangle(
                x, y1, x + w, y + h,
                fill=bg, outline=""
            )
            # 绘制数字下半部分（简化）
            self.canvas.create_text(
                x + w // 2, y1 + h // 4,
                text=digit[0] if digit else "0",
                font=("Arial", h // 2, "bold"),
                fill=color
            )
    
    def _draw_digit_full(self, x: int, y: int, w: int, h: int,
                         digit: str, color: str, bg: str) -> None:
        """绘制完整数字"""
        self.canvas.create_rectangle(
            x, y, x + w, y + h,
            fill=bg, outline=""
        )
        self.canvas.create_text(
            x + w // 2, y + h // 2,
            text=digit,
            font=("Arial", h // 1.5, "bold"),
            fill=color
        )


# ==================== 动画配置 ====================

@dataclass
class AnimationConfig:
    """动画配置"""
    hour_chime_enabled: bool = True
    hour_chime_volume: float = 0.5
    mode_transition_enabled: bool = True
    mode_transition_duration: float = 0.4
    theme_transition_enabled: bool = True
    theme_transition_duration: float = 0.4
    smooth_second_hand: bool = True
    digit_flip_enabled: bool = True
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AnimationConfig':
        """从字典创建配置"""
        return cls(
            hour_chime_enabled=data.get("hour_chime_enabled", True),
            hour_chime_volume=data.get("hour_chime_volume", 0.5),
            mode_transition_enabled=data.get("mode_transition_enabled", True),
            mode_transition_duration=data.get("mode_transition_duration", 0.4),
            theme_transition_enabled=data.get("theme_transition_enabled", True),
            theme_transition_duration=data.get("theme_transition_duration", 0.4),
            smooth_second_hand=data.get("smooth_second_hand", True),
            digit_flip_enabled=data.get("digit_flip_enabled", True)
        )


# ==================== 工具函数 ====================

def interpolate_color(color1: str, color2: str, t: float) -> str:
    """颜色插值"""
    # 解析颜色
    r1, g1, b1 = int(color1[1:3], 16), int(color1[3:5], 16), int(color1[5:7], 16)
    r2, g2, b2 = int(color2[1:3], 16), int(color2[3:5], 16), int(color2[5:7], 16)
    
    # 插值
    r = int(r1 + (r2 - r1) * t)
    g = int(g1 + (g2 - g1) * t)
    b = int(b1 + (b2 - b1) * t)
    
    return f"#{r:02x}{g:02x}{b:02x}"


def create_gradient_colors(color1: str, color2: str, steps: int) -> List[str]:
    """创建渐变色列表"""
    return [interpolate_color(color1, color2, i / (steps - 1)) for i in range(steps)]


# ==================== 测试代码 ====================

if __name__ == "__main__":
    print("🎨 ClawClock 增强动画效果模块")
    print("=" * 50)
    
    # 测试缓动函数
    print("\n【测试 1】缓动函数")
    print(f"Linear(0.5): {Easing.linear(0.5):.3f}")
    print(f"EaseOutQuad(0.5): {Easing.ease_out_quad(0.5):.3f}")
    print(f"EaseOutBounce(0.5): {Easing.ease_out_bounce(0.5):.3f}")
    
    # 测试动画管理器
    print("\n【测试 2】动画管理器")
    manager = AnimationManager()
    manager.create_animation("test", duration=1.0, easing="ease_out_quad")
    manager.start_animation("test")
    
    for i in range(5):
        value = manager.update_animation("test")
        print(f"  进度 {i*0.2:.1f}: 值 = {value:.3f}")
    
    # 测试配置
    print("\n【测试 3】动画配置")
    config = AnimationConfig()
    print(f"  整点报时：{config.hour_chime_enabled}")
    print(f"  平滑秒针：{config.smooth_second_hand}")
    print(f"  数字翻页：{config.digit_flip_enabled}")
    
    print("\n✅ 所有测试完成！")
