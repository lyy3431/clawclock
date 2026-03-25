#!/usr/bin/env python3
"""
ClawClock - 核心时钟逻辑模块
============================

提供时钟应用的核心功能：
- 版本管理
- 数据类定义
- 配置管理
- 主题管理
- 时区管理
"""

import os
import json
import time
import datetime
import threading
from typing import Dict, List, Optional, Tuple, Any, TYPE_CHECKING
from dataclasses import dataclass, field

# NTP 同步模块 (可选导入)
try:
    from utils.ntp_client import NTPSyncManager, NTPResult
    NTP_AVAILABLE = True
except ImportError:
    NTP_AVAILABLE = False
    NTPSyncManager = None  # type: ignore
    NTPResult = None  # type: ignore

if TYPE_CHECKING:
    from clock import ClockApp

# ==================== 版本常量 ====================
__version__ = "1.8.0"
__version_info__: Tuple[int, int, int] = (1, 8, 0)


def get_version() -> str:
    """
    获取版本号（优先从 git 获取，fallback 到硬编码版本）

    Returns:
        str: 版本号字符串
    """
    try:
        import subprocess
        result = subprocess.run(
            ['git', 'describe', '--tags', '--always', '--dirty'],
            capture_output=True,
            text=True,
            timeout=2,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        if result.returncode == 0 and result.stdout.strip():
            git_version = result.stdout.strip()
            if git_version.startswith('v'):
                return git_version[1:]
            return git_version
    except Exception:
        pass
    return __version__


@dataclass
class Alarm:
    """闹钟数据类

    Attributes:
        time: 闹钟时间 (HH:MM 格式)
        enabled: 是否启用
        label: 闹钟标签
        sound: 铃声类型
        repeat_days: 重复日期列表 (0=Monday, 6=Sunday)
        snooze_minutes: 小睡时长 (分钟)
    """
    time: str
    enabled: bool = True
    label: str = ""
    sound: str = "default"
    repeat_days: List[int] = field(default_factory=list)
    snooze_minutes: int = 5

    def is_due(self, current_time: datetime.datetime) -> bool:
        """检查当前时间是否触发闹钟"""
        if not self.enabled:
            return False

        current_hour = current_time.hour
        current_minute = current_time.minute
        current_second = current_time.second
        current_weekday = current_time.weekday()

        alarm_hour, alarm_minute = map(int, self.time.split(":"))

        if current_hour == alarm_hour and current_minute == alarm_minute and current_second == 0:
            if not self.repeat_days or current_weekday in self.repeat_days:
                return True
        return False


@dataclass
class LapRecord:
    """计次记录数据类"""
    lap_number: int
    time_ms: int
    split_ms: int
    timestamp: datetime.datetime = field(default_factory=datetime.datetime.now)


@dataclass
class StopwatchState:
    """秒表状态数据类"""
    is_running: bool = False
    start_time: float = 0.0
    elapsed_ms: int = 0
    laps: List[LapRecord] = field(default_factory=list)


@dataclass
class TimerState:
    """倒计时状态数据类"""
    is_running: bool = False
    total_seconds: int = 0
    remaining_seconds: float = 0.0
    start_time: float = 0.0
    sound_enabled: bool = True
    preset_name: str = ""


class ConfigMixin:
    """配置管理混入类"""

    def load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
        default_config: Dict[str, Any] = {
            "timezone": "Asia/Shanghai",
            "display_mode": "digital",
            "window": {
                "width": 600,
                "height": 500,
                "resizable": True,
                "always_on_top": False,
                "fullscreen": False
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
            },
            "alarms": [],
            "stopwatch": {"laps": []}
        }

        try:
            if os.path.exists(config_file):
                with open(config_file, "r", encoding="utf-8") as f:
                    config = json.load(f)
                return self._merge_config(default_config, config)
            else:
                self._save_config_raw(default_config, config_file)
                return default_config
        except Exception as e:
            print(f"⚠️  加载配置文件失败：{e}")
            return default_config

    def _merge_config(self, default: Dict[str, Any], custom: Dict[str, Any]) -> Dict[str, Any]:
        """递归合并配置字典"""
        result = default.copy()
        for key, value in custom.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_config(result[key], value)
            else:
                result[key] = value
        return result

    def _save_config_raw(self, config: Dict[str, Any], config_file: str) -> None:
        """保存配置到文件（原始方法）"""
        sorted_config = self._sort_config(config)
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(sorted_config, f, indent=2, ensure_ascii=False)

    def _sort_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """递归排序配置字典"""
        sorted_config: Dict[str, Any] = {}
        for key in sorted(config.keys()):
            value = config[key]
            if isinstance(value, dict):
                sorted_config[key] = self._sort_config(value)
            else:
                sorted_config[key] = value
        return sorted_config

    def save_config(self, config: Optional[Dict[str, Any]] = None) -> bool:
        """保存配置文件"""
        config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
        config_to_save = config if config is not None else getattr(self, 'config', {})

        try:
            self._save_config_raw(config_to_save, config_file)
            return True
        except Exception as e:
            print(f"⚠️  保存配置文件失败：{e}")
            return False


class NTPMixin:
    """NTP 时间同步混入类"""

    def init_ntp(self) -> None:
        """初始化 NTP 同步管理器"""
        if not NTP_AVAILABLE:
            self.ntp_manager = None
            self.ntp_available = False
            return

        self.ntp_available = True
        self.ntp_manager = NTPSyncManager(
            history_file=os.path.join(
                os.path.dirname(os.path.abspath(__file__)),
                "ntp_history.json"
            )
        )
        self.ntp_manager.load_history()
        
        # 从配置加载 NTP 设置
        ntp_config = self.config.get("ntp", {})
        if ntp_config.get("auto_sync", False):
            self.ntp_manager.enable_auto_sync(
                ntp_config.get("sync_interval_hours", 24)
            )
        
        # 启动时自动同步一次 (如果启用)
        if ntp_config.get("enabled", False):
            self.sync_time_ntp(background=True)
        else:
            # 即使 NTP 未启用，也尝试获取一次状态用于显示
            # 这样用户可以看到 NTP 是否可用
            if hasattr(self, 'root') and self.root:
                self.root.after(500, self._init_ntp_status_check)
    
    def _init_ntp_status_check(self) -> None:
        """初始化 NTP 状态检查（仅用于显示，不自动同步）"""
        if hasattr(self, 'update_ntp_status_display'):
            self.update_ntp_status_display()

    def sync_time_ntp(self, server: Optional[str] = None, 
                      background: bool = False) -> Optional[NTPResult]:
        """执行 NTP 时间同步

        Args:
            server: NTP 服务器地址，默认自动选择
            background: 是否在后台线程执行

        Returns:
            Optional[NTPResult]: 同步结果，后台执行时返回 None
        """
        if not self.ntp_available or not self.ntp_manager:
            return None

        def do_sync() -> NTPResult:
            result = self.ntp_manager.sync_now(server)
            # 无论成功还是失败，都更新状态显示
            if hasattr(self, 'update_ntp_status_display'):
                self.root.after(0, self.update_ntp_status_display, result)
            return result

        if background:
            thread = threading.Thread(target=do_sync, daemon=True)
            thread.start()
            return None
        else:
            return do_sync()

    def get_ntp_status(self) -> Dict[str, Any]:
        """获取 NTP 同步状态

        Returns:
            Dict[str, Any]: 状态信息
        """
        if not self.ntp_available or not self.ntp_manager:
            return {
                "available": False,
                "enabled": False,
                "status": "不可用"
            }

        status = self.ntp_manager.get_sync_status()
        ntp_config = self.config.get("ntp", {})
        
        return {
            "available": True,
            "enabled": ntp_config.get("enabled", False),
            "auto_sync": status.get("auto_sync_enabled", False),
            "sync_interval": status.get("auto_sync_interval", 24),
            "last_sync_time": status.get("last_sync_time"),
            "last_sync_offset": status.get("last_sync_offset"),
            "last_sync_server": status.get("last_sync_server"),
            "total_sync_count": status.get("total_sync_count", 0),
            "status": self._get_ntp_status_text(status)
        }

    def _get_ntp_status_text(self, status: Dict[str, Any]) -> str:
        """获取 NTP 状态文本"""
        if not status.get("last_sync_time"):
            return "未同步"
        
        offset = status.get("last_sync_offset", 0)
        if offset is None:
            return "未同步"
        
        if abs(offset) < 0.001:
            return "✓ 精确同步"
        elif abs(offset) < 0.1:
            return f"✓ 偏差 {offset:+.3f}秒"
        elif abs(offset) < 1.0:
            return f"⚠ 偏差 {offset:+.3f}秒"
        else:
            return f"✗ 偏差 {offset:+.3f}秒"

    def set_ntp_enabled(self, enabled: bool) -> None:
        """设置 NTP 同步启用状态"""
        if not self.ntp_available:
            return
        
        if "ntp" not in self.config:
            self.config["ntp"] = {}
        
        self.config["ntp"]["enabled"] = enabled
        self.save_config()
        
        if enabled and self.ntp_manager:
            self.sync_time_ntp(background=True)

    def set_ntp_auto_sync(self, enabled: bool, interval_hours: int = 24) -> None:
        """设置自动同步"""
        if not self.ntp_available or not self.ntp_manager:
            return
        
        if "ntp" not in self.config:
            self.config["ntp"] = {}
        
        self.config["ntp"]["auto_sync"] = enabled
        self.config["ntp"]["sync_interval_hours"] = interval_hours
        self.save_config()
        
        if enabled:
            self.ntp_manager.enable_auto_sync(interval_hours)
        else:
            self.ntp_manager.disable_auto_sync()


class ThemeMixin:
    """主题管理混入类"""

    def load_themes(self) -> Dict[str, Dict[str, Any]]:
        """加载所有主题"""
        themes_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "themes")
        themes = {}

        if os.path.exists(themes_dir):
            for filename in os.listdir(themes_dir):
                if filename.endswith('.json'):
                    theme_name = filename[:-5]
                    try:
                        with open(os.path.join(themes_dir, filename), 'r', encoding='utf-8') as f:
                            themes[theme_name] = json.load(f)
                    except Exception as e:
                        print(f"⚠️  加载主题 {theme_name} 失败：{e}")

        return themes

    def apply_theme(self, theme_name: str) -> None:
        """应用主题到当前实例"""
        theme = self.themes.get(theme_name, {})
        colors = theme.get("colors", {})

        self.bg_color = colors.get("background", "#1a1a2e")
        self.face_color = colors.get("face", "#16213e")
        self.hand_color = colors.get("hand", "#e94560")
        self.text_color = colors.get("text", "#ffffff")
        self.accent_color = colors.get("accent", "#0f3460")
        self.seg_color_on = colors.get("segment_on", "#ff3333")
        self.seg_color_off = colors.get("segment_off", "#331111")
        
        # 保存当前主题到配置
        if hasattr(self, 'config'):
            self.config["theme"] = {"name": theme_name}
            self.save_config()
        
        # 刷新 UI 主题
        if hasattr(self, 'root') and self.root:
            self.root.after(0, self._refresh_theme_ui)
    
    def _refresh_theme_ui(self) -> None:
        """刷新 UI 组件以应用新主题 - 完整版本"""
        if not hasattr(self, 'root'):
            return

        # 1. 更新主窗口背景色（最关键！）
        try:
            self.root.configure(bg=self.bg_color)
            # 确保窗口背景色生效
            self.root["bg"] = self.bg_color
        except Exception:
            pass

        # 2. 更新 main_frame 背景色（关键！）
        if hasattr(self, 'main_frame'):
            try:
                self.main_frame.configure(bg=self.bg_color)
                self.main_frame["bg"] = self.bg_color
            except Exception:
                pass

        # 3. 更新 digital_frame 背景色（数字显示区）
        if hasattr(self, 'digital_frame'):
            try:
                self.digital_frame.configure(bg=self.bg_color)
                self.digital_frame["bg"] = self.bg_color
            except Exception:
                pass

        # 4. 更新 stopwatch_frame 背景色（秒表显示区）
        if hasattr(self, 'stopwatch_frame'):
            try:
                self.stopwatch_frame.configure(bg=self.bg_color)
                self.stopwatch_frame["bg"] = self.bg_color
            except Exception:
                pass

        # 5. 更新 timer_frame 背景色（倒计时显示区）
        if hasattr(self, 'timer_frame'):
            try:
                self.timer_frame.configure(bg=self.bg_color)
                self.timer_frame["bg"] = self.bg_color
            except Exception:
                pass

        # 6. 更新 ttk 样式（关键！）
        self._update_ttk_styles()

        # 6b. 显式刷新 ttk 组件（关键修复！）
        self._refresh_ttk_widgets()

        # 7. 强制刷新主窗口
        self.root.update_idletasks()

        # 8. 更新所有 Frame 的背景色
        for widget in self.root.winfo_children():
            self._update_widget_theme(widget)

        # 9. 重绘时钟表盘
        if hasattr(self, 'canvas'):
            self.canvas.config(bg=self.bg_color)
            self.draw_clock_face()

        # 10. 重绘数字显示
        if hasattr(self, 'seg_canvas'):
            self.seg_canvas.config(bg=self.bg_color)
            time_str = datetime.datetime.now().strftime("%H:%M:%S")
            self.draw_seven_segment_time(time_str)

        # 11. 更新秒表显示颜色
        if hasattr(self, 'stopwatch_label'):
            self.stopwatch_label.config(bg=self.bg_color, fg=self.seg_color_on)

        # 12. 更新倒计时显示颜色
        if hasattr(self, 'timer_label'):
            self.timer_label.config(bg=self.bg_color, fg=self.text_color)

        # 13. 更新日期标签
        if hasattr(self, 'date_label'):
            self.date_label.config(bg=self.bg_color, fg=self.text_color)

        # 14. 更新 NTP 状态标签
        if hasattr(self, 'ntp_status_label'):
            self.ntp_status_label.config(bg=self.bg_color, fg=self.text_color)

        # 15. 更新所有按钮的背景色和前景色
        self._update_all_button_colors()

        # 16. 更新模式选择器 Radiobutton 颜色
        self._update_mode_selector_colors()

        # 17. 更新秒表计次列表背景色
        if hasattr(self, 'lap_listbox'):
            self.lap_listbox.config(bg=self.face_color, fg=self.text_color,
                                   selectbackground=self.accent_color, selectforeground=self.text_color)

        # 18. 更新倒计时输入框背景色（使用 face_color 作为 Entry 的背景）
        if hasattr(self, 'timer_hour_entry'):
            self.timer_hour_entry.config(bg=self.face_color, fg=self.text_color,
                                        insertbackground=self.text_color)
        if hasattr(self, 'timer_min_entry'):
            self.timer_min_entry.config(bg=self.face_color, fg=self.text_color,
                                       insertbackground=self.text_color)
        if hasattr(self, 'timer_sec_entry'):
            self.timer_sec_entry.config(bg=self.face_color, fg=self.text_color,
                                       insertbackground=self.text_color)

        # 20. 更新时区和主题选择器 Combobox - 关键修复：完全刷新 Combobox
        self._refresh_combobox_widgets()

        # 21. 强制刷新整个窗口（两次确保生效）
        self.root.after(50, lambda: self.root.update_idletasks())
        self.root.after(100, lambda: self.root.update_idletasks())
        self.root.after(150, lambda: self.root.update_idletasks())

    def _update_ttk_styles(self) -> None:
        """更新 ttk 组件的样式（Combobox 等）- 完整修复版本"""
        try:
            style = ttk.Style()

            # 关键：首先获取当前使用的 ttk theme，确保我们修改的是正确的主题
            current_theme = style.theme_use()

            # 定义要更新的 ttk 样式
            ttk_styles = [
                'TCombobox', 'TEntry', 'TFrame', 'TLabel', 'TButton',
                'Horizontal.TScale', 'Vertical.TScale', 'TRadiobutton', 'TCheckbutton', 'TListbox'
            ]

            for style_name in ttk_styles:
                try:
                    if style_name == 'TCombobox':
                        # 配置 Combobox 样式 - 完整配置
                        style.configure(style_name,
                                       background=self.bg_color,
                                       foreground=self.text_color,
                                       fieldbackground=self.face_color,
                                       arrowcolor=self.text_color,
                                       bordercolor=self.accent_color,
                                       selectbackground=self.accent_color,
                                       selectforeground=self.text_color,
                                       lightcolor=self.bg_color,
                                       darkcolor=self.accent_color,
                                       focuscolor=self.bg_color,
                                       troughcolor=self.bg_color)
                        # 配置各种状态的样式 - 覆盖所有可能状态
                        style.map(style_name,
                                 fieldbackground=[
                                     ('readonly', self.face_color),
                                     ('focus', self.face_color),
                                     ('active', self.face_color),
                                     ('disabled', self.bg_color),
                                     ('!disabled', self.face_color)
                                 ],
                                 foreground=[
                                     ('readonly', self.text_color),
                                     ('focus', self.text_color),
                                     ('disabled', self.text_color),
                                     ('!disabled', self.text_color)
                                 ],
                                 selectbackground=[('readonly', self.accent_color), ('focus', self.accent_color)],
                                 selectforeground=[('readonly', self.text_color), ('focus', self.text_color)])

                    elif style_name == 'TEntry':
                        style.configure(style_name,
                                       background=self.face_color,
                                       foreground=self.text_color,
                                       fieldbackground=self.face_color,
                                       insertcolor=self.text_color,
                                       lightcolor=self.face_color,
                                       darkcolor=self.accent_color,
                                       focuscolor=self.face_color,
                                       troughcolor=self.face_color)
                        style.map(style_name,
                                 fieldbackground=[
                                     ('focus', self.face_color),
                                     ('readonly', self.face_color),
                                     ('disabled', self.bg_color),
                                     ('active', self.face_color),
                                     ('!disabled', self.face_color),
                                     ('!focus', self.face_color)
                                 ],
                                 foreground=[
                                     ('focus', self.text_color),
                                     ('readonly', self.text_color),
                                     ('disabled', self.text_color),
                                     ('!disabled', self.text_color)
                                 ])

                    elif style_name == 'TFrame':
                        style.configure(style_name, background=self.bg_color)

                    elif style_name == 'TLabel':
                        style.configure(style_name, background=self.bg_color,
                                       foreground=self.text_color)

                    elif style_name == 'TButton':
                        style.configure(style_name,
                                       background=self.accent_color,
                                       foreground=self.text_color,
                                       bordercolor=self.accent_color,
                                       focuscolor=self.accent_color,
                                       lightcolor=self.accent_color,
                                       darkcolor=self.bg_color)
                        style.map(style_name,
                                 background=[
                                     ('active', self.bg_color),
                                     ('pressed', self.accent_color),
                                     ('focus', self.bg_color),
                                     ('disabled', self.bg_color),
                                     ('!disabled', self.accent_color),
                                     ('!active', self.accent_color)
                                 ],
                                 foreground=[
                                     ('active', self.text_color),
                                     ('pressed', self.text_color),
                                     ('focus', self.text_color),
                                     ('disabled', self.text_color),
                                     ('!disabled', self.text_color)
                                 ])

                    elif style_name == 'TRadiobutton':
                        style.configure(style_name,
                                       background=self.bg_color,
                                       foreground=self.text_color,
                                       indicatorcolor=self.accent_color,
                                       focuscolor=self.accent_color)
                        style.map(style_name,
                                 background=[('active', self.bg_color), ('disabled', self.bg_color), ('!disabled', self.bg_color)],
                                 foreground=[('active', self.text_color), ('disabled', self.text_color), ('!disabled', self.text_color)])

                    elif style_name == 'TCheckbutton':
                        style.configure(style_name,
                                       background=self.bg_color,
                                       foreground=self.text_color,
                                       indicatorcolor=self.accent_color,
                                       focuscolor=self.accent_color)
                        style.map(style_name,
                                 background=[('active', self.bg_color), ('disabled', self.bg_color), ('!disabled', self.bg_color)],
                                 foreground=[('active', self.text_color), ('disabled', self.text_color), ('!disabled', self.text_color)])

                    elif style_name == 'TListbox':
                        style.configure(style_name,
                                       background=self.face_color,
                                       foreground=self.text_color,
                                       fieldbackground=self.face_color,
                                       selectbackground=self.accent_color,
                                       selectforeground=self.text_color)

                    elif 'Scale' in style_name:
                        style.configure(style_name,
                                       background=self.bg_color,
                                       troughcolor=self.face_color,
                                       bordercolor=self.accent_color,
                                       sliderrelief='flat')
                        style.map(style_name,
                                 background=[('active', self.bg_color)])
                except Exception as e:
                    pass  # 忽略不支持的样式选项
        except Exception as e:
            pass

        # 额外配置：针对 clam 主题的特殊处理 - 关键修复：Combobox 下拉列表颜色
        try:
            # 配置 Combobox 的布局元素颜色
            style = ttk.Style()
            # 获取 Combobox 的当前布局
            combo_layout = style.layout('TCombobox')
            if combo_layout:
                # 配置 Combobox 内部元素
                style.configure('Combobox.PopdownMenu',
                               background=self.face_color,
                               foreground=self.text_color)
                
            # 关键修复：配置下拉列表的 Listbox 颜色
            style.configure('TCombobox',
                           postoffset=[0, 0, 0, 0])
            
            # 尝试配置下拉列表背景色（多种可能的样式名）
            for popdown_style in ['Combobox.Treeview', 'Treeview', 'Combobox.Listbox']:
                try:
                    style.configure(popdown_style,
                                   background=self.face_color,
                                   foreground=self.text_color,
                                   fieldbackground=self.face_color,
                                   selectbackground=self.accent_color,
                                   selectforeground=self.text_color)
                except Exception:
                    pass
        except Exception:
            pass

    def _refresh_combobox_widgets(self) -> None:
        """专门刷新 Combobox 组件 - 彻底修复下拉列表颜色问题"""
        if not hasattr(self, 'root'):
            return
        
        # 刷新所有 Combobox 的颜色
        for combo_attr in ['tz_combo', 'theme_combo']:
            if hasattr(self, combo_attr):
                combo = getattr(self, combo_attr)
                try:
                    # 保存当前状态
                    current_value = combo.get()
                    values = combo.cget('values')
                    state = combo.cget('state')
                    width = combo.cget('width')
                    
                    # 获取父容器和布局信息
                    parent = combo.master
                    pack_info = combo.pack_info()
                    
                    # 销毁旧组件
                    combo.destroy()
                    
                    # 创建新组件
                    new_combo = ttk.Combobox(parent, values=values, width=width, state=state)
                    new_combo.set(current_value)
                    
                    # 重新打包到相同位置
                    if pack_info:
                        new_combo.pack(**pack_info)
                    else:
                        new_combo.pack(side=tk.LEFT, padx=(5, 0))
                    
                    # 重新绑定事件
                    if combo_attr == 'tz_combo' and hasattr(self, 'on_timezone_change'):
                        new_combo.bind("<<ComboboxSelected>>", self.on_timezone_change)
                    elif combo_attr == 'theme_combo' and hasattr(self, 'on_theme_change'):
                        new_combo.bind("<<ComboboxSelected>>", self.on_theme_change)
                    
                    # 更新引用
                    setattr(self, combo_attr, new_combo)
                except Exception as e:
                    print(f"刷新 {combo_attr} 失败：{e}")

    def _refresh_ttk_widgets(self) -> None:
        """显式刷新所有 ttk 组件的颜色 - 关键修复方法"""
        if not hasattr(self, 'root'):
            return

        # 显式刷新 Combobox - 通过重新应用样式和刷新值
        if hasattr(self, 'tz_combo'):
            try:
                # 强制重新应用样式
                self.tz_combo.configure(style='TCombobox')
                # 通过重新设置值来强制刷新显示
                current_value = self.tz_combo.get()
                values = self.tz_combo.cget('values')
                self.tz_combo.configure(values=values)
                self.tz_combo.set(current_value)
            except Exception:
                pass

        if hasattr(self, 'theme_combo'):
            try:
                # 强制重新应用样式
                self.theme_combo.configure(style='TCombobox')
                # 通过重新设置值来强制刷新显示
                current_value = self.theme_combo.get()
                values = self.theme_combo.cget('values')
                self.theme_combo.configure(values=values)
                self.theme_combo.set(current_value)
            except Exception:
                pass

        # 显式刷新 Entry 组件
        if hasattr(self, 'timer_hour_entry'):
            try:
                value = self.timer_hour_entry.get()
                self.timer_hour_entry.delete(0, tk.END)
                self.timer_hour_entry.insert(0, value)
            except Exception:
                pass

        if hasattr(self, 'timer_min_entry'):
            try:
                value = self.timer_min_entry.get()
                self.timer_min_entry.delete(0, tk.END)
                self.timer_min_entry.insert(0, value)
            except Exception:
                pass

        if hasattr(self, 'timer_sec_entry'):
            try:
                value = self.timer_sec_entry.get()
                self.timer_sec_entry.delete(0, tk.END)
                self.timer_sec_entry.insert(0, value)
            except Exception:
                pass

    def _update_mode_selector_colors(self) -> None:
        """更新模式选择器 Radiobutton 的颜色"""
        # 查找并更新所有 Radiobutton
        if hasattr(self, 'root'):
            for widget in self.root.winfo_children():
                self._update_radiobutton_recursive(widget)

    def _update_radiobutton_recursive(self, widget) -> None:
        """递归更新 Radiobutton 颜色"""
        try:
            if isinstance(widget, tk.Radiobutton):
                widget.config(bg=self.bg_color, fg=self.text_color,
                             selectcolor=self.accent_color,
                             activebackground=self.bg_color,
                             activeforeground=self.text_color)
            
            if hasattr(widget, 'winfo_children'):
                for child in widget.winfo_children():
                    self._update_radiobutton_recursive(child)
        except Exception:
            pass

    def _update_widget_theme(self, widget) -> None:
        """递归更新组件主题 - 完整版本支持所有控件类型"""
        try:
            widget_type = type(widget).__name__
            widget_class = widget.winfo_class()

            # 更新 Frame (包括 ttk.Frame)
            if isinstance(widget, tk.Frame):
                widget.config(bg=self.bg_color)
                # 递归更新 Frame 内的子组件
                for child in widget.winfo_children():
                    self._update_widget_theme(child)
                return

            # 更新 Label (包括 ttk.Label)
            if isinstance(widget, tk.Label):
                widget.config(bg=self.bg_color, fg=self.text_color)

            # 更新 Button (包括 ttk.Button)
            elif isinstance(widget, tk.Button):
                widget.config(bg=self.accent_color, fg=self.text_color,
                             activebackground=self.bg_color, activeforeground=self.text_color)

            # 更新 Checkbutton (包括 ttk.Checkbutton)
            elif isinstance(widget, tk.Checkbutton):
                widget.config(bg=self.bg_color, fg=self.text_color,
                             selectcolor=self.accent_color, activebackground=self.bg_color,
                             activeforeground=self.text_color)

            # 更新 Radiobutton (包括 ttk.Radiobutton)
            elif isinstance(widget, tk.Radiobutton):
                widget.config(bg=self.bg_color, fg=self.text_color,
                             selectcolor=self.accent_color, activebackground=self.bg_color,
                             activeforeground=self.text_color)

            # 更新 Listbox
            elif isinstance(widget, tk.Listbox):
                widget.config(bg=self.face_color, fg=self.text_color,
                             selectbackground=self.accent_color, selectforeground=self.text_color)

            # 更新 Canvas
            elif isinstance(widget, tk.Canvas):
                widget.config(bg=self.bg_color, highlightthickness=0)

            # 更新 Entry (包括 ttk.Entry) - 关键修复：显式设置背景色
            elif isinstance(widget, tk.Entry):
                widget.config(bg=self.face_color, fg=self.text_color,
                             insertbackground=self.text_color)

            # 更新 Combobox (ttk.Combobox) - 关键修复：显式配置样式
            elif widget_class == 'TCombobox':
                try:
                    # 强制重新应用样式
                    widget.configure(style='TCombobox')
                    # 显式设置颜色（确保生效）
                    widget.configure(values=widget.cget('values'))  # 刷新显示
                except Exception:
                    pass

            # 更新 ttk.Entry - 关键修复：显式设置背景色
            elif widget_class == 'TEntry':
                try:
                    widget.configure(style='TEntry')
                except Exception:
                    pass

            # 更新 Scale (滑块)
            elif isinstance(widget, ttk.Scale):
                try:
                    orient = str(widget.cget('orient'))
                    style_name = 'Horizontal.TScale' if orient == 'horizontal' else 'Vertical.TScale'
                    widget.configure(style=style_name)
                except Exception:
                    pass

            # 更新 ttk.Label
            elif widget_class == 'TLabel':
                try:
                    widget.configure(style='TLabel')
                except Exception:
                    pass

            # 更新 ttk.Button - 关键修复：显式配置样式
            elif widget_class == 'TButton':
                try:
                    widget.configure(style='TButton')
                except Exception:
                    pass

            # 更新 ttk.Radiobutton - 关键修复：显式配置样式
            elif widget_class == 'TRadiobutton':
                try:
                    widget.configure(style='TRadiobutton')
                except Exception:
                    pass

            # 更新 ttk.Checkbutton
            elif widget_class == 'TCheckbutton':
                try:
                    widget.configure(style='TCheckbutton')
                except Exception:
                    pass

            # 更新 ttk.Frame
            elif widget_class == 'TFrame':
                try:
                    widget.configure(style='TFrame')
                except Exception:
                    pass

            # 其他 ttk 组件使用样式更新
            elif hasattr(widget, 'configure') and widget_class.startswith('T'):
                try:
                    widget.configure(style=widget_class)
                except Exception:
                    pass
        except Exception:
            pass

    def _update_all_button_colors(self) -> None:
        """更新所有按钮的颜色"""
        if not hasattr(self, 'root'):
            return

        for widget in self.root.winfo_children():
            self._update_button_recursive(widget)

    def _update_button_recursive(self, widget) -> None:
        """递归更新按钮颜色"""
        try:
            if isinstance(widget, tk.Button):
                widget.config(bg=self.accent_color, fg=self.text_color,
                             activebackground=self.bg_color, activeforeground=self.text_color)

            for child in widget.winfo_children():
                self._update_button_recursive(child)
        except Exception:
            pass


