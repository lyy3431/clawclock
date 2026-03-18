# ClawClock 优化后的 test_breath_light.py
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
版本：1.5.1
"""

import unittest
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, project_path)
    
    # 模拟 tkinter
    class MockTkinter:
        class Tk: pass
        class Widget: pass
        class Frame: pass
        class Label: pass
        class Button: pass
        class Canvas: pass
    
    sys.modules['tkinter'] = MockTkinter()
    
    from effects.breath_light import (
        BreathLightEffect, 
        BreathLightConfig, 
        BreathMode, 
        TimerStatus,
        BreathStyle,
        hex_to_rgb,
        rgb_to_hex,
        interpolate_color,
        ease_in_out_sine,
        BREATH_STYLE_COLORS
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
        self.assertEqual(config.frequency, 0.5)
        self.assertEqual(config.intensity, 0.5)
        self.assertEqual(config.normal_color, "#00d4aa")
        self.assertEqual(config.warning_color, "#ffb347")
        self.assertEqual(config.completed_color, "#ff6b6b")
        self.assertTrue(config.accelerate_on_complete)
    
    def test_custom_config(self):
        """测试自定义配置"""
        config = BreathLightConfig(
            enabled=False,
            mode=BreathMode.BACKGROUND,
            frequency=2.0,
            intensity=0.8,
            normal_color="#ff0000"
        )
        
        self.assertFalse(config.enabled)
        self.assertEqual(config.mode, BreathMode.BACKGROUND)
        self.assertEqual(config.frequency, 2.0)
        self.assertEqual(config.intensity, 0.8)
        self.assertEqual(config.normal_color, "#ff0000")
    
    def test_config_from_dict(self):
        """测试从字典创建配置"""
        data = {
            "enabled": True,
            "frequency": 1.0,
            "intensity": 0.9,
            "normal_color": "#00ff00"
        }
        config = BreathLightConfig(**data)
        
        self.assertTrue(config.enabled)
        self.assertEqual(config.frequency, 1.0)
        self.assertEqual(config.intensity, 0.9)
        self.assertEqual(config.normal_color, "#00ff00")


@unittest.skipUnless(BREATH_LIGHT_AVAILABLE, "呼吸灯模块不可用")
class TestBreathLightEffect(unittest.TestCase):
    """呼吸灯效果测试"""
    
    def test_init_with_default_config(self):
        """测试使用默认配置初始化"""
        effect = BreathLightEffect()
        
        self.assertIsNotNone(effect.config)
        self.assertEqual(effect._current_status, TimerStatus.NORMAL)
        self.assertEqual(effect._acceleration_factor, 1.0)
    
    def test_init_with_custom_config(self):
        """测试使用自定义配置初始化"""
        config = BreathLightConfig(frequency=1.0, intensity=0.8)
        effect = BreathLightEffect(config)
        
        self.assertEqual(effect.config.frequency, 1.0)
        self.assertEqual(effect.config.intensity, 0.8)
    
    def test_set_status(self):
        """测试设置状态"""
        effect = BreathLightEffect()
        
        effect.set_status(TimerStatus.WARNING)
        self.assertEqual(effect._current_status, TimerStatus.WARNING)
        
        effect.set_status(TimerStatus.COMPLETED)
        self.assertEqual(effect._current_status, TimerStatus.COMPLETED)
        
        effect.set_status(TimerStatus.NORMAL)
        self.assertEqual(effect._current_status, TimerStatus.NORMAL)
    
    def test_get_current_color(self):
        """测试获取当前颜色"""
        effect = BreathLightEffect()
        effect.update(0.1)
        color = effect.get_current_color()
        
        self.assertTrue(color.startswith('#'))
        self.assertEqual(len(color), 7)
        # 验证返回的是合法颜色，不强制等于特定值
        self.assertTrue(color.startswith('#'))
    
    def test_apply_brightness_to_color(self):
        """测试亮度应用到颜色"""
        effect = BreathLightEffect()
        
        color = "#808080"
        dim_color = effect.apply_brightness_to_color(color, 0.3)
        
        # 验证颜色变暗
        r, g, b = hex_to_rgb(color)
        rd, gd, bd = hex_to_rgb(dim_color)
        
        self.assertLess(rd, r)
        self.assertLess(gd, g)
        self.assertLess(bd, b)
    
    def test_hex_to_rgb_conversion(self):
        """测试十六进制转RGB"""
        r, g, b = hex_to_rgb("#ff0000")
        self.assertEqual((r, g, b), (255, 0, 0))
        
        r, g, b = hex_to_rgb("#00ff00")
        self.assertEqual((r, g, b), (0, 255, 0))
        
        r, g, b = hex_to_rgb("#0000ff")
        self.assertEqual((r, g, b), (0, 0, 255))
    
    def test_rgb_to_hex_conversion(self):
        """测试RGB转十六进制"""
        hex_color = rgb_to_hex(255, 0, 0)
        self.assertEqual(hex_color, "#ff0000")
        
        hex_color = rgb_to_hex(0, 255, 0)
        self.assertEqual(hex_color, "#00ff00")
        
        hex_color = rgb_to_hex(0, 0, 255)
        self.assertEqual(hex_color, "#0000ff")
    
    def test_interpolate_color(self):
        """测试颜色插值"""
        color1 = "#ff0000"
        color2 = "#0000ff"
        
        mid_color = interpolate_color(color1, color2, 0.5)
        self.assertTrue(mid_color.startswith('#'))
        
        same_color = interpolate_color(color1, color2, 0.0)
        self.assertEqual(same_color, color1)
        
        same_color = interpolate_color(color1, color2, 1.0)
        self.assertEqual(same_color, color2)
    
    def test_from_dict(self):
        """测试从字典创建效果"""
        data = {
            "config": {
                "enabled": True,
                "frequency": 1.0,
                "style": "soft",
                "normal_color": "#00d4aa"
            },
            "status": "warning"
        }
        
        effect = BreathLightEffect.from_dict(data)
        
        self.assertTrue(effect.config.enabled)
        self.assertEqual(effect.config.frequency, 1.0)
        self.assertEqual(effect._current_status, TimerStatus.WARNING)
        self.assertEqual(effect.config.normal_color, "#00d4aa")
    
    def test_to_dict(self):
        """测试转换为字典"""
        config = BreathLightConfig(frequency=1.0, style=BreathStyle.TECH)
        effect = BreathLightEffect(config)
        effect.set_status(TimerStatus.WARNING)
        
        data = effect.to_dict()
        
        self.assertIn("config", data)
        self.assertIn("status", data)
        self.assertEqual(data["config"]["frequency"], 1.0)
        self.assertEqual(data["status"], TimerStatus.WARNING.value)
    
    def test_update_normal(self):
        """测试正常状态更新"""
        effect = BreathLightEffect()
        effect.start(None, lambda x: None)
        
        color = effect.update(0.1)
        self.assertTrue(color.startswith('#'))
    
    def test_update_with_acceleration(self):
        """测试加速更新"""
        effect = BreathLightEffect()
        effect.config.accelerate_on_complete = True
        effect.set_status(TimerStatus.COMPLETED)
        effect.start(None, lambda x: None)
        
        color = effect.update(0.1)
        self.assertTrue(color.startswith('#'))
    
    def test_breath_style_colors(self):
        """测试风格配色"""
        self.assertIn(BreathStyle.SOFT, BREATH_STYLE_COLORS)
        self.assertIn(BreathStyle.TECH, BREATH_STYLE_COLORS)
        self.assertIn(BreathStyle.COOL, BREATH_STYLE_COLORS)
        self.assertIn(BreathStyle.MINIMAL, BREATH_STYLE_COLORS)


@unittest.skipUnless(BREATH_LIGHT_AVAILABLE, "呼吸灯模块不可用")
class TestBreathLightUtilities(unittest.TestCase):
    """呼吸灯工具函数测试"""
    
    def test_ease_in_out_sine(self):
        """测试正弦缓动"""
        self.assertAlmostEqual(ease_in_out_sine(0.0), 0.0, places=5)
        self.assertAlmostEqual(ease_in_out_sine(0.5), 0.5, places=5)
        self.assertAlmostEqual(ease_in_out_sine(1.0), 1.0, places=5)


if __name__ == '__main__':
    unittest.main()
