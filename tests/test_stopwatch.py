#!/usr/bin/env python3
"""
ClawClock 秒表功能测试
=====================

测试秒表核心功能：开始/停止/复位/计圈
"""

import json
import os
import sys
import time
import unittest
from unittest.mock import Mock, patch, MagicMock
import datetime

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock tkinter 以在无 GUI 环境下测试
sys.modules['tkinter'] = MagicMock()
sys.modules['tkinter.ttk'] = MagicMock()

from clock import StopwatchState, LapRecord, ClockApp


class TestStopwatchState(unittest.TestCase):
    """测试秒表状态数据类"""
    
    def test_initial_state(self):
        """测试秒表初始状态"""
        state = StopwatchState()
        self.assertFalse(state.is_running)
        self.assertEqual(state.start_time, 0.0)
        self.assertEqual(state.elapsed_ms, 0)
        self.assertEqual(len(state.laps), 0)
    
    def test_lap_record_creation(self):
        """测试计圈记录创建"""
        lap = LapRecord(lap_number=1, time_ms=5000, split_ms=5000)
        self.assertEqual(lap.lap_number, 1)
        self.assertEqual(lap.time_ms, 5000)
        self.assertEqual(lap.split_ms, 5000)
        self.assertIsInstance(lap.timestamp, datetime.datetime)
    
    def test_lap_record_with_custom_timestamp(self):
        """测试带自定义时间戳的计圈记录"""
        custom_time = datetime.datetime(2026, 3, 18, 12, 0, 0)
        lap = LapRecord(lap_number=2, time_ms=10000, split_ms=5000, timestamp=custom_time)
        self.assertEqual(lap.timestamp, custom_time)


