#!/usr/bin/env python3
"""
ClawClock - 增强动画效果测试
"""

import unittest
from unittest.mock import Mock, MagicMock, patch
import math
import sys

# Mock tkinter before importing
sys.modules['tkinter'] = MagicMock()

from effects.enhanced_animations import (
    Easing, AnimationManager, AnimationState,
    HourChimeAnimation, ModeTransitionAnimation,
    ThemeTransitionAnimation, SmoothSecondHandAnimation,
    DigitFlipAnimation, AnimationConfig,
    interpolate_color, create_gradient_colors
)


class TestEasingFunctions(unittest.TestCase):
    """测试缓动函数"""

    def test_linear(self):
        """测试线性缓动"""
        self.assertEqual(Easing.linear(0.0), 0.0)
        self.assertEqual(Easing.linear(0.5), 0.5)
        self.assertEqual(Easing.linear(1.0), 1.0)

    def test_ease_in_quad(self):
        """测试二次缓入"""
        self.assertEqual(Easing.ease_in_quad(0.0), 0.0)
        self.assertEqual(Easing.ease_in_quad(1.0), 1.0)
        self.assertLess(Easing.ease_in_quad(0.5), 0.5)  # 缓入应该慢于线性

    def test_ease_out_quad(self):
        """测试二次缓出"""
        self.assertEqual(Easing.ease_out_quad(0.0), 0.0)
        self.assertEqual(Easing.ease_out_quad(1.0), 1.0)
        self.assertGreater(Easing.ease_out_quad(0.5), 0.5)  # 缓出应该快于线性

    def test_ease_in_out_quad(self):
        """测试二次缓入缓出"""
        self.assertEqual(Easing.ease_in_out_quad(0.0), 0.0)
        self.assertEqual(Easing.ease_in_out_quad(1.0), 1.0)
        self.assertEqual(Easing.ease_in_out_quad(0.5), 0.5)

    def test_ease_in_out_sine(self):
        """测试正弦缓入缓出"""
        self.assertAlmostEqual(Easing.ease_in_out_sine(0.0), 0.0, places=5)
        self.assertAlmostEqual(Easing.ease_in_out_sine(1.0), 1.0, places=5)
        self.assertAlmostEqual(Easing.ease_in_out_sine(0.5), 0.5, places=5)

    def test_ease_out_bounce(self):
        """测试弹跳缓出"""
        self.assertEqual(Easing.ease_out_bounce(0.0), 0.0)
        self.assertEqual(Easing.ease_out_bounce(1.0), 1.0)
        # 弹跳效果应该在某些点大于 t
        self.assertGreater(Easing.ease_out_bounce(0.9), 0.9)


class TestAnimationManager(unittest.TestCase):
    """测试动画管理器"""

    def test_create_animation(self):
        """测试创建动画"""
        manager = AnimationManager()
        anim = manager.create_animation("test", duration=1.0, easing="linear")
        
        self.assertIn("test", manager.animations)
        self.assertEqual(anim.duration, 1.0)
        self.assertEqual(anim.easing, "linear")
        self.assertFalse(anim.running)

    def test_start_animation(self):
        """测试启动动画"""
        manager = AnimationManager()
        manager.create_animation("test", duration=1.0)
        manager.start_animation("test")
        
        self.assertTrue(manager.animations["test"].running)
        self.assertEqual(manager.animations["test"].progress, 0.0)

    def test_update_animation(self):
        """测试更新动画"""
        manager = AnimationManager()
        manager.create_animation("test", duration=1.0, easing="linear")
        manager.start_animation("test")
        
        # 模拟时间流逝
        import time
        original_time = time.time
        time.time = lambda: original_time() + 0.5  # 前进 0.5 秒
        
        value = manager.update_animation("test")
        
        self.assertAlmostEqual(value, 0.5, places=1)
        
        # 恢复
        time.time = original_time

    def test_animation_complete(self):
        """测试动画完成"""
        manager = AnimationManager()
        completed = []
        
        def on_complete():
            completed.append(True)
        
        manager.create_animation(
            "test", duration=0.1,
            on_complete=on_complete
        )
        manager.start_animation("test")
        
        # 等待完成
        import time
        original_time = time.time
        time.time = lambda: original_time() + 0.2
        
        manager.update_animation("test")
        
        self.assertTrue(completed)
        self.assertFalse(manager.is_animation_running("test"))
        
        time.time = original_time

    def test_is_animation_running(self):
        """测试检查动画状态"""
        manager = AnimationManager()
        manager.create_animation("test", duration=1.0)
        
        self.assertFalse(manager.is_animation_running("test"))
        
        manager.start_animation("test")
        self.assertTrue(manager.is_animation_running("test"))


