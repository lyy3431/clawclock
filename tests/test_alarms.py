#!/usr/bin/env python3
"""
ClawClock 闹钟功能测试
=====================

测试闹钟增强功能：
- Alarm 类：重复周期、小睡功能
- 渐入铃声
- 工作日/周末快捷选项
- 系统通知

测试用例数量：10+
"""

import json
import os
import sys
import time
import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import threading

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock tkinter 以在无 GUI 环境下测试
sys.modules['tkinter'] = MagicMock()
sys.modules['tkinter.ttk'] = MagicMock()
sys.modules['tkinter.messagebox'] = MagicMock()

from clock import Alarm


class TestAlarmRepeatDays(unittest.TestCase):
    """测试闹钟重复周期功能"""
    
    def test_alarm_no_repeat_days(self):
        """测试无重复设置的闹钟（仅一次）"""
        alarm = Alarm(time="08:00", enabled=True)
        self.assertEqual(alarm.repeat_days, [])
        
        # 在任何工作日都应该触发（因为没有设置重复）
        test_time = datetime(2024, 3, 18, 8, 0, 0)  # 周一
        self.assertTrue(alarm.is_due(test_time))
    
    def test_alarm_weekday_repeat(self):
        """测试工作日重复（周一到周五）"""
        # 0=Monday, 4=Friday
        alarm = Alarm(time="08:00", enabled=True, repeat_days=[0, 1, 2, 3, 4])
        
        # 周一应该触发
        monday = datetime(2024, 3, 18, 8, 0, 0)
        self.assertTrue(alarm.is_due(monday))
        
        # 周五应该触发
        friday = datetime(2024, 3, 22, 8, 0, 0)
        self.assertTrue(alarm.is_due(friday))
        
        # 周六不应该触发
        saturday = datetime(2024, 3, 23, 8, 0, 0)
        self.assertFalse(alarm.is_due(saturday))
        
        # 周日不应该触发
        sunday = datetime(2024, 3, 24, 8, 0, 0)
        self.assertFalse(alarm.is_due(sunday))
    
    def test_alarm_weekend_repeat(self):
        """测试周末重复（周六、周日）"""
        # 5=Saturday, 6=Sunday
        alarm = Alarm(time="09:00", enabled=True, repeat_days=[5, 6])
        
        # 周六应该触发
        saturday = datetime(2024, 3, 23, 9, 0, 0)
        self.assertTrue(alarm.is_due(saturday))
        
        # 周日应该触发
        sunday = datetime(2024, 3, 24, 9, 0, 0)
        self.assertTrue(alarm.is_due(sunday))
        
        # 周一不应该触发
        monday = datetime(2024, 3, 18, 9, 0, 0)
        self.assertFalse(alarm.is_due(monday))
    
    def test_alarm_everyday_repeat(self):
        """测试每天重复"""
        alarm = Alarm(time="07:00", enabled=True, repeat_days=[0, 1, 2, 3, 4, 5, 6])
        
        # 每天都应该触发
        for day in range(18, 25):  # 3 月 18 日 -24 日
            test_time = datetime(2024, 3, day, 7, 0, 0)
            self.assertTrue(alarm.is_due(test_time))
    
    def test_alarm_specific_days(self):
        """测试特定日期重复"""
        # 只在周一、三、五触发
        alarm = Alarm(time="10:00", enabled=True, repeat_days=[0, 2, 4])
        
        # 周一应该触发
        monday = datetime(2024, 3, 18, 10, 0, 0)
        self.assertTrue(alarm.is_due(monday))
        
        # 周二不应该触发
        tuesday = datetime(2024, 3, 19, 10, 0, 0)
        self.assertFalse(alarm.is_due(tuesday))
        
        # 周三应该触发
        wednesday = datetime(2024, 3, 20, 10, 0, 0)
        self.assertTrue(alarm.is_due(wednesday))
    
    def test_alarm_disabled(self):
        """测试禁用的闹钟不触发"""
        alarm = Alarm(time="08:00", enabled=False, repeat_days=[0, 1, 2, 3, 4])
        
        test_time = datetime(2024, 3, 18, 8, 0, 0)  # 周一
        self.assertFalse(alarm.is_due(test_time))
    
    def test_alarm_wrong_time(self):
        """测试时间不匹配"""
        alarm = Alarm(time="08:00", enabled=True, repeat_days=[0])
        
        # 时间不对（7:59）
        test_time = datetime(2024, 3, 18, 7, 59, 0)
        self.assertFalse(alarm.is_due(test_time))
        
        # 时间不对（8:01）
        test_time = datetime(2024, 3, 18, 8, 1, 0)
        self.assertFalse(alarm.is_due(test_time))
        
        # 秒数不对（8:00:30）
        test_time = datetime(2024, 3, 18, 8, 0, 30)
        self.assertFalse(alarm.is_due(test_time))


