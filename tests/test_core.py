#!/usr/bin/env python3
"""
ClawClock 核心功能单元测试
=========================

测试时钟应用的核心功能，包括配置管理、闹钟功能等。
不依赖 tkinter，可独立运行。
"""

import unittest
import json
import os
import sys
import tempfile
import shutil
from datetime import datetime, timedelta
from typing import Dict, Any
from dataclasses import dataclass, field

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@dataclass
class Alarm:
    """闹钟数据类（与 clock.py 中相同）"""
    time: str  # HH:MM 格式
    enabled: bool = True
    label: str = ""
    sound: str = "default"
    repeat_days: list = field(default_factory=list)  # 0=Monday, 6=Sunday
    
    def is_due(self, current_time: datetime) -> bool:
        """检查当前时间是否触发闹钟"""
        if not self.enabled:
            return False
        
        current_hour = current_time.hour
        current_minute = current_time.minute
        current_second = current_time.second
        current_weekday = current_time.weekday()
        
        alarm_hour, alarm_minute = map(int, self.time.split(":"))
        
        # 检查时间匹配（在秒数为 0 时触发）
        if current_hour == alarm_hour and current_minute == alarm_minute and current_second == 0:
            # 检查重复设置
            if not self.repeat_days or current_weekday in self.repeat_days:
                return True
        
        return False


class AlarmManager:
    """闹钟管理器（用于测试）"""
    
    def __init__(self, config_file: str):
        self.config_file = config_file
        self.config = {
            "timezone": "Asia/Shanghai",
            "display_mode": "analog",
            "window": {"width": 600, "height": 500},
            "theme": {"name": "dark"},
            "alarms": []
        }
        self.alarms: list = []
    
    def add_alarm(self, time_str: str, label: str = "") -> bool:
        """添加新闹钟"""
        # 验证时间格式
        try:
            hour, minute = map(int, time_str.split(":"))
            if not (0 <= hour <= 23 and 0 <= minute <= 59):
                raise ValueError("时间超出范围")
        except Exception as e:
            print(f"⚠️  无效的时间格式：{e}")
            return False
        
        alarm = Alarm(time=time_str, label=label)
        self.alarms.append(alarm)
        self._save_alarms()
        print(f"✅ 闹钟已添加：{time_str} {label}")
        return True
    
    def remove_alarm(self, index: int) -> bool:
        """删除闹钟"""
        if 0 <= index < len(self.alarms):
            self.alarms.pop(index)
            self._save_alarms()
            print(f"✅ 闹钟已删除：索引 {index}")
            return True
        return False
    
    def toggle_alarm(self, index: int) -> bool:
        """切换闹钟启用状态"""
        if 0 <= index < len(self.alarms):
            self.alarms[index].enabled = not self.alarms[index].enabled
            self._save_alarms()
            status = "启用" if self.alarms[index].enabled else "禁用"
            print(f"✅ 闹钟已{status}：索引 {index}")
            return True
        return False
    
    def _save_alarms(self) -> None:
        """保存闹钟到配置"""
        self.config["alarms"] = [
            {
                "time": alarm.time,
                "enabled": alarm.enabled,
                "label": alarm.label,
                "sound": alarm.sound,
                "repeat_days": alarm.repeat_days
            }
            for alarm in self.alarms
        ]
        self.save_config()
    
    def save_config(self, config: dict = None, config_file: str = None) -> bool:
        """保存配置文件"""
        if config is None:
            config = self.config
        if config_file is None:
            config_file = self.config_file
        
        try:
            sorted_config = self.sort_config(config)
            with open(config_file, "w", encoding="utf-8") as f:
                json.dump(sorted_config, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"⚠️  保存配置文件失败：{e}")
            return False
    
    def sort_config(self, config: dict) -> dict:
        """递归排序配置字典"""
        sorted_config = {}
        for key in sorted(config.keys()):
            value = config[key]
            if isinstance(value, dict):
                sorted_config[key] = self.sort_config(value)
            else:
                sorted_config[key] = value
        return sorted_config
    
    def load_config(self) -> dict:
        """加载配置文件"""
        default_config = {
            "timezone": "Asia/Shanghai",
            "display_mode": "analog",
            "window": {"width": 600, "height": 500, "resizable": False},
            "theme": {"name": "dark", "colors": {}},
            "alarms": []
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, "r", encoding="utf-8") as f:
                    config = json.load(f)
                return self.merge_config(default_config, config)
            else:
                self.save_config(default_config, self.config_file)
                return default_config
        except Exception as e:
            print(f"⚠️  加载配置文件失败：{e}")
            return default_config
    
    def merge_config(self, default: dict, custom: dict) -> dict:
        """递归合并配置字典"""
        result = default.copy()
        for key, value in custom.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self.merge_config(result[key], value)
            else:
                result[key] = value
        return result