class TestHourChimeAnimation(unittest.TestCase):
    """测试整点报时动画"""

    @patch('tkinter.Canvas')
    def test_init(self, mock_canvas):
        """测试初始化"""
        anim = HourChimeAnimation(mock_canvas)
        
        self.assertIsNotNone(anim.manager)
        self.assertTrue(hasattr(anim, 'effect'))
        self.assertEqual(anim.effect.particle_count, 20)

    @patch('tkinter.Canvas')
    def test_trigger(self, mock_canvas):
        """测试触发"""
        anim = HourChimeAnimation(mock_canvas)
        anim.effect.enabled = True
        anim.trigger(12)
        
        self.assertTrue(anim.manager.is_animation_running("scale"))
        self.assertTrue(anim.manager.is_animation_running("glow"))
        self.assertTrue(anim.manager.is_animation_running("particles"))

    @patch('tkinter.Canvas')
    def test_create_particles(self, mock_canvas):
        """测试粒子创建"""
        anim = HourChimeAnimation(mock_canvas)
        anim._create_particles()
        
        self.assertEqual(len(anim.particles), anim.effect.particle_count)
        # 检查粒子属性
        for particle in anim.particles:
            self.assertIn("angle", particle)
            self.assertIn("distance", particle)
            self.assertIn("speed", particle)


class TestModeTransitionAnimation(unittest.TestCase):
    """测试模式切换动画"""

    @patch('tkinter.Canvas')
    def test_start_transition(self, mock_canvas):
        """测试开始切换"""
        anim = ModeTransitionAnimation(mock_canvas)
        anim.start_transition("analog", "digital")
        
        self.assertEqual(anim.transition.from_mode, "analog")
        self.assertEqual(anim.transition.to_mode, "digital")
        self.assertTrue(anim.is_active())

    @patch('tkinter.Canvas')
    def test_update(self, mock_canvas):
        """测试更新"""
        anim = ModeTransitionAnimation(mock_canvas)
        anim.start_transition("analog", "digital")
        
        value = anim.update()
        
        self.assertGreater(value, 0.0)
        self.assertLessEqual(value, 1.0)


class TestThemeTransitionAnimation(unittest.TestCase):
    """测试主题切换动画"""

    @patch('tkinter.Canvas')
    def test_start_transition(self, mock_canvas):
        """测试开始切换"""
        anim = ThemeTransitionAnimation(mock_canvas)
        anim.start_transition()
        
        self.assertTrue(anim.is_active())

    @patch('tkinter.Canvas')
    def test_update(self, mock_canvas):
        """测试更新"""
        anim = ThemeTransitionAnimation(mock_canvas)
        anim.start_transition()
        
        value = anim.update()
        
        self.assertGreater(value, 0.0)
        self.assertLessEqual(value, 1.0)


class TestSmoothSecondHandAnimation(unittest.TestCase):
    """测试秒针平滑动画"""

    def test_set_target(self):
        """测试设置目标"""
        anim = SmoothSecondHandAnimation()
        anim.set_target(30)
        
        self.assertEqual(anim.target_second, 30)
        self.assertEqual(anim.target_angle, 180)  # 30 * 6

    def test_update(self):
        """测试更新"""
        anim = SmoothSecondHandAnimation()
        anim.set_target(15)
        
        value = anim.update()
        
        self.assertGreaterEqual(value, 0.0)
        self.assertLessEqual(value, 360.0)

    def test_lerp_angle(self):
        """测试角度插值"""
        anim = SmoothSecondHandAnimation()
        
        # 测试正常插值
        result = anim._lerp_angle(0, 90, 0.5)
        self.assertEqual(result, 45)
        
        # 测试环绕（从 350 到 10 度）
        result = anim._lerp_angle(350, 10, 0.5)
        self.assertLessEqual(result, 360)  # 应该走短路径


