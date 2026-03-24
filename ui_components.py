# ClawClock UI 组件模块
"""
将 UI 组件创建拆分为独立的方法
"""
import tkinter as tk
from tkinter import ttk
from typing import Dict, List, Any, Optional, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from clock import ClockApp


class UIMixin:
    """
    UI 组件混入类
    将 setup_ui 大函数拆分为多个小的组件创建方法
    """

    # UI 组件属性类型注解
    tz_combo: ttk.Combobox
    theme_combo: ttk.Combobox
    theme_display_to_name: Dict[str, str]
    theme_name_to_display: Dict[str, str]
    mode_var: tk.StringVar
    fullscreen_btn: tk.Button
    topmost_btn: tk.Button
    canvas: tk.Canvas
    digital_frame: tk.Frame
    seg_canvas: tk.Canvas
    date_label: tk.Label
    stopwatch_frame: tk.Frame
    stopwatch_time_var: tk.StringVar
    stopwatch_label: tk.Label
    sw_start_btn: tk.Button
    sw_stop_btn: tk.Button
    sw_lap_btn: tk.Button
    lap_listbox: tk.Listbox
    timer_frame: tk.Frame
    timer_time_var: tk.StringVar
    timer_label: tk.Label
    timer_status_var: tk.StringVar
    timer_status_label: tk.Label
    timer_preset_buttons: List[tk.Button]
    timer_hour_entry: tk.Entry
    timer_min_entry: tk.Entry
    timer_sec_entry: tk.Entry
    timer_start_btn: tk.Button
    timer_sound_var: tk.BooleanVar
    alarm_listbox: tk.Listbox

    def _setup_timezone_selector(self, parent: tk.Frame) -> None:
        """创建时区选择器 UI"""
        tz_frame: tk.Frame = tk.Frame(parent, bg=self.bg_color)
        tz_frame.pack(pady=(0, 10))

        tk.Label(tz_frame, text="时区:", bg=self.bg_color, fg=self.text_color,
                      font=("Arial", 10)).pack(side=tk.LEFT)

        # 格式化时区选项显示
        tz_values: List[str] = [f"{tz[0]} {tz[2]} ({tz[1]})" for tz in self.timezones]
        self.tz_combo = ttk.Combobox(tz_frame, values=tz_values, width=28, state="readonly")

        # 设置默认时区
        default_tz_display: str = f"UTC+8 上海 (Asia/Shanghai)"
        for tz_val in tz_values:
            if self.timezone in tz_val:
                default_tz_display = tz_val
                break
        self.tz_combo.set(default_tz_display)
        self.tz_combo.pack(side=tk.LEFT, padx=(5, 0))
        self.tz_combo.bind("<<ComboboxSelected>>", self.on_timezone_change)

    def _setup_theme_selector(self, parent: tk.Frame) -> None:
        """创建主题选择器 UI"""
        theme_frame: tk.Frame = tk.Frame(parent, bg=self.bg_color)
        theme_frame.pack(pady=(0, 10))

        tk.Label(theme_frame, text="主题:", bg=self.bg_color, fg=self.text_color,
                      font=("Arial", 10)).pack(side=tk.LEFT)

        # 格式化主题选项显示
        theme_values: List[str] = []
        theme_display_to_name: Dict[str, str] = {}

        for name, data in self.themes.items():
            display_name: str = data.get("display_name", name)
            theme_values.append(display_name)
            theme_display_to_name[display_name] = name

        self.theme_combo = ttk.Combobox(theme_frame, values=theme_values, width=28, state="readonly")
        current_theme_name: str = self.config.get("theme", {}).get("name", "dark")
        current_display: str = self.themes.get(current_theme_name, {}).get(
            "display_name", theme_values[0] if theme_values else "Dark")
        self.theme_combo.set(current_display)
        self.theme_combo.pack(side=tk.LEFT, padx=(5, 0))
        self.theme_combo.bind("<<ComboboxSelected>>", self.on_theme_change)

        # 存储映射
        self.theme_display_to_name = theme_display_to_name
        self.theme_name_to_display: Dict[str, str] = {v: k for k, v in theme_display_to_name.items()}

    def _setup_mode_selector(self, parent: tk.Frame) -> None:
        """创建模式选择器 UI"""
        self.mode_var = tk.StringVar(value=self.display_mode)
        mode_frame: tk.Frame = tk.Frame(parent, bg=self.bg_color)
        mode_frame.pack(pady=(0, 10))

        tk.Radiobutton(mode_frame, text="Analog", variable=self.mode_var, value="analog",
                            bg=self.bg_color, fg=self.text_color, selectcolor=self.accent_color,
                            command=self.update_mode).pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(mode_frame, text="Digital", variable=self.mode_var, value="digital",
                            bg=self.bg_color, fg=self.text_color, selectcolor=self.accent_color,
                            command=self.update_mode).pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(mode_frame, text="⏱️ 秒表", variable=self.mode_var, value="stopwatch",
                            bg=self.bg_color, fg=self.text_color, selectcolor=self.accent_color,
                            command=self.update_mode).pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(mode_frame, text="⏳ 倒计时", variable=self.mode_var, value="timer",
                            bg=self.bg_color, fg=self.text_color, selectcolor=self.accent_color,
                            command=self.update_mode).pack(side=tk.LEFT, padx=5)

    def _setup_action_buttons(self, parent: tk.Frame) -> None:
        """创建功能按钮 UI"""
        btn_frame: tk.Frame = tk.Frame(parent, bg=self.bg_color)
        btn_frame.pack(pady=(0, 10))

        tk.Button(btn_frame, text="⏰ 闹钟", command=self.show_alarm_dialog,
                       bg=self.accent_color, fg=self.text_color).pack(side=tk.LEFT, padx=5)

        self.fullscreen_btn = tk.Button(btn_frame, text="🔲 全屏", command=self.toggle_fullscreen,
                                                   bg=self.accent_color, fg=self.text_color)
        self.fullscreen_btn.pack(side=tk.LEFT, padx=5)

        self.topmost_btn = tk.Button(btn_frame, text="📌 置顶", command=self.toggle_topmost,
                                                bg=self.accent_color, fg=self.text_color)
        self.topmost_btn.pack(side=tk.LEFT, padx=5)

        # NTP 状态标签 (如果 NTP 可用)
        if getattr(self, 'ntp_available', False):
            self.ntp_status_label = tk.Label(
                btn_frame, text="NTP: 未同步",
                font=("Arial", 10),
                bg=self.bg_color,
                fg=self.text_color
            )
            self.ntp_status_label.pack(side=tk.RIGHT, padx=10)

        self._update_button_states()

    def _setup_canvas(self, parent: tk.Frame) -> None:
        """创建模拟时钟画布"""
        self.canvas = tk.Canvas(parent, width=300, height=300, bg=self.bg_color, highlightthickness=0)
        self.canvas.pack(pady=10)

    def _setup_digital_display(self, parent: tk.Frame) -> None:
        """创建数字时钟显示 UI"""
        self.digital_frame = tk.Frame(parent, bg=self.bg_color)

        canvas_width: int = 560
        canvas_height: int = 130
        self.seg_canvas = tk.Canvas(self.digital_frame, width=canvas_width, height=canvas_height,
                                               bg=self.bg_color, highlightthickness=0)
        self.seg_canvas.pack(expand=True)

        self.date_label = tk.Label(self.digital_frame, text="", font=("Arial", 14),
                                              bg=self.bg_color, fg=self.text_color)
        self.date_label.pack(pady=10)

    def _setup_stopwatch_ui(self, parent: tk.Frame) -> None:
        """创建秒表 UI"""
        self.stopwatch_frame = tk.Frame(parent, bg=self.bg_color)

        # 秒表时间显示
        self.stopwatch_time_var = tk.StringVar(value="00:00:00.00")
        self.stopwatch_label = tk.Label(self.stopwatch_frame, textvariable=self.stopwatch_time_var,
                                                   font=("Courier New", 72, "bold"), bg=self.bg_color,
                                                   fg=self.seg_color_on, relief=tk.FLAT)
        self.stopwatch_label.pack(pady=20)

        # 呼吸灯控制
        self.breath_phase: float = 0.0
        self.breath_job: Optional[str] = None

        # 秒表按钮
        sw_btn_frame: tk.Frame = tk.Frame(self.stopwatch_frame, bg=self.bg_color)
        sw_btn_frame.pack(pady=10)

        self.sw_start_btn = tk.Button(sw_btn_frame, text="▶️ 开始", command=self.toggle_stopwatch,
                                                 bg=self.accent_color, fg=self.text_color, font=("Arial", 12), width=10)
        self.sw_start_btn.pack(side=tk.LEFT, padx=10)

        self.sw_stop_btn = tk.Button(sw_btn_frame, text="⏸️ 停止", command=self.toggle_stopwatch,
                                                bg=self.accent_color, fg=self.text_color, font=("Arial", 12), width=10)
        self.sw_stop_btn.pack(side=tk.LEFT, padx=10)
        self.sw_stop_btn.config(state=tk.DISABLED)

        self.sw_lap_btn = tk.Button(sw_btn_frame, text="🏁 计次", command=self.record_lap,
                                               bg=self.accent_color, fg=self.text_color, font=("Arial", 12), width=10)
        self.sw_lap_btn.pack(side=tk.LEFT, padx=10)
        self.sw_lap_btn.config(state=tk.DISABLED)

        tk.Button(sw_btn_frame, text="🔄 重置", command=self.reset_stopwatch,
                       bg=self.accent_color, fg=self.text_color, font=("Arial", 12), width=10).pack(side=tk.LEFT, padx=10)

        # 计次记录列表
        self.lap_listbox = tk.Listbox(self.stopwatch_frame, font=("Courier New", 12),
                                                 bg=self.face_color, fg=self.text_color, height=8, width=30,
                                                 selectbackground=self.accent_color, selectforeground=self.text_color)
        self.lap_listbox.pack(pady=10)

    def _setup_timer_ui(self, parent: tk.Frame) -> None:
        """创建倒计时 UI"""
        self.timer_frame = tk.Frame(parent, bg=self.bg_color)

        # 倒计时时间显示
        self.timer_time_var = tk.StringVar(value="00:00:00")
        self.timer_label = tk.Label(self.timer_frame, textvariable=self.timer_time_var,
                                               font=("Courier New", 72, "bold"), bg=self.bg_color, fg=self.text_color)
        self.timer_label.pack(pady=20)

        # 倒计时状态标签
        self.timer_status_var = tk.StringVar(value="准备就绪")
        self.timer_status_label = tk.Label(self.timer_frame, textvariable=self.timer_status_var,
                                                      font=("Arial", 14), bg=self.bg_color, fg=self.text_color)
        self.timer_status_label.pack(pady=5)

        # 预设时间按钮
        self._setup_timer_presets()

        # 自定义时间输入
        self._setup_timer_custom_input()

        # 倒计时控制按钮
        self._setup_timer_buttons()

    def _setup_timer_presets(self) -> None:
        """创建倒计时预设按钮"""
        timer_preset_frame: tk.Frame = tk.Frame(self.timer_frame, bg=self.bg_color)
        timer_preset_frame.pack(pady=10)

        preset_configs: List[Tuple[str, int, str]] = [
            ("🍅 番茄钟", 1500, "番茄钟"),
            ("☕ 短休息", 300, "短休息"),
            ("🛌 长休息", 900, "长休息"),
            ("⏱️ 5 分钟", 300, "5 分钟"),
            ("⏱️ 10 分钟", 600, "10 分钟"),
            ("⏱️ 30 分钟", 1800, "30 分钟"),
        ]

        self.timer_preset_buttons: List[tk.Button] = []
        for text, seconds, name in preset_configs:
            btn: tk.Button = tk.Button(timer_preset_frame, text=text,
                                       command=lambda s=seconds, n=name: self.set_timer_preset(s, n),
                                       bg=self.accent_color, fg=self.text_color, font=("Arial", 11), width=11)
            btn.pack(side=tk.LEFT, padx=5)
            self.timer_preset_buttons.append(btn)

    def _setup_timer_custom_input(self) -> None:
        """创建倒计时自定义输入 UI"""
        custom_frame: tk.Frame = tk.Frame(self.timer_frame, bg=self.bg_color)
        custom_frame.pack(pady=10)

        tk.Label(custom_frame, text="自定义:", bg=self.bg_color, fg=self.text_color).pack(side=tk.LEFT)

        self.timer_hour_entry = tk.Entry(custom_frame, width=4, justify='center')
        self.timer_hour_entry.insert(0, "00")
        self.timer_hour_entry.pack(side=tk.LEFT, padx=2)
        tk.Label(custom_frame, text=":", bg=self.bg_color, fg=self.text_color).pack(side=tk.LEFT)

        self.timer_min_entry = tk.Entry(custom_frame, width=4, justify='center')
        self.timer_min_entry.insert(0, "00")
        self.timer_min_entry.pack(side=tk.LEFT, padx=2)
        tk.Label(custom_frame, text=":", bg=self.bg_color, fg=self.text_color).pack(side=tk.LEFT)

        self.timer_sec_entry = tk.Entry(custom_frame, width=4, justify='center')
        self.timer_sec_entry.insert(0, "00")
        self.timer_sec_entry.pack(side=tk.LEFT, padx=2)

        tk.Button(custom_frame, text="设置", command=self.set_timer_custom, bg=self.accent_color,
                       fg=self.text_color).pack(side=tk.LEFT, padx=5)

    def _setup_timer_buttons(self) -> None:
        """创建倒计时控制按钮"""
        timer_btn_frame: tk.Frame = tk.Frame(self.timer_frame, bg=self.bg_color)
        timer_btn_frame.pack(pady=15)

        self.timer_start_btn = tk.Button(timer_btn_frame, text="▶️ 开始", command=self.toggle_timer,
                                                    bg=self.accent_color, fg=self.text_color, font=("Arial", 12), width=10)
        self.timer_start_btn.pack(side=tk.LEFT, padx=10)

        tk.Button(timer_btn_frame, text="🔄 重置", command=self.reset_timer,
                       bg=self.accent_color, fg=self.text_color, font=("Arial", 12), width=10).pack(side=tk.LEFT, padx=10)

        # 声音开关
        self.timer_sound_var = tk.BooleanVar(value=True)
        tk.Checkbutton(timer_btn_frame, text="🔊 声音", variable=self.timer_sound_var,
                            bg=self.bg_color, fg=self.text_color, selectcolor=self.accent_color,
                            command=self.toggle_timer_sound).pack(side=tk.LEFT, padx=10)

    def setup_ui(self) -> None:
        """设置用户界面"""
        # Main frame
        main_frame: tk.Frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 时区选择器
        self._setup_timezone_selector(main_frame)

        # 主题选择器
        self._setup_theme_selector(main_frame)

        # 模式选择器
        self._setup_mode_selector(main_frame)

        # 功能按钮
        self._setup_action_buttons(main_frame)

        # 模拟时钟画布
        self._setup_canvas(main_frame)

        # 数字时钟显示
        self._setup_digital_display(main_frame)

        # 秒表 UI
        self._setup_stopwatch_ui(main_frame)

        # 倒计时 UI
        self._setup_timer_ui(main_frame)

        # 7 段数码管段定义
        self.seg_width: int = 60
        self.seg_height: int = 100
        self.seg_thickness: int = 14
        self.digit_spacing: int = 10
        self.colon_space: int = 25

        # 绘制时钟表盘
        self.draw_clock_face()

        # 绑定键盘快捷键
        self._bind_keyboard_shortcuts()

    def _bind_keyboard_shortcuts(self) -> None:
        """绑定键盘快捷键"""
        self.root.bind('<space>', self.on_space_key)
        self.root.bind('<r>', lambda e: self.on_reset_key())
        self.root.bind('<R>', lambda e: self.on_reset_key())
        self.root.bind('<f>', lambda e: self.toggle_fullscreen())
        self.root.bind('<F>', lambda e: self.toggle_fullscreen())
        self.root.bind('<t>', lambda e: self.toggle_topmost())
        self.root.bind('<T>', lambda e: self.toggle_topmost())