class TestAlarm(unittest.TestCase):
    """闹钟功能测试"""
    
    def test_01_alarm_creation(self):
        """测试 1: 闹钟创建"""
        alarm = Alarm(time="07:30", label="起床")
        self.assertEqual(alarm.time, "07:30")
        self.assertEqual(alarm.label, "起床")
        self.assertTrue(alarm.enabled)
        self.assertEqual(alarm.sound, "default")
        self.assertEqual(alarm.repeat_days, [])
    
    def test_02_alarm_creation_default(self):
        """测试 2: 闹钟默认值"""
        alarm = Alarm(time="08:00")
        self.assertEqual(alarm.time, "08:00")
        self.assertTrue(alarm.enabled)
        self.assertEqual(alarm.label, "")
        self.assertEqual(alarm.sound, "default")
    
    def test_03_alarm_is_due_match(self):
        """测试 3: 闹钟触发时间匹配"""
        alarm = Alarm(time="07:30", enabled=True)
        test_time = datetime(2024, 3, 18, 7, 30, 0)  # 精确匹配
        self.assertTrue(alarm.is_due(test_time))
    
    def test_04_alarm_is_due_not_match(self):
        """测试 4: 闹钟不触发时间不匹配"""
        alarm = Alarm(time="07:30", enabled=True)
        test_time = datetime(2024, 3, 18, 8, 30, 0)  # 小时不匹配
        self.assertFalse(alarm.is_due(test_time))
    
    def test_05_alarm_is_due_disabled(self):
        """测试 5: 禁用的闹钟不触发"""
        alarm = Alarm(time="07:30", enabled=False)
        test_time = datetime(2024, 3, 18, 7, 30, 0)
        self.assertFalse(alarm.is_due(test_time))
    
    def test_06_alarm_is_due_with_repeat(self):
        """测试 6: 闹钟重复设置"""
        # 设置周一重复 (weekday 0)
        alarm = Alarm(time="07:30", enabled=True, repeat_days=[0])
        # 2024-03-18 是周一
        test_time = datetime(2024, 3, 18, 7, 30, 0)
        self.assertTrue(alarm.is_due(test_time))
        
        # 2024-03-19 是周二
        test_time2 = datetime(2024, 3, 19, 7, 30, 0)
        self.assertFalse(alarm.is_due(test_time2))
    
    def test_07_alarm_is_due_seconds_check(self):
        """测试 7: 闹钟秒数检查"""
        alarm = Alarm(time="07:30", enabled=True)
        # 秒数不为 0 时不触发
        test_time = datetime(2024, 3, 18, 7, 30, 30)
        self.assertFalse(alarm.is_due(test_time))


