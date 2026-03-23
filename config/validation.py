#!/usr/bin/env python3
"""
ClawClock - 配置验证模块
========================

使用 pydantic 验证配置结构，确保配置数据的完整性和类型安全。

功能特性:
    - BreathLightConfig 验证
    - WindowConfig 验证
    - ThemeConfig 验证
    - 完整应用配置验证
"""

from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Dict, List, Optional, Any
from enum import Enum


class BreathStyle(str, Enum):
    """呼吸灯风格枚举"""
    SOFT = "soft"
    TECH = "tech"
    COOL = "cool"
    MINIMAL = "minimal"


class TimerStatus(str, Enum):
    """计时器状态枚举"""
    NORMAL = "normal"
    WARNING = "warning"
    COMPLETED = "completed"


class BreathLightConfig(BaseModel):
    """
    呼吸灯配置验证模型

    Attributes:
        enabled: 是否启用呼吸灯效果
        mode: 模式 (digital/analog)
        style: 风格 (soft/tech/cool/minimal)
        frequency: 频率 (0.0-1.0)
        intensity: 强度 (0.0-1.0)
        accelerate_on_complete: 完成时加速
        smooth_curve: 平滑曲线
    """
    model_config = ConfigDict(
        extra='ignore',  # 忽略额外字段
        str_strip_whitespace=True,  # 字符串去除空白
    )

    enabled: bool = True
    mode: str = Field(default="digital", pattern="^(digital|analog)$")
    style: BreathStyle = BreathStyle.SOFT
    frequency: float = Field(default=0.5, ge=0.0, le=1.0)
    intensity: float = Field(default=0.5, ge=0.0, le=1.0)
    accelerate_on_complete: bool = True
    smooth_curve: bool = True

    @field_validator('frequency', 'intensity', mode='before')
    @classmethod
    def validate_range(cls, v: Any) -> float:
        """验证频率和强度在有效范围内"""
        if isinstance(v, (int, float)):
            return max(0.0, min(1.0, float(v)))
        return 0.5

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "enabled": self.enabled,
            "mode": self.mode,
            "style": self.style.value,
            "frequency": self.frequency,
            "intensity": self.intensity,
            "accelerate_on_complete": self.accelerate_on_complete,
            "smooth_curve": self.smooth_curve
        }


class WindowConfig(BaseModel):
    """
    窗口配置验证模型

    Attributes:
        width: 窗口宽度
        height: 窗口高度
        x: 窗口 X 坐标
        y: 窗口 Y 坐标
        resizable: 是否可调整大小
        always_on_top: 是否窗口置顶
        fullscreen: 是否全屏
    """
    model_config = ConfigDict(
        extra='ignore',
        validate_assignment=True,
    )

    width: int = Field(default=600, ge=400, le=3840)
    height: int = Field(default=500, ge=300, le=2160)
    x: Optional[int] = None
    y: Optional[int] = None
    resizable: bool = True
    always_on_top: bool = False
    fullscreen: bool = False

    @field_validator('width', 'height', mode='before')
    @classmethod
    def validate_dimensions(cls, v: Any) -> int:
        """验证窗口尺寸"""
        if isinstance(v, (int, float)):
            return int(v)
        if isinstance(v, str):
            try:
                return int(v)
            except ValueError:
                pass
        return 600  # 默认值

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "width": self.width,
            "height": self.height,
            "x": self.x,
            "y": self.y,
            "resizable": self.resizable,
            "always_on_top": self.always_on_top,
            "fullscreen": self.fullscreen
        }


class ThemeColorsConfig(BaseModel):
    """
    主题颜色配置验证模型
    """
    model_config = ConfigDict(
        extra='ignore',
        validate_assignment=True,
    )

    background: str = Field(default="#1a1a2e", pattern="^#[0-9a-fA-F]{6}$")
    face: str = Field(default="#16213e", pattern="^#[0-9a-fA-F]{6}$")
    hand: str = Field(default="#e94560", pattern="^#[0-9a-fA-F]{6}$")
    text: str = Field(default="#ffffff", pattern="^#[0-9a-fA-F]{6}$")
    accent: str = Field(default="#0f3460", pattern="^#[0-9a-fA-F]{6}$")
    segment_on: str = Field(default="#ff3333", pattern="^#[0-9a-fA-F]{6}$")
    segment_off: str = Field(default="#331111", pattern="^#[0-9a-fA-F]{6}$")

    @field_validator('background', 'face', 'hand', 'text', 'accent', 'segment_on', 'segment_off', mode='before')
    @classmethod
    def validate_hex_color(cls, v: Any) -> str:
        """验证十六进制颜色格式"""
        if not isinstance(v, str):
            return "#000000"
        v = v.strip()
        if len(v) == 7 and v.startswith('#'):
            try:
                int(v[1:], 16)
                return v.upper() if v.islower() else v
            except ValueError:
                pass
        return "#000000"

    def to_dict(self) -> Dict[str, str]:
        """转换为字典"""
        return {
            "background": self.background,
            "face": self.face,
            "hand": self.hand,
            "text": self.text,
            "accent": self.accent,
            "segment_on": self.segment_on,
            "segment_off": self.segment_off
        }


class ThemeConfig(BaseModel):
    """
    主题配置验证模型

    Attributes:
        name: 主题名称
        display_name: 显示名称
        colors: 颜色配置
    """
    model_config = ConfigDict(
        extra='ignore',
        validate_assignment=True,
    )

    name: str = Field(default="dark")
    display_name: str = Field(default="Dark")
    colors: ThemeColorsConfig = Field(default_factory=ThemeColorsConfig)

    @field_validator('name', 'display_name', mode='before')
    @classmethod
    def validate_string(cls, v: Any) -> str:
        """验证字符串字段"""
        if not isinstance(v, str):
            return str(v) if v is not None else ""
        return v.strip()

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "name": self.name,
            "display_name": self.display_name,
            "colors": self.colors.to_dict()
        }


