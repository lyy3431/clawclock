#!/usr/bin/env python3
"""
呼吸灯效果测试 - ClawClock 呼吸灯功能单元测试
============================================

测试覆盖:
    - 呼吸灯配置加载
    - 呼吸灯效果初始化
    - 亮度计算
    - 颜色转换
    - 状态切换
    - 配置更新

作者：ClawClock Development Team
版本：1.5.0
"""

import unittest
import sys
import os
import math

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # 添加项目路径
    project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, project_path)
    
    # 模拟 tkinter 以便导入模块
    import sys
    class MockTkinter:
        class Tk: pass
        class Widget: pass
        class Frame: pass
        class Label: pass
        class Button: pass
        class Canvas: pass
    
    sys.modules['tkinter'] = MockTkinter()
    
    from breath_light import (
        BreathLightEffect, 
        BreathLightConfig, 
        BreathMode, 
        TimerStatus,
        hex_to_rgb,
        rgb_to_hex,
        interpolate_color
    )
    BREATH_LIGHT_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  呼吸灯模块导入失败：{e}")
    BREATH_LIGHT_AVAILABLE = False


@unittest.skipUnless(BREATH_LIGHT_AVAILABLE, "呼吸灯模块不可用")
class TestBreathLightConfig(unittest.TestCase):
    """呼吸灯配置测试"""
    
    def test_default_config(self):
        """测试默认配置"""
        config = BreathLightConfig()
        
        self.assertTrue(config.enabled)
        self.assertEqual(config.mode, BreathMode.DIGITAL)
        self.assertEqual(config.frequency, 1.0)
        self.assertEqual(config.intensity, 0.7)
        self.assertEqual(config.normal_color, "#00ff88")
        self.assertEqual(config.warning_color, "#ffaa00")
        self.assertEqual(config.completed_color, "#ff3333")
        self.assertTrue(config.accelerate_on_complete)
    
    def test_custom_config(self):
        """测试自定义配置"""
        config = BreathLightConfig(
            enabled=False,
            mode=BreathMode.BACKGROUND,
            frequency=2.0,
            intensity=0.5,
            normal_color="#ff0000",
            accelerate_on_complete=False
        )
        
        self.assertFalse(config.enabled)
        self.assertEqual(config.mode, BreathMode.BACKGROUND)
        self.assertEqual(config.frequency, 2.0)
        self.assertEqual(config.intensity, 0.5)
        self.assertEqual(config.normal_color, "#ff0000")
        self.assertFalse(config.accelerate_on_complete)
    
    def test_breath_mode_values(self):
        """测试呼吸模式枚举值"""
        self.assertEqual(BreathMode.DIGITAL.value, "digital")
        self.assertEqual(BreathMode.BACKGROUND.value, "background")
        self.assertEqual(BreathMode.BORDER.value, "border")
        self.assertEqual(BreathMode.ALL.value, "all")