class TestStopwatchFunctions(unittest.TestCase):
    """测试秒表核心功能"""
    
    def setUp(self):
        """测试前准备"""
        # 创建 Mock 的 Tk 根窗口
        self.mock_root = Mock()
        self.mock_root.geometry.return_value = "600x500+0+0"
        self.mock_root.resizable.return_value = (False, False)
        self.mock_root.winfo_x.return_value = 0
        self.mock_root.winfo_y.return_value = 0
        self.mock_root.winfo_width.return_value = 600
        self.mock_root.winfo_height.return_value = 500
        
        # Mock after 方法
        self.mock_root.after = Mock(return_value="job_1")
        self.mock_root.after_cancel = Mock()
        
        # 创建应用实例（需要 Mock tkinter 组件）
        with patch('clock.tk.Tk', return_value=self.mock_root):
            with patch('clock.ttk.Style'):
                with patch('clock.os.path.exists', return_value=False):
                    self.app = ClockApp.__new__(ClockApp)
                    self.app.root = self.mock_root
                    self.app.config = {
                        "display_mode": "analog",
                        "theme": {"name": "dark", "colors": {}},
                        "timezone": "Asia/Shanghai",
                        "window": {"width": 600, "height": 500}
                    }
                    self.app.stopwatch = StopwatchState()
                    self.app.stopwatch_job = None
                    
                    # Mock UI 组件
                    self.app.stopwatch_canvas = Mock()
                    self.app.lap_listbox = Mock()
                    self.app.sw_start_btn = Mock()
                    self.app.sw_stop_btn = Mock()
                    self.app.sw_lap_btn = Mock()
                    self.app.sw_reset_btn = Mock()
                    
                    # 设置颜色
                    self.app.seg_color_on = "#ff3333"
                    self.app.text_color = "#ffffff"
                    self.app.bg_color = "#1a1a2e"
    
    def test_format_stopwatch_time_zero(self):
        """测试格式化零时间"""
        # 需要创建真实实例来测试这个方法
        mock_root = Mock()
        mock_root.geometry.return_value = "600x500+0+0"
        
        with patch('clock.tk.Tk', return_value=mock_root):
            with patch('clock.ttk.Style'):
                with patch('clock.os.path.exists', return_value=False):
                    app = ClockApp.__new__(ClockApp)
                    app.root = mock_root
                    app.stopwatch = StopwatchState()
                    
                    result = app.format_stopwatch_time(0)
                    self.assertEqual(result, "00:00.00")
    
    def test_format_stopwatch_time_simple(self):
        """测试格式化简单时间"""
        mock_root = Mock()
        mock_root.geometry.return_value = "600x500+0+0"
        
        with patch('clock.tk.Tk', return_value=mock_root):
            with patch('clock.ttk.Style'):
                with patch('clock.os.path.exists', return_value=False):
                    app = ClockApp.__new__(ClockApp)
                    app.root = mock_root
                    app.stopwatch = StopwatchState()
                    
                    # 1 分 23 秒 45 毫秒 = 83045ms
                    result = app.format_stopwatch_time(83045)
                    self.assertEqual(result, "01:23.04")  # 45ms 显示为 2 位是 04（除以 10）
    
    def test_format_stopwatch_time_hours(self):
        """测试格式化超过 1 小时的时间"""
        mock_root = Mock()
        mock_root.geometry.return_value = "600x500+0+0"
        
        with patch('clock.tk.Tk', return_value=mock_root):
            with patch('clock.ttk.Style'):
                with patch('clock.os.path.exists', return_value=False):
                    app = ClockApp.__new__(ClockApp)
                    app.root = mock_root
                    app.stopwatch = StopwatchState()
                    
                    # 2 小时 15 分 30 秒
                    result = app.format_stopwatch_time(8130000)
                    self.assertEqual(result, "135:30.00")
    
    def test_stopwatch_start(self):
        """测试秒表开始功能"""
        self.app.stopwatch_start()
        
        self.assertTrue(self.app.stopwatch.is_running)
        self.assertNotEqual(self.app.stopwatch.start_time, 0.0)
        self.app.root.after.assert_called_once()
        self.app.sw_start_btn.config.assert_called()
        self.app.sw_stop_btn.config.assert_called()
        self.app.sw_lap_btn.config.assert_called()
    
    def test_stopwatch_stop(self):
        """测试秒表停止功能"""
        # 先开始
        self.app.stopwatch.is_running = True
        self.app.stopwatch.start_time = time.time()
        self.app.stopwatch_job = "job_1"
        
        # 然后停止
        self.app.stopwatch_stop()
        
        self.assertFalse(self.app.stopwatch.is_running)
        self.app.root.after_cancel.assert_called_once_with("job_1")
        self.app.sw_start_btn.config.assert_called()
        self.app.sw_stop_btn.config.assert_called()
        self.app.sw_lap_btn.config.assert_called()
    
    def test_stopwatch_reset(self):
        """测试秒表复位功能"""
        # 设置一些状态
        self.app.stopwatch.is_running = True
        self.app.stopwatch.elapsed_ms = 5000
        self.app.stopwatch.laps = [LapRecord(1, 5000, 5000)]
        
        # 复位
        self.app.stopwatch_reset()
        
        self.assertFalse(self.app.stopwatch.is_running)
        self.assertEqual(self.app.stopwatch.elapsed_ms, 0)
        self.assertEqual(len(self.app.stopwatch.laps), 0)
        # 验证调用了 delete 方法（不检查具体参数，因为 Mock 会改变 END 常量）
        self.app.lap_listbox.delete.assert_called_once()
    
    def test_stopwatch_lap_first(self):
        """测试第一次计圈"""
        self.app.stopwatch.is_running = True
        self.app.stopwatch.start_time = time.time()
        self.app.stopwatch.elapsed_ms = 0
        
        # 计圈
        self.app.stopwatch_lap()
        
        self.assertEqual(len(self.app.stopwatch.laps), 1)
        self.assertEqual(self.app.stopwatch.laps[0].lap_number, 1)
        self.app.lap_listbox.insert.assert_called_once()
    
    def test_stopwatch_lap_multiple(self):
        """测试多次计圈"""
        self.app.stopwatch.is_running = True
        self.app.stopwatch.start_time = time.time()
        self.app.stopwatch.elapsed_ms = 0
        
        # 计圈 3 次
        self.app.stopwatch_lap()
        time.sleep(0.01)
        self.app.stopwatch_lap()
        time.sleep(0.01)
        self.app.stopwatch_lap()
        
        self.assertEqual(len(self.app.stopwatch.laps), 3)
        self.assertEqual(self.app.stopwatch.laps[0].lap_number, 1)
        self.assertEqual(self.app.stopwatch.laps[1].lap_number, 2)
        self.assertEqual(self.app.stopwatch.laps[2].lap_number, 3)
    
    def test_stopwatch_lap_split_time(self):
        """测试计圈单圈时间计算"""
        self.app.stopwatch.is_running = True
        self.app.stopwatch.start_time = time.time()
        self.app.stopwatch.elapsed_ms = 0
        
        # 第一次计圈
        self.app.stopwatch_lap()
        first_time = self.app.stopwatch.laps[0].time_ms
        
        # 模拟过了一段时间后第二次计圈
        self.app.stopwatch.elapsed_ms += 5000
        self.app.stopwatch_lap()
        
        self.assertGreater(self.app.stopwatch.laps[1].time_ms, first_time)
        self.assertGreater(self.app.stopwatch.laps[1].split_ms, 0)
    
    def test_stopwatch_state_persistence(self):
        """测试秒表状态不会在重启后保留（预期行为）"""
        mock_root = Mock()
        mock_root.geometry.return_value = "600x500+0+0"
        
        with patch('clock.tk.Tk', return_value=mock_root):
            with patch('clock.ttk.Style'):
                with patch('clock.os.path.exists', return_value=False):
                    app = ClockApp.__new__(ClockApp)
                    app.root = mock_root
                    app.stopwatch = StopwatchState()
                    app.load_stopwatch_config()
                    
                    # 重启后应该重置
                    self.assertFalse(app.stopwatch.is_running)
                    self.assertEqual(app.stopwatch.elapsed_ms, 0)
                    self.assertEqual(len(app.stopwatch.laps), 0)