class TestDigitFlipAnimation(unittest.TestCase):
    """测试数字翻页动画"""

    @patch('tkinter.Canvas')
    def test_flip_digit(self, mock_canvas):
        """测试翻页"""
        anim = DigitFlipAnimation(mock_canvas)
        anim.flip_digit("5", "6")
        
        self.assertTrue(anim.is_flipping())
        self.assertEqual(anim.flip.current_digit, "5")
        self.assertEqual(anim.flip.next_digit, "6")

    @patch('tkinter.Canvas')
    def test_flip_same_digit(self, mock_canvas):
        """测试相同数字不翻页"""
        anim = DigitFlipAnimation(mock_canvas)
        anim.flip_digit("5", "5")
        
        self.assertFalse(anim.is_flipping())

    @patch('tkinter.Canvas')
    def test_update(self, mock_canvas):
        """测试更新"""
        anim = DigitFlipAnimation(mock_canvas)
        anim.flip_digit("1", "2")
        
        # 模拟完成
        import time
        original_time = time.time
        time.time = lambda: original_time() + 1.0
        
        value = anim.update()
        
        self.assertEqual(value, 1.0)
        self.assertFalse(anim.is_flipping())
        
        time.time = original_time


class TestAnimationConfig(unittest.TestCase):
    """测试动画配置"""

    def test_default_config(self):
        """测试默认配置"""
        config = AnimationConfig()
        
        self.assertTrue(config.hour_chime_enabled)
        self.assertTrue(config.mode_transition_enabled)
        self.assertTrue(config.theme_transition_enabled)
        self.assertTrue(config.smooth_second_hand)
        self.assertTrue(config.digit_flip_enabled)

    def test_from_dict(self):
        """测试从字典创建"""
        data = {
            "hour_chime_enabled": False,
            "smooth_second_hand": False,
            "digit_flip_enabled": True
        }
        config = AnimationConfig.from_dict(data)
        
        self.assertFalse(config.hour_chime_enabled)
        self.assertFalse(config.smooth_second_hand)
        self.assertTrue(config.digit_flip_enabled)
        # 默认值
        self.assertTrue(config.mode_transition_enabled)


class TestColorInterpolation(unittest.TestCase):
    """测试颜色插值"""

    def test_interpolate_color(self):
        """测试颜色插值"""
        # 黑色到白色
        result = interpolate_color("#000000", "#ffffff", 0.5)
        self.assertIn(result, ["#7f7f7f", "#808080"])  # 允许舍入误差
        
        # 红色到蓝色
        result = interpolate_color("#ff0000", "#0000ff", 0.5)
        self.assertIn(result, ["#7f007f", "#800080"])  # 紫色，允许舍入误差

    def test_interpolate_color_endpoints(self):
        """测试端点"""
        self.assertEqual(interpolate_color("#ff0000", "#00ff00", 0.0), "#ff0000")
        self.assertEqual(interpolate_color("#ff0000", "#00ff00", 1.0), "#00ff00")

    def test_create_gradient_colors(self):
        """测试创建渐变色"""
        colors = create_gradient_colors("#000000", "#ffffff", 5)
        
        self.assertEqual(len(colors), 5)
        self.assertEqual(colors[0], "#000000")
        self.assertEqual(colors[4], "#ffffff")


class TestIntegration(unittest.TestCase):
    """集成测试"""

    @patch('tkinter.Canvas')
    def test_full_animation_workflow(self, mock_canvas):
        """测试完整动画流程"""
        # 创建多个动画
        hour_chime = HourChimeAnimation(mock_canvas)
        mode_transition = ModeTransitionAnimation(mock_canvas)
        theme_transition = ThemeTransitionAnimation(mock_canvas)
        
        # 触发整点报时
        hour_chime.effect.enabled = True
        hour_chime.trigger(12)
        
        # 开始模式切换
        mode_transition.start_transition("analog", "digital")
        
        # 开始主题切换
        theme_transition.start_transition()
        
        # 所有动画都应该活跃
        self.assertTrue(hour_chime.is_active())
        self.assertTrue(mode_transition.is_active())
        self.assertTrue(theme_transition.is_active())
        
        # 更新所有动画
        hour_chime.update()
        mode_transition.update()
        theme_transition.update()


if __name__ == '__main__':
    unittest.main()