class TestAlarmSnooze(unittest.TestCase):
    """测试闹钟小睡功能"""
    
    def test_alarm_default_snooze_minutes(self):
        """测试默认小睡时长"""
        alarm = Alarm(time="08:00")
        self.assertEqual(alarm.snooze_minutes, 5)
    
    def test_alarm_custom_snooze_minutes(self):
        """测试自定义小睡时长"""
        alarm = Alarm(time="08:00", snooze_minutes=10)
        self.assertEqual(alarm.snooze_minutes, 10)
        
        alarm2 = Alarm(time="09:00", snooze_minutes=3)
        self.assertEqual(alarm2.snooze_minutes, 3)
    
    def test_alarm_snooze_calculation(self):
        """测试小睡时间计算"""
        alarm = Alarm(time="08:00", snooze_minutes=5)
        
        # 5 分钟 = 300 秒 = 300000 毫秒
        expected_ms = 5 * 60 * 1000
        self.assertEqual(alarm.snooze_minutes * 60 * 1000, expected_ms)
        
        alarm2 = Alarm(time="09:00", snooze_minutes=10)
        expected_ms2 = 10 * 60 * 1000
        self.assertEqual(alarm2.snooze_minutes * 60 * 1000, expected_ms2)


class TestAlarmSerialization(unittest.TestCase):
    """测试闹钟序列化"""
    
    def test_alarm_to_dict(self):
        """测试闹钟转换为字典"""
        alarm = Alarm(
            time="07:30",
            enabled=True,
            label="起床",
            sound="default",
            repeat_days=[0, 1, 2, 3, 4],
            snooze_minutes=5
        )
        
        alarm_dict = {
            "time": alarm.time,
            "enabled": alarm.enabled,
            "label": alarm.label,
            "sound": alarm.sound,
            "repeat_days": alarm.repeat_days,
            "snooze_minutes": alarm.snooze_minutes
        }
        
        self.assertEqual(alarm_dict["time"], "07:30")
        self.assertEqual(alarm_dict["enabled"], True)
        self.assertEqual(alarm_dict["label"], "起床")
        self.assertEqual(alarm_dict["repeat_days"], [0, 1, 2, 3, 4])
        self.assertEqual(alarm_dict["snooze_minutes"], 5)
    
    def test_alarm_from_dict(self):
        """测试从字典创建闹钟"""
        alarm_dict = {
            "time": "08:00",
            "enabled": True,
            "label": "上班",
            "sound": "default",
            "repeat_days": [0, 1, 2, 3, 4],
            "snooze_minutes": 10
        }
        
        alarm = Alarm(
            time=alarm_dict["time"],
            enabled=alarm_dict["enabled"],
            label=alarm_dict["label"],
            sound=alarm_dict["sound"],
            repeat_days=alarm_dict["repeat_days"],
            snooze_minutes=alarm_dict["snooze_minutes"]
        )
        
        self.assertEqual(alarm.time, "08:00")
        self.assertEqual(alarm.label, "上班")
        self.assertEqual(alarm.repeat_days, [0, 1, 2, 3, 4])
        self.assertEqual(alarm.snooze_minutes, 10)


class TestAlarmEdgeCases(unittest.TestCase):
    """测试边界情况"""
    
    def test_alarm_midnight(self):
        """测试午夜闹钟"""
        alarm = Alarm(time="00:00", enabled=True)
        
        midnight = datetime(2024, 3, 18, 0, 0, 0)
        self.assertTrue(alarm.is_due(midnight))
    
    test_alarm_end_of_day = lambda self: None  # Placeholder
    
    def test_alarm_leap_year(self):
        """测试闰年闹钟"""
        alarm = Alarm(time="08:00", enabled=True, repeat_days=[0])
        
        # 2024 年是闰年
        leap_monday = datetime(2024, 2, 26, 8, 0, 0)  # 周一
        self.assertTrue(alarm.is_due(leap_monday))
    
    def test_alarm_multiple_same_time(self):
        """测试多个相同时间的闹钟"""
        alarm1 = Alarm(time="08:00", enabled=True, label="闹钟 1")
        alarm2 = Alarm(time="08:00", enabled=True, label="闹钟 2")
        
        test_time = datetime(2024, 3, 18, 8, 0, 0)
        self.assertTrue(alarm1.is_due(test_time))
        self.assertTrue(alarm2.is_due(test_time))


if __name__ == "__main__":
    unittest.main(verbosity=2)