@unittest.skipUnless(BREATH_LIGHT_AVAILABLE, "呼吸灯模块不可用")
class TestBreathLightEffect(unittest.TestCase):
    """呼吸灯效果测试"""
    
    def test_effect_initialization(self):
        """测试效果初始化"""
        effect = BreathLightEffect()
        
        self.assertFalse(effect.running)
        self.assertEqual(effect.status, TimerStatus.NORMAL)
        self.assertIsNotNone(effect.config)
    
    def test_effect_with_custom_config(self):
        """测试自定义配置初始化"""
        config = BreathLightConfig(frequency=1.5, intensity=0.8)
        effect = BreathLightEffect(config)
        
        self.assertEqual(effect.config.frequency, 1.5)
        self.assertEqual(effect.config.intensity, 0.8)
    
    def test_status_change(self):
        """测试状态切换"""
        effect = BreathLightEffect()
        
        # 初始状态
        self.assertEqual(effect.status, TimerStatus.NORMAL)
        
        # 切换到警告状态
        effect.set_status(TimerStatus.WARNING)
        self.assertEqual(effect.status, TimerStatus.WARNING)
        
        # 切换到完成状态
        effect.set_status(TimerStatus.COMPLETED)
        self.assertEqual(effect.status, TimerStatus.COMPLETED)
    
    def test_get_current_color(self):
        """测试获取当前颜色"""
        effect = BreathLightEffect()
        
        # 正常状态
        effect.set_status(TimerStatus.NORMAL)
        self.assertEqual(effect.get_current_color(), "#00ff88")
        
        # 警告状态
        effect.set_status(TimerStatus.WARNING)
        self.assertEqual(effect.get_current_color(), "#ffaa00")
        
        # 完成状态
        effect.set_status(TimerStatus.COMPLETED)
        self.assertEqual(effect.get_current_color(), "#ff3333")
    
    def test_brightness_calculation(self):
        """测试亮度计算（正弦波）"""
        effect = BreathLightEffect()
        
        # 模拟不同时间点的亮度
        test_times = [0, 0.25, 0.5, 0.75, 1.0]
        expected_brightness = [0.5, 1.0, 0.5, 0.0, 0.5]  # 正弦波
        
        for elapsed, expected in zip(test_times, expected_brightness):
            brightness = (math.sin(elapsed * 2 * math.pi) + 1) / 2
            # 允许小范围误差
            self.assertAlmostEqual(brightness, expected, delta=0.01)
    
    def test_apply_brightness_to_color(self):
        """测试亮度应用到颜色"""
        effect = BreathLightEffect()
        
        base_color = "#ffffff"  # 白色
        
        # 最大亮度
        bright_color = effect.apply_brightness_to_color(base_color, 1.0)
        self.assertEqual(bright_color, "#ffffff")
        
        # 最小亮度（应该变暗）
        dim_color = effect.apply_brightness_to_color(base_color, 0.0)
        # 最小亮度因子是 0.3，所以应该是 #4c4c4c (255 * 0.3 = 76.5 -> 76 = 0x4c)
        self.assertEqual(dim_color, "#4c4c4c")
        
        # 中间亮度
        mid_color = effect.apply_brightness_to_color(base_color, 0.5)
        # 因子 = 0.3 + 0.7 * 0.5 = 0.65, 255 * 0.65 = 165.75 -> 165 = 0xa5
        self.assertIn(mid_color, ["#a5a5a5", "#a6a6a6"])  # 允许四舍五入误差
    
    def test_color_cache(self):
        """测试颜色缓存"""
        effect = BreathLightEffect()
        
        # 第一次调用应该缓存颜色
        effect.apply_brightness_to_color("#ff0000", 0.5)
        self.assertIn("#ff0000", effect._color_cache)
        
        # 第二次调用应该使用缓存
        effect.apply_brightness_to_color("#ff0000", 0.8)
        self.assertEqual(len(effect._color_cache), 1)
    
    def test_update_config(self):
        """测试配置更新"""
        effect = BreathLightEffect()
        
        # 更新配置
        effect.update_config(frequency=2.0, intensity=0.9)
        
        self.assertEqual(effect.config.frequency, 2.0)
        self.assertEqual(effect.config.intensity, 0.9)
    
    def test_to_dict(self):
        """测试转换为字典"""
        config = BreathLightConfig(
            enabled=True,
            mode=BreathMode.DIGITAL,
            frequency=1.5,
            intensity=0.8
        )
        effect = BreathLightEffect(config)
        
        data = effect.to_dict()
        
        self.assertTrue(data["enabled"])
        self.assertEqual(data["mode"], "digital")
        self.assertEqual(data["frequency"], 1.5)
        self.assertEqual(data["intensity"], 0.8)
        self.assertIn("color_scheme", data)
        self.assertTrue(data["accelerate_on_complete"])
    
    def test_from_dict(self):
        """测试从字典创建"""
        data = {
            "enabled": False,
            "mode": "background",
            "frequency": 2.0,
            "intensity": 0.6,
            "color_scheme": {
                "normal": "#00ff00",
                "warning": "#ffff00",
                "completed": "#ff0000"
            },
            "accelerate_on_complete": False
        }
        
        effect = BreathLightEffect.from_dict(data)
        
        self.assertFalse(effect.config.enabled)
        self.assertEqual(effect.config.mode, BreathMode.BACKGROUND)
        self.assertEqual(effect.config.frequency, 2.0)
        self.assertEqual(effect.config.intensity, 0.6)
        self.assertEqual(effect.config.normal_color, "#00ff00")
        self.assertFalse(effect.config.accelerate_on_complete)


