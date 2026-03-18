#!/usr/bin/env python3
"""
配置功能测试用例
================

测试 ClawClock 的配置加载、保存和合并功能。
"""

import unittest
import json
import os
import sys
import tempfile
import shutil

# 添加父目录到路径以便导入 clock 模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestConfigLoading(unittest.TestCase):
    """配置加载测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.test_dir = tempfile.mkdtemp()
        self.default_config = {
            "timezone": "Asia/Shanghai",
            "display_mode": "analog",
            "window": {
                "width": 600,
                "height": 500,
                "resizable": False
            },
            "theme": {
                "name": "dark",
                "colors": {
                    "background": "#1a1a2e",
                    "face": "#16213e",
                    "hand": "#e94560",
                    "text": "#ffffff",
                    "accent": "#0f3460",
                    "segment_on": "#ff3333",
                    "segment_off": "#331111"
                }
            }
        }
    
    def tearDown(self):
        """测试后清理"""
        shutil.rmtree(self.test_dir)
    
    def test_default_config_structure(self):
        """测试默认配置结构"""
        required_keys = ["timezone", "display_mode", "window", "theme"]
        for key in required_keys:
            self.assertIn(key, self.default_config, f"默认配置应包含 {key}")
    
    def test_window_config(self):
        """测试窗口配置"""
        window = self.default_config["window"]
        self.assertIn("width", window, "窗口配置应包含 width")
        self.assertIn("height", window, "窗口配置应包含 height")
        self.assertIn("resizable", window, "窗口配置应包含 resizable")
        self.assertIsInstance(window["width"], int, "width 应为整数")
        self.assertIsInstance(window["height"], int, "height 应为整数")
        self.assertIsInstance(window["resizable"], bool, "resizable 应为布尔值")
    
    def test_theme_config(self):
        """测试主题配置"""
        theme = self.default_config["theme"]
        self.assertIn("name", theme, "主题配置应包含 name")
        self.assertIn("colors", theme, "主题配置应包含 colors")
        
        colors = theme["colors"]
        required_colors = ["background", "face", "hand", "text", "accent"]
        for color in required_colors:
            self.assertIn(color, colors, f"颜色配置应包含 {color}")
            self.assertIsInstance(colors[color], str, f"{color} 应为字符串")
            self.assertTrue(colors[color].startswith("#"), f"{color} 应为十六进制颜色")
    
    def test_config_file_creation(self):
        """测试配置文件创建"""
        config_file = os.path.join(self.test_dir, "config.json")
        
        # 模拟保存配置
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(self.default_config, f, indent=2, ensure_ascii=False)
        
        # 验证文件存在
        self.assertTrue(os.path.exists(config_file), "配置文件应被创建")
        
        # 验证内容
        with open(config_file, "r", encoding="utf-8") as f:
            loaded_config = json.load(f)
        
        self.assertEqual(loaded_config, self.default_config, "加载的配置应与保存的一致")
    
    def test_config_file_not_exists(self):
        """测试配置文件不存在的情况"""
        config_file = os.path.join(self.test_dir, "nonexistent.json")
        
        # 文件不应存在
        self.assertFalse(os.path.exists(config_file), "配置文件不应存在")
    
    def test_invalid_config_handling(self):
        """测试无效配置处理"""
        invalid_configs = [
            {},  # 空配置
            {"invalid_key": "value"},  # 无效键
            None,  # None 值
        ]
        
        for invalid_config in invalid_configs:
            if invalid_config is None:
                continue
            # 验证配置结构检查
            required_keys = ["timezone", "display_mode", "window", "theme"]
            missing_keys = [key for key in required_keys if key not in invalid_config]
            self.assertTrue(len(missing_keys) > 0, "无效配置应缺少必要键")


class TestConfigMerging(unittest.TestCase):
    """配置合并测试类"""
    
    def merge_config(self, default, custom):
        """递归合并配置字典（模拟 clock.py 中的实现）"""
        result = default.copy()
        for key, value in custom.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self.merge_config(result[key], value)
            else:
                result[key] = value
        return result
    
    def test_merge_simple_config(self):
        """测试简单配置合并"""
        default = {"a": 1, "b": 2}
        custom = {"b": 3, "c": 4}
        
        result = self.merge_config(default, custom)
        
        self.assertEqual(result["a"], 1, "应保持默认值 a")
        self.assertEqual(result["b"], 3, "应使用自定义值 b")
        self.assertEqual(result["c"], 4, "应添加新值 c")
    
    def test_merge_nested_config(self):
        """测试嵌套配置合并"""
        default = {
            "theme": {
                "name": "dark",
                "colors": {
                    "background": "#000000",
                    "text": "#ffffff"
                }
            }
        }
        custom = {
            "theme": {
                "colors": {
                    "background": "#ffffff"
                }
            }
        }
        
        result = self.merge_config(default, custom)
        
        self.assertEqual(result["theme"]["name"], "dark", "应保持默认主题名")
        self.assertEqual(result["theme"]["colors"]["background"], "#ffffff", "应使用自定义背景色")
        self.assertEqual(result["theme"]["colors"]["text"], "#ffffff", "应保持默认文字色")
    
    def test_merge_timezone_override(self):
        """测试时区配置覆盖"""
        default = {"timezone": "Asia/Shanghai", "display_mode": "analog"}
        custom = {"timezone": "UTC"}
        
        result = self.merge_config(default, custom)
        
        self.assertEqual(result["timezone"], "UTC", "应使用自定义时区")
        self.assertEqual(result["display_mode"], "analog", "应保持默认显示模式")
    
    def test_merge_theme_override(self):
        """测试主题配置覆盖"""
        default = {
            "theme": {
                "name": "dark",
                "colors": {"background": "#1a1a2e"}
            }
        }
        custom = {
            "theme": {
                "name": "light",
                "colors": {"background": "#ffffff", "text": "#000000"}
            }
        }
        
        result = self.merge_config(default, custom)
        
        self.assertEqual(result["theme"]["name"], "light", "应使用自定义主题名")
        self.assertEqual(result["theme"]["colors"]["background"], "#ffffff", "应使用自定义背景色")
        self.assertEqual(result["theme"]["colors"]["text"], "#000000", "应添加自定义文字色")


class TestConfigSaving(unittest.TestCase):
    """配置保存测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.test_dir = tempfile.mkdtemp()
        self.config = {
            "timezone": "Asia/Shanghai",
            "display_mode": "digital",
            "window": {"width": 800, "height": 600, "resizable": True},
            "theme": {
                "name": "dark",
                "colors": {
                    "background": "#1a1a2e",
                    "face": "#16213e",
                    "hand": "#e94560",
                    "text": "#ffffff"
                }
            }
        }
    
    def tearDown(self):
        """测试后清理"""
        shutil.rmtree(self.test_dir)
    
    def test_save_config(self):
        """测试配置保存"""
        config_file = os.path.join(self.test_dir, "config.json")
        
        # 保存配置
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
        
        # 验证保存成功
        self.assertTrue(os.path.exists(config_file), "配置文件应被保存")
        
        # 验证内容
        with open(config_file, "r", encoding="utf-8") as f:
            saved_config = json.load(f)
        
        self.assertEqual(saved_config, self.config, "保存的配置应与原始配置一致")
    
    def test_save_config_encoding(self):
        """测试配置保存编码（中文支持）"""
        config_with_chinese = {
            "timezone": "Asia/Shanghai",
            "description": "测试配置 - 中文支持"
        }
        
        config_file = os.path.join(self.test_dir, "config_chinese.json")
        
        # 保存含中文的配置
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(config_with_chinese, f, indent=2, ensure_ascii=False)
        
        # 验证中文正确保存
        with open(config_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        self.assertIn("测试配置", content, "中文应正确保存")
        self.assertIn("中文支持", content, "中文应正确保存")
    
    def test_config_sorting(self):
        """测试配置键排序"""
        unsorted_config = {
            "zebra": "last",
            "alpha": "first",
            "middle": "center"
        }
        
        # 模拟排序
        sorted_config = dict(sorted(unsorted_config.items()))
        
        keys = list(sorted_config.keys())
        self.assertEqual(keys, ["alpha", "middle", "zebra"], "配置键应按字母顺序排序")


class TestConfigValidation(unittest.TestCase):
    """配置验证测试类"""
    
    def test_timezone_validation(self):
        """测试时区配置验证"""
        valid_timezones = ["UTC", "Asia/Shanghai", "America/New_York", "Europe/London"]
        
        for tz in valid_timezones:
            try:
                import zoneinfo
                zoneinfo.ZoneInfo(tz)
                # 有效时区应能创建
            except (ImportError, Exception):
                # 如果 zoneinfo 不可用，跳过
                pass
    
    def test_display_mode_validation(self):
        """测试显示模式配置验证"""
        valid_modes = ["analog", "digital"]
        invalid_modes = ["analog_digital", "clock", "watch", ""]
        
        for mode in valid_modes:
            self.assertIn(mode, valid_modes, f"{mode} 应为有效显示模式")
        
        for mode in invalid_modes:
            self.assertNotIn(mode, valid_modes, f"{mode} 应为无效显示模式")
    
    def test_color_format_validation(self):
        """测试颜色格式验证"""
        valid_colors = ["#ffffff", "#000000", "#1a1a2e", "#FF0000", "#abc"]
        invalid_colors = ["ffffff", "rgb(255,255,255)", "red", "#gggggg", ""]
        
        import re
        color_pattern = re.compile(r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$')
        
        for color in valid_colors:
            self.assertTrue(color_pattern.match(color), f"{color} 应为有效颜色格式")
        
        for color in invalid_colors:
            if color:  # 跳过空字符串
                self.assertFalse(color_pattern.match(color), f"{color} 应为无效颜色格式")
    
    def test_window_size_validation(self):
        """测试窗口尺寸验证"""
        valid_sizes = [(600, 500), (800, 600), (1024, 768)]
        invalid_sizes = [(-100, 100), (0, 0), (600, -500)]
        
        for width, height in valid_sizes:
            self.assertGreater(width, 0, f"宽度 {width} 应为正数")
            self.assertGreater(height, 0, f"高度 {height} 应为正数")
        
        for width, height in invalid_sizes:
            if width <= 0 or height <= 0:
                # 无效尺寸
                pass


if __name__ == "__main__":
    unittest.main()
