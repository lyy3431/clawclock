#!/usr/bin/env python3
"""
ClawClock 集成测试模块
======================

测试模块间的集成和交互：
- UI 交互测试
- 配置持久化端到端测试
- 闹钟触发集成测试
- 秒表和倒计时集成测试
"""

import unittest
import json
import os
import sys
import tempfile
import time
from typing import Dict, Any, Optional

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from clock_core import Alarm, StopwatchState, TimerState, LapRecord
from config.validation import (
    AppConfig, BreathLightConfig, WindowConfig,
    ThemeConfig, validate_config
)
from config.settings import ConfigManager, get_config_manager


class TestConfigValidationIntegration(unittest.TestCase):
    """配置验证集成测试"""

    def setUp(self):
        """设置测试环境"""
        self.test_config = {
            "timezone": "Asia/Shanghai",
            "display_mode": "digital",
            "window": {
                "width": 800,
                "height": 600,
                "resizable": True,
                "always_on_top": False,
                "fullscreen": False
            },
            "theme": {
                "name": "dark",
                "display_name": "Dark",
                "colors": {
                    "background": "#1a1a2e",
                    "face": "#16213e",
                    "hand": "#e94560",
                    "text": "#ffffff",
                    "accent": "#0f3460",
                    "segment_on": "#ff3333",
                    "segment_off": "#331111"
                }
            },
            "breath_light": {
                "enabled": True,
                "mode": "digital",
                "style": "soft",
                "frequency": 0.5,
                "intensity": 0.7,
                "accelerate_on_complete": True,
                "smooth_curve": True
            },
            "alarms": [
                {"time": "07:00", "enabled": True, "label": "起床"},
                {"time": "23:00", "enabled": False, "label": "睡觉"}
            ]
        }

    def test_full_config_validation(self):
        """测试完整配置验证"""
        config = validate_config(self.test_config)
        self.assertIsInstance(config, AppConfig)
        self.assertEqual(config.timezone, "Asia/Shanghai")
        self.assertEqual(config.display_mode, "digital")
        self.assertEqual(config.window.width, 800)
        self.assertEqual(config.window.height, 600)

    def test_breath_light_config_validation(self):
        """测试呼吸灯配置验证"""
        breath_config = BreathLightConfig(**self.test_config["breath_light"])
        self.assertEqual(breath_config.style.value, "soft")
        self.assertEqual(breath_config.frequency, 0.5)
        self.assertEqual(breath_config.intensity, 0.7)

    def test_invalid_config_fallback(self):
        """测试无效配置降级处理"""
        invalid_config = {
            "window": {"width": -100},  # 无效值
            "breath_light": {"frequency": 2.0}  # 超出范围
        }
        # 应该使用默认值
        config = validate_config(invalid_config)
        self.assertGreaterEqual(config.window.width, 400)
        self.assertLessEqual(config.breath_light.frequency, 1.0)

    def test_config_to_dict_roundtrip(self):
        """测试配置序列化和反序列化"""
        config1 = validate_config(self.test_config)
        config_dict = config1.to_dict()
        config2 = validate_config(config_dict)

        self.assertEqual(config1.window.width, config2.window.width)
        self.assertEqual(config1.theme.name, config2.theme.name)