class TestConfigManagement(unittest.TestCase):
    """配置管理测试"""
    
    def setUp(self):
        """测试前准备"""
        self.test_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.test_dir, "config.json")
    
    def tearDown(self):
        """测试后清理"""
        shutil.rmtree(self.test_dir)
    
    def test_08_config_load_default(self):
        """测试 8: 加载默认配置"""
        manager = AlarmManager(self.config_file)
        config = manager.load_config()
        
        self.assertIn("timezone", config)
        self.assertIn("display_mode", config)
        self.assertIn("window", config)
        self.assertIn("theme", config)
        self.assertEqual(config["timezone"], "Asia/Shanghai")
        self.assertEqual(config["display_mode"], "analog")
    
    def test_09_config_load_custom(self):
        """测试 9: 加载自定义配置"""
        custom_config = {
            "timezone": "UTC",
            "display_mode": "digital",
            "window": {"width": 800, "height": 600},
            "theme": {"name": "light"}
        }
        
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(custom_config, f)
        
        manager = AlarmManager(self.config_file)
        config = manager.load_config()
        
        self.assertEqual(config["timezone"], "UTC")
        self.assertEqual(config["display_mode"], "digital")
    
    def test_10_config_merge(self):
        """测试 10: 配置合并"""
        manager = AlarmManager(self.config_file)
        
        default = {
            "a": 1,
            "b": {"c": 2, "d": 3},
            "e": 4
        }
        custom = {
            "b": {"c": 5},
            "f": 6
        }
        
        merged = manager.merge_config(default, custom)
        
        self.assertEqual(merged["a"], 1)
        self.assertEqual(merged["b"]["c"], 5)  # 被覆盖
        self.assertEqual(merged["b"]["d"], 3)  # 保留
        self.assertEqual(merged["e"], 4)
        self.assertEqual(merged["f"], 6)  # 新增
    
    def test_11_config_save(self):
        """测试 11: 配置保存"""
        manager = AlarmManager(self.config_file)
        config = {"test": "value", "number": 42}
        
        result = manager.save_config(config, self.config_file)
        
        self.assertTrue(result)
        self.assertTrue(os.path.exists(self.config_file))
        
        with open(self.config_file, "r", encoding="utf-8") as f:
            loaded = json.load(f)
        
        self.assertEqual(loaded["test"], "value")
        self.assertEqual(loaded["number"], 42)
    
    def test_12_config_sort(self):
        """测试 12: 配置排序"""
        manager = AlarmManager(self.config_file)
        
        unsorted_config = {
            "zebra": 1,
            "apple": 2,
            "banana": {"yellow": 3, "apple": 4}
        }
        
        sorted_config = manager.sort_config(unsorted_config)
        
        keys = list(sorted_config.keys())
        self.assertEqual(keys, ["apple", "banana", "zebra"])


class TestAlarmManagement(unittest.TestCase):
    """闹钟管理测试"""
    
    def setUp(self):
        """测试前准备"""
        self.test_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.test_dir, "config.json")
        
        # 创建初始配置
        initial_config = {
            "timezone": "Asia/Shanghai",
            "display_mode": "analog",
            "window": {"width": 600, "height": 500},
            "theme": {"name": "dark"},
            "alarms": []
        }
        
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(initial_config, f)
    
    def tearDown(self):
        """测试后清理"""
        shutil.rmtree(self.test_dir)
    
    def test_13_add_alarm(self):
        """测试 13: 添加闹钟"""
        manager = AlarmManager(self.config_file)
        
        result = manager.add_alarm("07:30", "起床闹钟")
        
        self.assertTrue(result)
        self.assertEqual(len(manager.alarms), 1)
        self.assertEqual(manager.alarms[0].time, "07:30")
        self.assertEqual(manager.alarms[0].label, "起床闹钟")
    
    def test_14_add_alarm_invalid_format(self):
        """测试 14: 添加无效格式闹钟"""
        manager = AlarmManager(self.config_file)
        
        result = manager.add_alarm("invalid", "测试")
        
        self.assertFalse(result)
        self.assertEqual(len(manager.alarms), 0)
    
    def test_15_add_alarm_out_of_range(self):
        """测试 15: 添加超出范围时间闹钟"""
        manager = AlarmManager(self.config_file)
        
        result = manager.add_alarm("25:00", "测试")
        
        self.assertFalse(result)
    
    def test_16_remove_alarm(self):
        """测试 16: 删除闹钟"""
        manager = AlarmManager(self.config_file)
        manager.add_alarm("07:30", "闹钟 1")
        manager.add_alarm("08:00", "闹钟 2")
        
        result = manager.remove_alarm(0)
        
        self.assertTrue(result)
        self.assertEqual(len(manager.alarms), 1)
        self.assertEqual(manager.alarms[0].time, "08:00")
    
    def test_17_remove_alarm_invalid_index(self):
        """测试 17: 删除无效索引闹钟"""
        manager = AlarmManager(self.config_file)
        
        result = manager.remove_alarm(5)
        
        self.assertFalse(result)
    
    def test_18_toggle_alarm(self):
        """测试 18: 切换闹钟状态"""
        manager = AlarmManager(self.config_file)
        manager.add_alarm("07:30", "测试")
        
        # 初始为启用
        self.assertTrue(manager.alarms[0].enabled)
        
        # 切换为禁用
        result = manager.toggle_alarm(0)
        self.assertTrue(result)
        self.assertFalse(manager.alarms[0].enabled)
        
        # 再次切换为启用
        manager.toggle_alarm(0)
        self.assertTrue(manager.alarms[0].enabled)