class AlarmManagerMixin:
    """闹钟管理混入类"""

    def _load_alarms(self) -> None:
        """从配置加载闹钟"""
        alarms_data = self.config.get("alarms", [])
        self.alarms = []
        for alarm_data in alarms_data:
            alarm = Alarm(
                time=alarm_data.get("time", "00:00"),
                enabled=alarm_data.get("enabled", True),
                label=alarm_data.get("label", ""),
                sound=alarm_data.get("sound", "default"),
                repeat_days=alarm_data.get("repeat_days", []),
                snooze_minutes=alarm_data.get("snooze_minutes", 5)
            )
            self.alarms.append(alarm)

    def _save_alarms(self) -> None:
        """保存闹钟到配置"""
        self.config["alarms"] = [
            {
                "time": alarm.time,
                "enabled": alarm.enabled,
                "label": alarm.label,
                "sound": alarm.sound,
                "repeat_days": alarm.repeat_days,
                "snooze_minutes": alarm.snooze_minutes
            }
            for alarm in self.alarms
        ]
        self.save_config()

    def _check_alarms(self) -> None:
        """定期检查闹钟（每秒）"""
        def check_loop() -> None:
            while True:
                time.sleep(1)
                if not getattr(self, 'alarm_triggered', False):
                    now = datetime.datetime.now()
                    for alarm in self.alarms:
                        if alarm.is_due(now):
                            self.alarm_triggered = True
                            if hasattr(self, 'root'):
                                self.root.after(0, self._trigger_alarm, alarm)
                            break

        thread = threading.Thread(target=check_loop, daemon=True)
        thread.start()

    def _trigger_alarm(self, alarm: Alarm) -> None:
        """触发闹钟"""
        raise NotImplementedError("子类必须实现 _trigger_alarm 方法")

    def add_alarm(self, time_str: str, label: str = "",
                  repeat_days: Optional[List[int]] = None,
                  snooze_minutes: int = 5) -> bool:
        """添加闹钟"""
        try:
            datetime.datetime.strptime(time_str, "%H:%M")
            alarm = Alarm(
                time=time_str,
                enabled=True,
                label=label,
                repeat_days=repeat_days or [],
                snooze_minutes=snooze_minutes
            )
            self.alarms.append(alarm)
            self._save_alarms()
            return True
        except ValueError:
            return False

    def remove_alarm(self, index: int) -> bool:
        """删除闹钟"""
        if 0 <= index < len(self.alarms):
            self.alarms.pop(index)
            self._save_alarms()
            return True
        return False

    def toggle_alarm(self, index: int) -> bool:
        """切换闹钟启用状态"""
        if 0 <= index < len(self.alarms):
            self.alarms[index].enabled = not self.alarms[index].enabled
            self._save_alarms()
            return True
        return False


class TimezoneManagerMixin:
    """时区管理混入类"""

    def _init_timezones(self) -> None:
        """初始化时区列表"""
        self.timezones: List[Tuple[str, str, str]] = [
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


class ClockCore(ConfigMixin, ThemeMixin, AlarmManagerMixin, TimezoneManagerMixin):
    """
    时钟核心逻辑类

    整合所有核心功能混入类，提供基础时钟功能
    """
    pass