class TestStopwatchEdgeCases(unittest.TestCase):
    """测试秒表边界情况"""
    
    def test_stop_without_start(self):
        """测试未开始就停止"""
        mock_root = Mock()
        mock_root.geometry.return_value = "600x500+0+0"
        
        with patch('clock.tk.Tk', return_value=mock_root):
            with patch('clock.ttk.Style'):
                with patch('clock.os.path.exists', return_value=False):
                    app = ClockApp.__new__(ClockApp)
                    app.root = mock_root
                    app.stopwatch = StopwatchState()
                    app.stopwatch_job = None
                    app.sw_start_btn = Mock()
                    app.sw_stop_btn = Mock()
                    app.sw_lap_btn = Mock()
                    app.stopwatch_canvas = Mock()
                    
                    # 应该不报错
                    app.stopwatch_stop()
                    
                    self.assertFalse(app.stopwatch.is_running)
    
    def test_lap_without_start(self):
        """测试未开始就计圈"""
        mock_root = Mock()
        mock_root.geometry.return_value = "600x500+0+0"
        
        with patch('clock.tk.Tk', return_value=mock_root):
            with patch('clock.ttk.Style'):
                with patch('clock.os.path.exists', return_value=False):
                    app = ClockApp.__new__(ClockApp)
                    app.root = mock_root
                    app.stopwatch = StopwatchState()
                    app.lap_listbox = Mock()
                    
                    # 应该不报错，但不添加计圈记录
                    app.stopwatch_lap()
                    
                    self.assertEqual(len(app.stopwatch.laps), 0)
    
    def test_double_start(self):
        """测试重复开始"""
        mock_root = Mock()
        mock_root.geometry.return_value = "600x500+0+0"
        
        with patch('clock.tk.Tk', return_value=mock_root):
            with patch('clock.ttk.Style'):
                with patch('clock.os.path.exists', return_value=False):
                    app = ClockApp.__new__(ClockApp)
                    app.root = mock_root
                    app.stopwatch = StopwatchState()
                    app.stopwatch_job = None
                    app.sw_start_btn = Mock()
                    app.sw_stop_btn = Mock()
                    app.sw_lap_btn = Mock()
                    
                    # 第一次开始
                    app.stopwatch_start()
                    first_start_time = app.stopwatch.start_time
                    
                    time.sleep(0.01)
                    
                    # 第二次开始（应该无效）
                    app.stopwatch_start()
                    
                    # 开始时间应该不变
                    self.assertEqual(app.stopwatch.start_time, first_start_time)
    
    def test_reset_while_running(self):
        """测试在运行时复位"""
        mock_root = Mock()
        mock_root.geometry.return_value = "600x500+0+0"
        
        with patch('clock.tk.Tk', return_value=mock_root):
            with patch('clock.ttk.Style'):
                with patch('clock.os.path.exists', return_value=False):
                    app = ClockApp.__new__(ClockApp)
                    app.root = mock_root
                    app.stopwatch = StopwatchState()
                    app.stopwatch_job = None
                    app.sw_start_btn = Mock()
                    app.sw_stop_btn = Mock()
                    app.sw_lap_btn = Mock()
                    app.sw_reset_btn = Mock()
                    app.lap_listbox = Mock()
                    app.stopwatch_canvas = Mock()
                    app.seg_color_on = "#ff3333"
                    app.text_color = "#ffffff"
                    app.bg_color = "#1a1a2e"
                    
                    # 开始计时
                    app.stopwatch_start()
                    self.assertTrue(app.stopwatch.is_running)
                    
                    # 直接复位
                    app.stopwatch_reset()
                    
                    # 应该已停止并归零
                    self.assertFalse(app.stopwatch.is_running)
                    self.assertEqual(app.stopwatch.elapsed_ms, 0)


def run_tests():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("🧪 ClawClock 秒表功能测试")
    print("=" * 60)
    print()
    
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加测试
    suite.addTests(loader.loadTestsFromTestCase(TestStopwatchState))
    suite.addTests(loader.loadTestsFromTestCase(TestStopwatchFunctions))
    suite.addTests(loader.loadTestsFromTestCase(TestStopwatchEdgeCases))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 打印总结
    print()
    print("=" * 60)
    print(f"📊 测试结果：{result.testsRun} 项测试")
    print(f"   ✅ 通过：{result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"   ❌ 失败：{len(result.failures)}")
    print(f"   ⚠️  错误：{len(result.errors)}")
    print("=" * 60)
    
    return len(result.failures) == 0 and len(result.errors) == 0


if __name__ == "__main__":
    import tkinter as tk
    success = run_tests()
    sys.exit(0 if success else 1)