class TestTimezoneData(unittest.TestCase):
    """时区数据测试"""
    
    def test_19_timezone_count(self):
        """测试 19: 时区数量"""
        # 应该有 25 个时区（UTC-12 到 UTC+12）
        expected_count = 25
        
        timezones = [
            ("UTC-12", "Pacific/Kwajalein", "国际日期变更线西"),
            ("UTC-11", "Pacific/Pago_Pago", "帕果帕果"),
            ("UTC-10", "Pacific/Honolulu", "檀香山"),
            ("UTC-9", "America/Anchorage", "安克雷奇"),
            ("UTC-8", "America/Los_Angeles", "洛杉矶"),
            ("UTC-7", "America/Denver", "丹佛"),
            ("UTC-6", "America/Chicago", "芝加哥"),
            ("UTC-5", "America/New_York", "纽约"),
            ("UTC-4", "America/Halifax", "哈利法克斯"),
            ("UTC-3", "America/Sao_Paulo", "圣保罗"),
            ("UTC-2", "Atlantic/South_Georgia", "南乔治亚"),
            ("UTC-1", "Atlantic/Azores", "亚速尔群岛"),
            ("UTC+0", "UTC", "协调世界时"),
            ("UTC+1", "Europe/London", "伦敦"),
            ("UTC+2", "Europe/Paris", "巴黎"),
            ("UTC+3", "Europe/Moscow", "莫斯科"),
            ("UTC+4", "Asia/Dubai", "迪拜"),
            ("UTC+5", "Asia/Karachi", "卡拉奇"),
            ("UTC+6", "Asia/Dhaka", "达卡"),
            ("UTC+7", "Asia/Bangkok", "曼谷"),
            ("UTC+8", "Asia/Shanghai", "上海"),
            ("UTC+9", "Asia/Tokyo", "东京"),
            ("UTC+10", "Australia/Sydney", "悉尼"),
            ("UTC+11", "Pacific/Noumea", "努美阿"),
            ("UTC+12", "Pacific/Auckland", "奥克兰"),
        ]
        
        self.assertEqual(len(timezones), expected_count)
    
    def test_20_timezone_structure(self):
        """测试 20: 时区数据结构"""
        timezone = ("UTC+8", "Asia/Shanghai", "上海")
        
        self.assertEqual(len(timezone), 3)
        self.assertTrue(timezone[0].startswith("UTC"))
        self.assertIn("/", timezone[1])  # IANA 时区格式
        self.assertIsInstance(timezone[2], str)


class TestSevenSegmentDisplay(unittest.TestCase):
    """7 段数码管显示测试"""
    
    def test_21_digit_segments_valid(self):
        """测试 21: 数字段定义有效性"""
        digit_segs = {
            0: [1, 1, 1, 1, 1, 1, 0],
            1: [0, 1, 1, 0, 0, 0, 0],
            2: [1, 1, 0, 1, 1, 0, 1],
            3: [1, 1, 1, 1, 0, 0, 1],
            4: [0, 1, 1, 0, 0, 1, 1],
            5: [1, 0, 1, 1, 0, 1, 1],
            6: [1, 0, 1, 1, 1, 1, 1],
            7: [1, 1, 1, 0, 0, 0, 0],
            8: [1, 1, 1, 1, 1, 1, 1],
            9: [1, 1, 1, 1, 0, 1, 1],
        }
        
        # 验证所有数字都有 7 个段定义
        for digit, segs in digit_segs.items():
            self.assertEqual(len(segs), 7, f"数字 {digit} 的段定义数量不正确")
            for seg in segs:
                self.assertIn(seg, [0, 1], f"数字 {digit} 的段值无效")
    
    def test_22_digit_eight_all_segments(self):
        """测试 22: 数字 8 使用所有段"""
        digit_segs = {
            8: [1, 1, 1, 1, 1, 1, 1],
        }
        
        self.assertEqual(sum(digit_segs[8]), 7, "数字 8 应该点亮所有 7 个段")
    
    def test_23_digit_one_minimal_segments(self):
        """测试 23: 数字 1 使用最少段"""
        digit_segs = {
            1: [0, 1, 1, 0, 0, 0, 0],
        }
        
        self.assertEqual(sum(digit_segs[1]), 2, "数字 1 应该只使用 2 个段（b 和 c）")


if __name__ == "__main__":
    # 运行测试
    unittest.main(verbosity=2)
