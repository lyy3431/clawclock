# ClawClock 配置管理模块
"""
负责加载、保存和管理应用配置

使用 pydantic 进行配置验证，确保配置数据的完整性和类型安全。
"""
import json
import os
from typing import Dict, Any, Optional
from config.constants import CONFIG_FILE, DEFAULT_THEME
from config.validation import AppConfig, validate_config


class ConfigManager:
    """配置管理器（使用 pydantic 验证）"""

    def __init__(self, config_file: str = CONFIG_FILE):
        """初始化配置管理器"""
        self.config_file = config_file
        self.config: Dict[str, Any] = {}
        self.validated_config: Optional[AppConfig] = None
        self.default_config: Dict[str, Any] = {
            "timezone": "Asia/Shanghai",
            "theme": DEFAULT_THEME,
            "mode": "analog",
            "window": {
                "width": 600,
                "height": 500,
                "x": None,
                "y": None,
                "resizable": False,
                "always_on_top": False,
                "fullscreen": False
            },
            "stopwatch": {
                "interval": 10  # 毫秒
            },
            "timer": {
                "sound_enabled": True,
                "preset": "番茄钟"
            },
            "breath_light": {
                "enabled": True,
                "mode": "digital",
                "style": "soft",
                "frequency": 0.5,
                "intensity": 0.5,
                "accelerate_on_complete": True,
                "smooth_curve": True
            }
        }

    def load(self) -> Dict[str, Any]:
        """加载配置文件（带 pydantic 验证）"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    custom_config = json.load(f)
                    self.config = self._merge(self.default_config, custom_config)
                    # 使用 pydantic 验证配置
                    self.validated_config = validate_config(self.config)
                    return self.config
            except (json.JSONDecodeError, IOError) as e:
                print(f"⚠️  配置文件加载失败：{e}")
                self.config = self.default_config.copy()
                self.validated_config = AppConfig()
        else:
            self.config = self.default_config.copy()
            self.validated_config = AppConfig()

        return self.config

    def save(self, config: Optional[Dict[str, Any]] = None) -> bool:
        """保存配置文件"""
        config_to_save = config if config is not None else self.config

        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_to_save, f, indent=2, ensure_ascii=False)
            return True
        except IOError as e:
            print(f"⚠️  配置文件保存失败：{e}")
            return False

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置项"""
        keys = key.split('.')
        value = self.config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value if value is not None else default

    def set(self, key: str, value: Any) -> bool:
        """设置配置项"""
        keys = key.split('.')
        config = self.config

        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]

        config[keys[-1]] = value
        return self.save()

    def _merge(self, default: Dict[str, Any], custom: Dict[str, Any]) -> Dict[str, Any]:
        """合并默认配置和自定义配置"""
        result = default.copy()

        for key, value in custom.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge(result[key], value)
            else:
                result[key] = value

        return result

    def reset(self) -> bool:
        """重置为默认配置"""
        self.config = self.default_config.copy()
        self.validated_config = AppConfig()
        return self.save()

    def get_validated(self) -> AppConfig:
        """获取验证后的配置对象"""
        if self.validated_config is None:
            self.validated_config = AppConfig()
        return self.validated_config


# 全局配置管理器实例
_config_manager: Optional[ConfigManager] = None


def get_config_manager() -> ConfigManager:
    """获取全局配置管理器实例"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
        _config_manager.load()
    return _config_manager


def reload_config() -> Dict[str, Any]:
    """重新加载配置"""
    return get_config_manager().load()


def save_config(config: Optional[Dict[str, Any]] = None) -> bool:
    """保存配置"""
    return get_config_manager().save(config)


def validate_breath_light_config(data: Dict[str, Any]) -> 'BreathLightConfig':
    """
    验证呼吸灯配置

    Args:
        data: 呼吸灯配置字典

    Returns:
        BreathLightConfig: 验证后的配置对象
    """
    from config.validation import BreathLightConfig
    return BreathLightConfig(**data)