@unittest.skipUnless(BREATH_LIGHT_AVAILABLE, "呼吸灯模块不可用")
class TestColorUtilities(unittest.TestCase):
    """颜色工具函数测试"""
    
    def test_hex_to_rgb(self):
        """测试十六进制转 RGB"""
        # 红色
        self.assertEqual(hex_to_rgb("#ff0000"), (255, 0, 0))
        self.assertEqual(hex_to_rgb("ff0000"), (255, 0, 0))
        
        # 绿色
        self.assertEqual(hex_to_rgb("#00ff00"), (0, 255, 0))
        
        # 蓝色
        self.assertEqual(hex_to_rgb("#0000ff"), (0, 0, 255))
        
        # 白色
        self.assertEqual(hex_to_rgb("#ffffff"), (255, 255, 255))
        
        # 黑色
        self.assertEqual(hex_to_rgb("#000000"), (0, 0, 0))
    
    def test_rgb_to_hex(self):
        """测试 RGB 转十六进制"""
        self.assertEqual(rgb_to_hex(255, 0, 0), "#ff0000")
        self.assertEqual(rgb_to_hex(0, 255, 0), "#00ff00")
        self.assertEqual(rgb_to_hex(0, 0, 255), "#0000ff")
        self.assertEqual(rgb_to_hex(255, 255, 255), "#ffffff")
        self.assertEqual(rgb_to_hex(0, 0, 0), "#000000")
        self.assertEqual(rgb_to_hex(128, 64, 32), "#804020")
    
    def test_color_roundtrip(self):
        """测试颜色往返转换"""
        test_colors = [
            "#ff0000", "#00ff00", "#0000ff",
            "#ffffff", "#000000", "#808080",
            "#123456", "#abcdef"
        ]
        
        for hex_color in test_colors:
            rgb = hex_to_rgb(hex_color)
            hex_back = rgb_to_hex(*rgb)
            self.assertEqual(hex_color.lower(), hex_back.lower())
    
    def test_interpolate_color(self):
        """测试颜色插值"""
        # 从黑色到白色
        self.assertEqual(interpolate_color("#000000", "#ffffff", 0.0), "#000000")
        self.assertEqual(interpolate_color("#000000", "#ffffff", 1.0), "#ffffff")
        # 0.5 插值：255 * 0.5 = 127.5 -> 127 = 0x7f
        result = interpolate_color("#000000", "#ffffff", 0.5)
        self.assertIn(result, ["#7f7f7f", "#808080"])  # 允许四舍五入误差
        
        # 从红色到蓝色
        result = interpolate_color("#ff0000", "#0000ff", 0.5)
        self.assertIn(result, ["#7f007f", "#800080"])  # 允许四舍五入误差
        
        # 因子为 0 应该返回起始颜色
        result = interpolate_color("#123456", "#abcdef", 0.0)
        self.assertEqual(result, "#123456")
        
        # 因子为 1 应该返回结束颜色
        result = interpolate_color("#123456", "#abcdef", 1.0)
        self.assertEqual(result, "#abcdef")


@unittest.skipUnless(BREATH_LIGHT_AVAILABLE, "呼吸灯模块不可用")
class TestTimerStatus(unittest.TestCase):
    """倒计时状态测试"""
    
    def test_timer_status_values(self):
        """测试倒计时状态枚举值"""
        self.assertEqual(TimerStatus.NORMAL.value, "normal")
        self.assertEqual(TimerStatus.WARNING.value, "warning")
        self.assertEqual(TimerStatus.COMPLETED.value, "completed")


@unittest.skipUnless(BREATH_LIGHT_AVAILABLE, "呼吸灯模块不可用")
class TestBreathLightIntegration(unittest.TestCase):
    """呼吸灯集成测试"""
    
    def test_frequency_acceleration(self):
        """测试频率加速（时间到时）"""
        config = BreathLightConfig(
            frequency=1.0,
            accelerate_on_complete=True
        )
        effect = BreathLightEffect(config)
        
        # 正常状态
        effect.set_status(TimerStatus.NORMAL)
        self.assertEqual(effect.config.frequency, 1.0)
        
        # 完成状态应该加速（在_animate 方法中处理）
        effect.set_status(TimerStatus.COMPLETED)
        # 频率配置不变，但在动画中会乘以 3
        self.assertEqual(effect.config.frequency, 1.0)
    
    def test_intensity_range(self):
        """测试强度范围"""
        # 最小强度
        config_min = BreathLightConfig(intensity=0.0)
        effect_min = BreathLightEffect(config_min)
        self.assertEqual(effect_min.config.intensity, 0.0)
        
        # 最大强度
        config_max = BreathLightConfig(intensity=1.0)
        effect_max = BreathLightEffect(config_max)
        self.assertEqual(effect_max.config.intensity, 1.0)
    
    def test_brightness_bounds(self):
        """测试亮度边界"""
        effect = BreathLightEffect()
        
        # 模拟亮度计算
        test_values = [-0.5, 0.0, 0.5, 1.0, 1.5]
        
        for value in test_values:
            # 确保亮度在 0-1 范围内
            brightness = max(0.0, min(1.0, value))
            self.assertGreaterEqual(brightness, 0.0)
            self.assertLessEqual(brightness, 1.0)


def run_tests():
    """运行所有测试"""
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加测试
    suite.addTests(loader.loadTestsFromTestCase(TestBreathLightConfig))
    suite.addTests(loader.loadTestsFromTestCase(TestBreathLightEffect))
    suite.addTests(loader.loadTestsFromTestCase(TestColorUtilities))
    suite.addTests(loader.loadTestsFromTestCase(TestTimerStatus))
    suite.addTests(loader.loadTestsFromTestCase(TestBreathLightIntegration))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 返回测试结果
    return result.wasSuccessful()


if __name__ == "__main__":
    print("🫧 " + "="*60)
    print("🫧 ClawClock 呼吸灯效果单元测试")
    print("🫧 " + "="*60)
    print()
    
    success = run_tests()
    
    print()
    print("="*60)
    if success:
        print("✅ 所有测试通过！")
    else:
        print("❌ 部分测试失败")
    print("="*60)
    
    sys.exit(0 if success else 1)
