# ClawClock 呼吸灯效果模块
"""
提供呼吸灯动画效果
"""
import math
from typing import Dict, Any, Optional, Callable
from enum import Enum
from dataclasses import dataclass, field

class BreathStyle(Enum):
    """呼吸灯风格"""
    SOFT = "soft"        # 柔和模式
    TECH = "tech"        # 科技模式
    COOL = "cool"        # 炫酷模式
    MINIMAL = "minimal"  # 简约模式


class BreathMode(Enum):
    """呼吸灯显示模式"""
    DIGITAL = "digital"       # 数字显示
    BACKGROUND = "background" # 背景
    BORDER = "border"         # 边框
    ALL = "all"              # 全部


class TimerStatus(Enum):
    """倒计时状态"""
    NORMAL = "normal"       # 正常
    WARNING = "warning"     # 警告
    COMPLETED = "completed" # 完成


@dataclass
class BreathLightConfig:
    """呼吸灯配置数据类"""
    enabled: bool = True
    mode: BreathMode = BreathMode.DIGITAL
    style: BreathStyle = BreathStyle.SOFT
    frequency: float = 0.5  # Hz
    intensity: float = 0.5  # 0-1
    normal_color: str = "#00d4aa"      # 正常状态颜色
    warning_color: str = "#ffb347"     # 警告状态颜色
    completed_color: str = "#ff6b6b"   # 完成状态颜色
    accelerate_on_complete: bool = True
    smooth_curve: bool = True


# 风格配色方案
BREATH_STYLE_COLORS = {
    BreathStyle.SOFT: {
        "normal": "#00d4aa",
        "warning": "#ffb347",
        "completed": "#ff6b6b",
        "gradient": ["#00d4aa", "#00a896", "#007f85"]
    },
    BreathStyle.TECH: {
        "normal": "#4d4dff",
        "warning": "#ff4d4d",
        "completed": "#ff99cc",
        "gradient": ["#4d4dff", "#0099ff", "#00ccff"]
    },
    BreathStyle.COOL: {
        "normal": "#00ff88",
        "warning": "#ffcc00",
        "completed": "#ff3333",
        "gradient": ["#00ff88", "#00ccff", "#ff00ff"]
    },
    BreathStyle.MINIMAL: {
        "normal": "#ffffff",
        "warning": "#ffaa00",
        "completed": "#ff3333",
        "gradient": ["#ffffff", "#eeeeee", "#dddddd"]
    }
}


