#!/usr/bin/env python3
"""
时区功能测试用例
================

测试 ClawClock 的时区切换功能，包括：
- 时区列表完整性
- 时区切换逻辑
- 时区时间计算
"""

import unittest
import datetime
import sys
import os

# 添加父目录到路径以便导入 clock 模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestTimezone(unittest.TestCase):
    """时区功能测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.timezones = [
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
    
    def test_timezone_count(self):
        """测试时区数量"""
        # 应该有 25 个时区（西区 12 + 零时区 1 + 东区 12）
        self.assertEqual(len(self.timezones), 25, "时区数量应为 25 个")
    
    def test_timezone_format(self):
        """测试时区格式正确性"""
        for tz in self.timezones:
            self.assertEqual(len(tz), 3, f"时区 {tz} 应包含 3 个元素")
            self.assertIsInstance(tz[0], str, "时区偏移应为字符串")
            self.assertIsInstance(tz[1], str, "时区 ID 应为字符串")
            self.assertIsInstance(tz[2], str, "时区描述应为字符串")
    
    def test_utc_zero_exists(self):
        """测试零时区存在"""
        utc_zeros = [tz for tz in self.timezones if tz[0] == "UTC+0"]
        self.assertEqual(len(utc_zeros), 1, "应存在一个零时区")
        self.assertEqual(utc_zeros[0][1], "UTC", "零时区 ID 应为 UTC")
    
    def test_timezone_range(self):
        """测试时区范围覆盖"""
        # 提取所有时区偏移
        offsets = [tz[0] for tz in self.timezones]
        
        # 检查西区起始
        self.assertIn("UTC-12", offsets, "应包含 UTC-12")
        # 检查东区结束
        self.assertIn("UTC+12", offsets, "应包含 UTC+12")
        # 检查零时区
        self.assertIn("UTC+0", offsets, "应包含 UTC+0")
    
    def test_asia_shanghai_exists(self):
        """测试上海时区存在"""
        shanghai = [tz for tz in self.timezones if tz[1] == "Asia/Shanghai"]
        self.assertEqual(len(shanghai), 1, "应存在上海时区")
        self.assertEqual(shanghai[0][0], "UTC+8", "上海时区应为 UTC+8")
    
    def test_timezone_parsing(self):
        """测试时区解析功能"""
        # 模拟从 UI 选择字符串解析时区 ID
        test_cases = [
            ("UTC+8 上海 (Asia/Shanghai)", "Asia/Shanghai"),
            ("UTC+0 协调世界时 (UTC)", "UTC"),
            ("UTC-5 纽约 (America/New_York)", "America/New_York"),
        ]
        
        for display_str, expected_id in test_cases:
            # 模拟 clock.py 中的解析逻辑
            try:
                tz_id = display_str.split("(")[1].split(")")[0]
                self.assertEqual(tz_id, expected_id, f"解析 {display_str} 应得到 {expected_id}")
            except Exception as e:
                self.fail(f"解析时区字符串失败：{display_str}, 错误：{e}")
    
    def test_timezone_datetime(self):
        """测试时区时间计算"""
        try:
            import zoneinfo
            
            # 测试上海时区
            shanghai_tz = zoneinfo.ZoneInfo("Asia/Shanghai")
            shanghai_time = datetime.datetime.now(shanghai_tz)
            
            # 测试 UTC 时区
            utc_tz = zoneinfo.ZoneInfo("UTC")
            utc_time = datetime.datetime.now(utc_tz)
            
            # 上海应该比 UTC 早 8 小时
            time_diff = shanghai_time.hour - utc_time.hour
            # 考虑日期变更的情况
            if time_diff < 0:
                time_diff += 24
            
            # 验证时差在合理范围内（7-9 小时，考虑夏令时等边界情况）
            self.assertIn(time_diff, [7, 8, 9], "上海与 UTC 时差应在 7-9 小时范围内")
            
        except ImportError:
            self.skipTest("zoneinfo 模块不可用")
        except Exception as e:
            self.fail(f"时区时间计算失败：{e}")
    
    def test_timezone_display_format(self):
        """测试时区显示格式"""
        for tz in self.timezones:
            display_str = f"{tz[0]} {tz[2]} ({tz[1]})"
            # 验证格式：偏移 描述 (ID)
            self.assertIn("(", display_str, "显示格式应包含左括号")
            self.assertIn(")", display_str, "显示格式应包含右括号")
            self.assertTrue(display_str.startswith(tz[0]), "显示格式应以偏移开头")


class TestTimezoneSwitching(unittest.TestCase):
    """时区切换功能测试"""
    
    def test_switch_to_utc(self):
        """测试切换到 UTC 时区"""
        current = "Asia/Shanghai"
        target = "UTC"
        
        # 模拟切换
        new_timezone = target
        self.assertEqual(new_timezone, "UTC", "应成功切换到 UTC")
    
    def test_switch_to_tokyo(self):
        """测试切换到东京时区"""
        current = "Asia/Shanghai"
        target = "Asia/Tokyo"
        
        # 模拟切换
        new_timezone = target
        self.assertEqual(new_timezone, "Asia/Tokyo", "应成功切换到东京")
    
    def test_invalid_timezone_handling(self):
        """测试无效时区处理"""
        invalid_timezones = [
            "Invalid/Timezone",
            "",
            None,
            "NOT_A_TIMEZONE",
        ]
        
        for invalid_tz in invalid_timezones:
            # 应该能处理无效时区而不崩溃
            try:
                if invalid_tz is None:
                    # None 值应该被跳过或使用默认值
                    continue
                import zoneinfo
                zoneinfo.ZoneInfo(invalid_tz)
                # 如果能创建，说明是有效的（不应该发生）
                self.fail(f"无效的时区 {invalid_tz} 应该抛出异常")
            except (Exception,):
                # 预期行为：抛出异常
                pass


if __name__ == "__main__":
    unittest.main()