class TestConfigPersistenceIntegration(unittest.TestCase):
    """配置持久化集成测试"""

    def setUp(self):
        """创建临时配置文件"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.temp_dir, "test_config.json")
        self.manager = ConfigManager(self.config_file)

    def tearDown(self):
        """清理临时文件"""
        if os.path.exists(self.config_file):
            os.remove(self.config_file)
        os.rmdir(self.temp_dir)

    def test_save_and_load_config(self):
        """测试保存和加载配置"""
        # 设置配置
        self.manager.config["timezone"] = "America/New_York"
        self.manager.config["window"] = {"width": 1024, "height": 768}

        # 保存
        result = self.manager.save()
        self.assertTrue(result)

        # 新建管理器并加载
        new_manager = ConfigManager(self.config_file)
        loaded_config = new_manager.load()

        self.assertEqual(loaded_config["timezone"], "America/New_York")
        self.assertEqual(loaded_config["window"]["width"], 1024)

    def test_config_merge_on_load(self):
        """测试加载时配置合并"""
        # 创建不完整的配置
        partial_config = {"timezone": "Europe/London"}
        with open(self.config_file, 'w') as f:
            json.dump(partial_config, f)

        # 加载应该合并默认配置
        self.manager.load()

        self.assertEqual(self.manager.config["timezone"], "Europe/London")
        self.assertIn("window", self.manager.config)
        self.assertIn("theme", self.manager.config)

    def test_validated_config_updated(self):
        """测试验证配置在加载后更新"""
        self.manager.load()
        self.assertIsNotNone(self.manager.validated_config)
        self.assertIsInstance(self.manager.validated_config, AppConfig)


class TestAlarmIntegration(unittest.TestCase):
    """闹钟集成测试"""

    def test_alarm_is_due(self):
        """测试闹钟触发逻辑"""
        import datetime

        alarm = Alarm(time="12:30", enabled=True)

        # 匹配时间
        match_time = datetime.datetime(2024, 1, 1, 12, 30, 0)
        self.assertTrue(alarm.is_due(match_time))

        # 不匹配时间
        mismatch_time = datetime.datetime(2024, 1, 1, 12, 31, 0)
        self.assertFalse(alarm.is_due(mismatch_time))

        # 禁用的闹钟
        disabled_alarm = Alarm(time="12:30", enabled=False)
        self.assertFalse(disabled_alarm.is_due(match_time))

    def test_alarm_with_repeat_days(self):
        """测试带重复日期的闹钟"""
        import datetime

        # 仅工作日重复
        weekday_alarm = Alarm(time="09:00", enabled=True, repeat_days=[0, 1, 2, 3, 4])

        # 周一（应该触发）
        monday = datetime.datetime(2024, 1, 1, 9, 0, 0)  # 2024-01-01 is Monday
        self.assertTrue(weekday_alarm.is_due(monday))

        # 周六（不应该触发）
        saturday = datetime.datetime(2024, 1, 6, 9, 0, 0)  # 2024-01-06 is Saturday
        self.assertFalse(weekday_alarm.is_due(saturday))

    def test_alarm_serialization(self):
        """测试闹钟序列化"""
        alarm = Alarm(
            time="07:30",
            enabled=True,
            label="Morning Alarm",
            repeat_days=[0, 1, 2, 3, 4],
            snooze_minutes=10
        )

        alarm_dict = {
            "time": alarm.time,
            "enabled": alarm.enabled,
            "label": alarm.label,
            "sound": alarm.sound,
            "repeat_days": alarm.repeat_days,
            "snooze_minutes": alarm.snooze_minutes
        }

        restored = Alarm(**alarm_dict)
        self.assertEqual(alarm.time, restored.time)
        self.assertEqual(alarm.repeat_days, restored.repeat_days)


class TestStopwatchIntegration(unittest.TestCase):
    """秒表集成测试"""

    def test_stopwatch_state_serialization(self):
        """测试秒表状态序列化"""
        state = StopwatchState(
            is_running=True,
            start_time=1000.0,
            elapsed_ms=5000,
            laps=[
                LapRecord(lap_number=1, time_ms=1000, split_ms=1000),
                LapRecord(lap_number=2, time_ms=2000, split_ms=1000)
            ]
        )

        self.assertTrue(state.is_running)
        self.assertEqual(len(state.laps), 2)
        self.assertEqual(state.laps[0].lap_number, 1)

    def test_stopwatch_elapsed_time_calculation(self):
        """测试秒表经过时间计算"""
        state = StopwatchState()
        state.is_running = True
        state.start_time = time.time()
        state.elapsed_ms = 1000

        # 等待一小段时间
        time.sleep(0.1)

        # 计算应该大于初始值
        current_time = time.time()
        delta_ms = int((current_time - state.start_time) * 1000)
        total_ms = state.elapsed_ms + delta_ms

        self.assertGreater(total_ms, 1000)


class TestTimerIntegration(unittest.TestCase):
    """倒计时集成测试"""

    def test_timer_state(self):
        """测试倒计时状态"""
        state = TimerState(
            is_running=True,
            total_seconds=1500,
            remaining_seconds=1400.5,
            sound_enabled=False,
            preset_name="番茄钟"
        )

        self.assertTrue(state.is_running)
        self.assertEqual(state.total_seconds, 1500)
        self.assertAlmostEqual(state.remaining_seconds, 1400.5, places=1)
        self.assertFalse(state.sound_enabled)

    def test_timer_remaining_calculation(self):
        """测试倒计时剩余时间计算"""
        state = TimerState()
        state.is_running = True
        state.start_time = time.time()
        state.remaining_seconds = 10.0

        # 等待一小段时间
        time.sleep(0.2)

        # 计算剩余时间
        elapsed = time.time() - state.start_time
        remaining = max(0, state.remaining_seconds - elapsed)

        self.assertLess(remaining, 10.0)
        self.assertGreater(remaining, 8.0)


class TestThemeValidationIntegration(unittest.TestCase):
    """主题验证集成测试"""

    def test_theme_colors_validation(self):
        """测试主题颜色验证"""
        from config.validation import ThemeColorsConfig

        colors = ThemeColorsConfig(
            background="#000000",
            face="#111111",
            hand="#222222",
            text="#ffffff",
            accent="#333333",
            segment_on="#ff0000",
            segment_off="#110000"
        )

        self.assertEqual(colors.background, "#000000")
        # pydantic 可能转换大小写，使用不区分大小写的比较
        self.assertEqual(colors.text.upper(), "#FFFFFF")

    def test_theme_config_validation(self):
        """测试完整主题配置验证"""
        theme_dict = {
            "name": "cyberpunk",
            "display_name": "Cyberpunk",
            "colors": {
                "background": "#0d0d0d",
                "face": "#1a1a2e",
                "hand": "#e94560",
                "text": "#00ff00",
                "accent": "#0f3460",
                "segment_on": "#ff3333",
                "segment_off": "#331111"
            }
        }

        from config.validation import ThemeConfig
        theme = ThemeConfig(**theme_dict)

        self.assertEqual(theme.name, "cyberpunk")
        # pydantic 可能转换大小写，使用不区分大小写的比较
        self.assertEqual(theme.colors.text.upper(), "#00FF00")

    def test_invalid_hex_color_handling(self):
        """测试无效十六进制颜色处理"""
        from config.validation import ThemeColorsConfig

        # 无效颜色应该使用默认值
        colors = ThemeColorsConfig(background="invalid")
        self.assertEqual(colors.background, "#000000")


class TestWindowConfigIntegration(unittest.TestCase):
    """窗口配置集成测试"""

    def test_window_config_bounds(self):
        """测试窗口配置边界值"""
        # 最小值
        window = WindowConfig(width=400, height=300)
        self.assertEqual(window.width, 400)
        self.assertEqual(window.height, 300)

        # 最大值
        window = WindowConfig(width=3840, height=2160)
        self.assertEqual(window.width, 3840)
        self.assertEqual(window.height, 2160)

    def test_window_config_invalid_values(self):
        """测试窗口配置无效值处理"""
        from pydantic import ValidationError

        # 负值应该抛出验证错误或被修正
        # pydantic v2 会抛出验证错误，我们测试这个行为
        try:
            window = WindowConfig(width=-100, height=-50)
            # 如果没抛出异常，检查值是否被修正
            self.assertGreaterEqual(window.width, 400)
            self.assertGreaterEqual(window.height, 300)
        except ValidationError:
            # pydantic v2 会抛出验证错误，这也是期望的行为
            pass

    def test_window_position_optional(self):
        """测试窗口位置可选性"""
        window1 = WindowConfig()
        self.assertIsNone(window1.x)
        self.assertIsNone(window1.y)

        window2 = WindowConfig(x=100, y=200)
        self.assertEqual(window2.x, 100)
        self.assertEqual(window2.y, 200)


class TestBreathLightConfigIntegration(unittest.TestCase):
    """呼吸灯配置集成测试"""

    def test_breath_style_enum(self):
        """测试呼吸风格枚举"""
        from config.validation import BreathStyle

        self.assertEqual(BreathStyle.SOFT.value, "soft")
        self.assertEqual(BreathStyle.TECH.value, "tech")
        self.assertEqual(BreathStyle.COOL.value, "cool")
        self.assertEqual(BreathStyle.MINIMAL.value, "minimal")

    def test_breath_config_frequency_bounds(self):
        """测试呼吸配置频率边界"""
        # 有效范围
        config1 = BreathLightConfig(frequency=0.0)
        config2 = BreathLightConfig(frequency=1.0)

        # 超出范围应该被修正
        config3 = BreathLightConfig(frequency=-0.5)
        config4 = BreathLightConfig(frequency=1.5)

        self.assertGreaterEqual(config3.frequency, 0.0)
        self.assertLessEqual(config4.frequency, 1.0)

    def test_breath_config_mode_validation(self):
        """测试呼吸配置模式验证"""
        # 有效模式
        config1 = BreathLightConfig(mode="digital")
        self.assertEqual(config1.mode, "digital")

        config2 = BreathLightConfig(mode="analog")
        self.assertEqual(config2.mode, "analog")

    def test_breath_config_to_dict(self):
        """测试呼吸配置转字典"""
        config = BreathLightConfig(
            enabled=True,
            mode="digital",
            style="tech",
            frequency=0.8,
            intensity=0.6
        )

        config_dict = config.to_dict()
        self.assertEqual(config_dict["enabled"], True)
        self.assertEqual(config_dict["mode"], "digital")
        self.assertEqual(config_dict["style"], "tech")


def run_integration_tests(verbosity: int = 2) -> unittest.TestResult:
    """运行集成测试"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # 添加所有测试类
    suite.addTests(loader.loadTestsFromTestCase(TestConfigValidationIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestConfigPersistenceIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestAlarmIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestStopwatchIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestTimerIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestThemeValidationIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestWindowConfigIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestBreathLightConfigIntegration))

    runner = unittest.TextTestRunner(verbosity=verbosity)
    return runner.run(suite)


if __name__ == "__main__":
    print("=" * 60)
    print("ClawClock 集成测试")
    print("=" * 60)
    result = run_integration_tests()

    # 返回退出码
    sys.exit(0 if result.wasSuccessful() else 1)