def hex_to_rgb(hex_color: str) -> tuple:
    """十六进制颜色转RGB"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def rgb_to_hex(r: int, g: int, b: int) -> str:
    """RGB转十六进制颜色"""
    return '#{:02x}{:02x}{:02x}'.format(max(0, min(255, r)), 
                                         max(0, min(255, g)), 
                                         max(0, min(255, b)))


def interpolate_color(color1: str, color2: str, factor: float) -> str:
    """颜色插值"""
    r1, g1, b1 = hex_to_rgb(color1)
    r2, g2, b2 = hex_to_rgb(color2)
    
    r = int(r1 + (r2 - r1) * factor)
    g = int(g1 + (g2 - g1) * factor)
    b = int(b1 + (b2 - b1) * factor)
    
    return rgb_to_hex(r, g, b)


def ease_in_out_sine(x: float) -> float:
    """正弦缓动函数"""
    return -(math.cos(math.pi * x) - 1) / 2


class BreathLightEffect:
    """呼吸灯效果类"""
    
    def __init__(self, config: Optional[BreathLightConfig] = None):
        """
        初始化呼吸灯效果
        
        Args:
            config: 呼吸灯配置，None 则使用默认配置
        """
        self.config = config if config is not None else BreathLightConfig()
        self._phase: float = 0.0
        self._current_brightness: float = 0.5
        self._current_status: TimerStatus = TimerStatus.NORMAL
        self._style_colors: Dict[str, str] = BREATH_STYLE_COLORS.get(
            self.config.style, BREATH_STYLE_COLORS[BreathStyle.SOFT]
        )
        self._acceleration_factor: float = 1.0
    
    def start(self, root, callback: Callable[[str], None]) -> None:
        """开始呼吸灯效果"""
        self._phase = 0.0
        self._acceleration_factor = 1.0
    
    def stop(self, root) -> None:
        """停止呼吸灯效果"""
        pass
    
    def set_status(self, status: TimerStatus) -> None:
        """设置倒计时状态"""
        self._current_status = status
        # 状态切换时重置相位，保证过渡平滑
        self._phase = 0.0
    
    def get_current_color(self) -> str:
        """获取当前颜色"""
        if not self.config.enabled:
            return self._get_base_color()
        
        # 获取目标颜色
        base_color = self._get_base_color()
        
        # 应用亮度
        return self.apply_brightness_to_color(base_color, self._current_brightness)
    
    def apply_brightness_to_color(self, color: str, brightness: float) -> str:
        """将亮度应用到颜色上"""
        r, g, b = hex_to_rgb(color)
        
        # 调整亮度
        factor = brightness * self.config.intensity * 2
        r = int(r * factor)
        g = int(g * factor)
        b = int(b * factor)
        
        return rgb_to_hex(r, g, b)
    
    def update(self, dt: float) -> str:
        """
        更新呼吸灯效果
        
        Args:
            dt: 时间增量（秒）
            
        Returns:
            当前颜色
        """
        if not self.config.enabled:
            return self._get_base_color()
        
        # 计算相位
        self._phase += dt * self.config.frequency * self._acceleration_factor * 2 * math.pi
        
        # 计算亮度（0-1）
        if self.config.smooth_curve:
            sine_value = math.sin(self._phase)
            self._current_brightness = ease_in_out_sine((sine_value + 1) / 2)
        else:
            self._current_brightness = (math.sin(self._phase) + 1) / 2
        
        # 时间到时加速
        if self._current_status == TimerStatus.COMPLETED and self.config.accelerate_on_complete:
            self._acceleration_factor = 2.5
        else:
            self._acceleration_factor = 1.0
        
        return self.get_current_color()
    
    def _get_base_color(self) -> str:
        """获取基础颜色"""
        if self._current_status == TimerStatus.COMPLETED:
            return self.config.completed_color
        elif self._current_status == TimerStatus.WARNING:
            return self.config.warning_color
        else:
            return self.config.normal_color
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BreathLightEffect':
        """从字典创建效果实例"""
        config_dict = data.get("config", {})
        config = BreathLightConfig(**config_dict)
        effect = cls(config)
        
        if "status" in data:
            try:
                effect._current_status = TimerStatus(data["status"])
            except ValueError:
                pass
        
        return effect
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "config": {
                "enabled": self.config.enabled,
                "mode": self.config.mode.value,
                "style": self.config.style.value,
                "frequency": self.config.frequency,
                "intensity": self.config.intensity,
                "normal_color": self.config.normal_color,
                "warning_color": self.config.warning_color,
                "completed_color": self.config.completed_color,
                "accelerate_on_complete": self.config.accelerate_on_complete,
                "smooth_curve": self.config.smooth_curve
            },
            "status": self._current_status.value
        }


def create_breath_light_effect(style: str = "soft", **kwargs) -> BreathLightEffect:
    """
    创建呼吸灯效果
    
    Args:
        style: 风格名称
        **kwargs: 其他配置参数
        
    Returns:
        BreathLightEffect 实例
    """
    style_map = {
        "soft": BreathStyle.SOFT,
        "tech": BreathStyle.TECH,
        "cool": BreathStyle.COOL,
        "minimal": BreathStyle.MINIMAL
    }
    
    config = BreathLightConfig(style=style_map.get(style, BreathStyle.SOFT), **kwargs)
    return BreathLightEffect(config)