class AlarmConfig(BaseModel):
    """
    闹钟配置验证模型

    Attributes:
        time: 闹钟时间 (HH:MM 格式)
        enabled: 是否启用
        label: 闹钟标签
        sound: 铃声类型
        repeat_days: 重复日期列表 (0-6)
        snooze_minutes: 小睡时长
    """
    model_config = ConfigDict(
        extra='ignore',
        validate_assignment=True,
    )

    time: str = Field(default="00:00", pattern="^([01]?[0-9]|2[0-3]):[0-5][0-9]$")
    enabled: bool = True
    label: str = ""
    sound: str = "default"
    repeat_days: List[int] = Field(default_factory=list)
    snooze_minutes: int = Field(default=5, ge=1, le=60)

    @field_validator('repeat_days', mode='before')
    @classmethod
    def validate_repeat_days(cls, v: Any) -> List[int]:
        """验证重复日期列表"""
        if not isinstance(v, list):
            return []
        return [day for day in v if isinstance(day, int) and 0 <= day <= 6]

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "time": self.time,
            "enabled": self.enabled,
            "label": self.label,
            "sound": self.sound,
            "repeat_days": self.repeat_days,
            "snooze_minutes": self.snooze_minutes
        }


class AppConfig(BaseModel):
    """
    完整应用配置验证模型

    整合所有子配置模型，提供完整的配置验证。

    Attributes:
        timezone: 时区设置
        display_mode: 显示模式
        window: 窗口配置
        theme: 主题配置
        breath_light: 呼吸灯配置
        alarms: 闹钟列表
    """
    model_config = ConfigDict(
        extra='allow',  # 允许额外字段（向后兼容）
        validate_assignment=True,
    )

    timezone: str = Field(default="Asia/Shanghai")
    display_mode: str = Field(default="digital", pattern="^(analog|digital|stopwatch|timer)$")
    window: WindowConfig = Field(default_factory=WindowConfig)
    theme: ThemeConfig = Field(default_factory=ThemeConfig)
    breath_light: BreathLightConfig = Field(default_factory=BreathLightConfig)
    alarms: List[AlarmConfig] = Field(default_factory=list)

    @field_validator('timezone', mode='before')
    @classmethod
    def validate_timezone(cls, v: Any) -> str:
        """验证时区设置"""
        if not isinstance(v, str):
            return "Asia/Shanghai"
        return v.strip()

    @field_validator('window', mode='before')
    @classmethod
    def validate_window(cls, v: Any) -> WindowConfig:
        """验证窗口配置"""
        if isinstance(v, WindowConfig):
            return v
        if isinstance(v, dict):
            return WindowConfig(**v)
        return WindowConfig()

    @field_validator('theme', mode='before')
    @classmethod
    def validate_theme(cls, v: Any) -> ThemeConfig:
        """验证主题配置"""
        if isinstance(v, ThemeConfig):
            return v
        if isinstance(v, dict):
            return ThemeConfig(**v)
        return ThemeConfig()

    @field_validator('breath_light', mode='before')
    @classmethod
    def validate_breath_light(cls, v: Any) -> BreathLightConfig:
        """验证呼吸灯配置"""
        if isinstance(v, BreathLightConfig):
            return v
        if isinstance(v, dict):
            return BreathLightConfig(**v)
        return BreathLightConfig()

    @field_validator('alarms', mode='before')
    @classmethod
    def validate_alarms(cls, v: Any) -> List[AlarmConfig]:
        """验证闹钟列表"""
        if not isinstance(v, list):
            return []
        result = []
        for alarm in v:
            if isinstance(alarm, AlarmConfig):
                result.append(alarm)
            elif isinstance(alarm, dict):
                try:
                    result.append(AlarmConfig(**alarm))
                except Exception:
                    pass  # 跳过无效的闹钟配置
        return result

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "timezone": self.timezone,
            "display_mode": self.display_mode,
            "window": self.window.to_dict(),
            "theme": self.theme.to_dict(),
            "breath_light": self.breath_light.to_dict(),
            "alarms": [alarm.to_dict() for alarm in self.alarms]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AppConfig':
        """从字典创建配置（带错误处理）"""
        try:
            return cls(**data)
        except Exception as e:
            print(f"⚠️  配置验证失败：{e}，使用默认配置")
            return cls()


def validate_config(data: Dict[str, Any]) -> AppConfig:
    """
    验证配置数据

    Args:
        data: 配置字典

    Returns:
        AppConfig: 验证后的配置对象
    """
    return AppConfig.from_dict(data)


def validate_breath_light_config(data: Dict[str, Any]) -> BreathLightConfig:
    """
    验证呼吸灯配置

    Args:
        data: 呼吸灯配置字典

    Returns:
        BreathLightConfig: 验证后的配置对象
    """
    return BreathLightConfig.from_dict(data) if hasattr(BreathLightConfig, 'from_dict') else BreathLightConfig(**data)


# 导出所有公共类和函数
__all__ = [
    'BreathStyle',
    'TimerStatus',
    'BreathLightConfig',
    'WindowConfig',
    'ThemeColorsConfig',
    'ThemeConfig',
    'AlarmConfig',
    'AppConfig',
    'validate_config',
    'validate_breath_light_config',
]
