#!/usr/bin/env python3
"""
ClawClock - 事件处理模块
========================

负责事件处理和状态管理：
- 秒表功能
- 倒计时功能
- 键盘事件
- 窗口管理
"""

import time
import math
import tkinter as tk
from tkinter import messagebox
from typing import Optional, Any, List, Tuple, TYPE_CHECKING, Dict

if TYPE_CHECKING:
    from clock import ClockApp

from clock_core import StopwatchState, LapRecord, TimerState


class StopwatchMixin:
    """秒表功能混入类"""

    # 秒表相关属性
    stopwatch_job: Optional[str]
    breath_job: Optional[str]
    breath_phase: float

    def _update_stopwatch_display(self) -> None:
        """更新秒表显示"""
        if hasattr(self, 'stopwatch_time_var'):
            # 只在秒表运行时计算时间，否则显示 0
            if self.stopwatch.is_running:
                current_time: float = time.time()
                delta_ms: int = int((current_time - self.stopwatch.start_time) * 1000)
                total_ms: int = self.stopwatch.elapsed_ms + delta_ms
                self.stopwatch_time_var.set(self._format_time_ms(total_ms))
            else:
                # 秒表未运行时显示已累积的时间（或 0）
                # 确保 elapsed_ms 是有效的非负值
                elapsed = max(0, self.stopwatch.elapsed_ms) if hasattr(self.stopwatch, 'elapsed_ms') else 0
                self.stopwatch_time_var.set(self._format_time_ms(elapsed))
            
            # 启动呼吸灯
            if not getattr(self, 'breath_job', None):
                self._start_breath_effect()

        # 继续更新
        if self.stopwatch.is_running and hasattr(self, 'root'):
            self.stopwatch_job = self.root.after(50, self._update_stopwatch_display)

    def _format_time_ms(self, ms: int) -> str:
        """格式化毫秒时间为显示字符串"""
        total_seconds = ms // 1000
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        milliseconds = (ms % 1000) // 10
        return f"{minutes:02d}:{seconds:02d}.{milliseconds:02d}"

    def toggle_stopwatch(self) -> None:
        """启动/停止秒表"""
        if self.stopwatch.is_running:
            # 暂停秒表
            self.stopwatch.is_running = False
            if self.stopwatch_job:
                self.root.after_cancel(self.stopwatch_job)
                self.stopwatch_job = None
            self.sw_start_btn.config(text="▶️ 继续")
            self.sw_stop_btn.config(state=tk.DISABLED)
            self.sw_lap_btn.config(state=tk.DISABLED)
            self._stop_breath_effect()
        else:
            # 启动/继续秒表
            self.stopwatch.is_running = True
            self.stopwatch.start_time = time.time()
            self.sw_start_btn.config(text="⏸️ 暂停")
            self.sw_stop_btn.config(state=tk.NORMAL)
            self.sw_lap_btn.config(state=tk.NORMAL)
            self._update_stopwatch_display()

    def reset_stopwatch(self) -> None:
        """重置秒表"""
        if self.stopwatch.is_running:
            self.stopwatch.is_running = False
            if self.stopwatch_job:
                self.root.after_cancel(self.stopwatch_job)
                self.stopwatch_job = None

        self._stop_breath_effect()

        self.stopwatch.elapsed_ms = 0
        self.stopwatch.laps = []
        if hasattr(self, 'stopwatch_time_var'):
            self.stopwatch_time_var.set(self._format_time_ms(0))
        if hasattr(self, 'sw_start_btn'):
            self.sw_start_btn.config(text="▶️ 开始")
        if hasattr(self, 'lap_listbox'):
            self.lap_listbox.delete(0, tk.END)

        if hasattr(self, 'seg_color_on') and hasattr(self, 'stopwatch_label'):
            self.stopwatch_label.config(fg=self.seg_color_on)

    def record_lap(self) -> None:
        """记录计次时间"""
        if self.stopwatch.is_running:
            current_time = time.time()
            total_elapsed = int((current_time - self.stopwatch.start_time) * 1000) + self.stopwatch.elapsed_ms

            if self.stopwatch.laps:
                last_lap_time = self.stopwatch.laps[-1].time_ms
                split_ms = total_elapsed - last_lap_time
            else:
                split_ms = total_elapsed

            lap_number = len(self.stopwatch.laps) + 1
            lap_record = LapRecord(
                lap_number=lap_number,
                time_ms=total_elapsed,
                split_ms=split_ms
            )
            self.stopwatch.laps.append(lap_record)

            lap_str = f"圈{lap_number:2d}: {self.format_stopwatch_time(total_elapsed)} (单圈：{self.format_stopwatch_time(split_ms)})"
            self.lap_listbox.insert(0, lap_str)
            self.lap_listbox.yview_moveto(0.0)

    def format_stopwatch_time(self, elapsed_ms: int) -> str:
        """格式化秒表时间"""
        total_seconds = elapsed_ms // 1000
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        milliseconds = (elapsed_ms % 1000) // 10
        return f"{minutes:02d}:{seconds:02d}.{milliseconds:02d}"

    def save_stopwatch_config(self) -> None:
        """保存秒表配置到 config.json"""
        # 秒表配置通常不需要持久化（因为计时状态是临时的）
        # 但可以保存一些设置，如计圈记录（如果需要）
        laps_data = [
            {
                "lap_number": lap.lap_number,
                "time_ms": lap.time_ms,
                "split_ms": lap.split_ms
            }
            for lap in self.stopwatch.laps
        ]
        self.config["stopwatch"] = {
            "laps": laps_data
        }
        self.save_config()

    def load_stopwatch_config(self) -> None:
        """从 config.json 加载秒表配置"""
        # 秒表状态在应用重启后重置
        self.stopwatch = StopwatchState()
        # 可以加载计圈记录（如果需要）
        if hasattr(self, 'config'):
            laps_data = self.config.get("stopwatch", {}).get("laps", [])
            for lap_data in laps_data:
                lap = LapRecord(
                    lap_number=lap_data.get("lap_number", 0),
                    time_ms=lap_data.get("time_ms", 0),
                    split_ms=lap_data.get("split_ms", 0)
                )
                self.stopwatch.laps.append(lap)

    # ========== 以下方法为兼容旧代码的包装方法 ==========

    def stopwatch_start(self) -> None:
        """开始秒表（兼容旧代码）"""
        self.toggle_stopwatch()

    def stopwatch_stop(self) -> None:
        """停止秒表（兼容旧代码）"""
        if self.stopwatch.is_running:
            self.toggle_stopwatch()

    def stopwatch_reset(self) -> None:
        """复位秒表（兼容旧代码）"""
        self.reset_stopwatch()

    def stopwatch_lap(self) -> None:
        """计圈（兼容旧代码）"""
        if self.stopwatch.is_running:
            self.record_lap()

    def _start_breath_effect(self) -> None:
        """启动呼吸灯效果"""
        self._update_breath_effect()

    def _stop_breath_effect(self) -> None:
        """停止呼吸灯效果"""
        if getattr(self, 'breath_job', None):
            self.root.after_cancel(self.breath_job)
            self.breath_job = None

    def _update_breath_effect(self) -> None:
        """更新呼吸灯效果（颜色渐变）"""
        # 更新呼吸相位
        self.breath_phase += 0.1
        if self.breath_phase > 2 * math.pi:
            self.breath_phase -= 2 * math.pi

        # 计算呼吸因子 (0.3 - 1.0)
        breath_factor: float = 0.65 + 0.35 * math.sin(self.breath_phase)

        # 根据主题色计算当前颜色
        if hasattr(self, 'seg_color_on'):
            # 将十六进制颜色转换为 RGB
            r: int = int(self.seg_color_on[1:3], 16)
            g: int = int(self.seg_color_on[3:5], 16)
            b: int = int(self.seg_color_on[5:7], 16)

            # 应用呼吸因子（变暗）
            r = int(r * breath_factor)
            g = int(g * breath_factor)
            b = int(b * breath_factor)

            # 转换回十六进制
            breath_color: str = f"#{r:02x}{g:02x}{b:02x}"
            self.stopwatch_label.config(fg=breath_color)

        # 继续更新
        self.breath_job = self.root.after(50, self._update_breath_effect)


class TimerMixin:
    """倒计时功能混入类"""

    # 倒计时相关属性
    timer_job: Optional[str]
    timer_blink_job: Optional[str]
    timer_breath_job: Optional[str]
    timer_breath_phase: float
    timer_is_blinking: bool
    _timer_blink_state: bool

    def load_timer_config(self) -> None:
        """加载倒计时配置"""
        timer_config: Dict[str, Any] = self.config.get("timer", {})
        if timer_config:
            self.timer.total_seconds = timer_config.get("total_duration", 0)
            self.timer.remaining_seconds = timer_config.get("remaining_time", 0)
            self.timer.sound_enabled = timer_config.get("sound_enabled", True)
            self.timer.preset_name = timer_config.get("last_preset", "")
            if hasattr(self, 'timer_sound_var'):
                self.timer_sound_var.set(self.timer.sound_enabled)
            self.update_timer_display()

    def set_timer_preset(self, seconds: int, name: str) -> None:
        """设置预设倒计时"""
        if self.timer.is_running:
            self.timer_stop()

        self.timer.total_seconds = seconds
        self.timer.remaining_seconds = float(seconds)
        self.timer.preset_name = name
        self.timer.is_running = False

        self.update_timer_display()
        if hasattr(self, 'timer_status_var'):
            self.timer_status_var.set(f"已设置：{name}")

        self.save_timer_config()

    def set_timer_custom(self) -> None:
        """设置自定义倒计时时间"""
        try:
            hours = int(self.timer_hour_entry.get().strip() or 0)
            minutes = int(self.timer_min_entry.get().strip() or 0)
            seconds = int(self.timer_sec_entry.get().strip() or 0)

            total_seconds = hours * 3600 + minutes * 60 + seconds

            if total_seconds <= 0:
                messagebox.showinfo("提示", "请输入有效的时间")
                return

            if self.timer.is_running:
                self.timer_stop()

            self.timer.total_seconds = total_seconds
            self.timer.remaining_seconds = float(total_seconds)
            self.timer.preset_name = "自定义"

            self.update_timer_display()
            if hasattr(self, 'timer_status_var'):
                self.timer_status_var.set("已设置：自定义")

            self.save_timer_config()
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字")

    def toggle_timer(self) -> None:
        """启动/停止倒计时"""
        if self.timer.is_running:
            self.timer_stop()
        else:
            self.timer_start()

    def timer_start(self) -> None:
        """启动倒计时"""
        if self.timer.remaining_seconds <= 0:
            messagebox.showinfo("提示", "请先设置倒计时时间")
            return

        self.timer.is_running = True
        self.timer.start_time: float = time.time()
        self.timer_start_btn.config(text="⏸️ 暂停")
        self._start_timer_breath_effect()
        self._update_timer_loop()

    def timer_stop(self) -> None:
        """暂停倒计时"""
        if self.timer.is_running:
            elapsed: float = time.time() - self.timer.start_time
            self.timer.remaining_seconds = max(0, self.timer.remaining_seconds - elapsed)
            self.timer.is_running = False

            if self.timer_job:
                self.root.after_cancel(self.timer_job)
                self.timer_job = None

            self._stop_timer_breath_effect()
            self.timer_start_btn.config(text="▶️ 继续")
            if hasattr(self, 'timer_status_var'):
                self.timer_status_var.set("已暂停")
            self.update_timer_display()

    def reset_timer(self) -> None:
        """重置倒计时"""
        if self.timer.is_running:
            self.timer_stop()

        self.timer.remaining_seconds = float(self.timer.total_seconds)
        self.timer.is_running = False
        self.timer_start_btn.config(text="▶️ 开始")
        if hasattr(self, 'timer_status_var'):
            self.timer_status_var.set("准备就绪")

        self._stop_timer_breath_effect()
        self._stop_timer_blink()
        self.update_timer_display()
        self.save_timer_config()

    def toggle_timer_sound(self) -> None:
        """切换声音提醒"""
        self.timer.sound_enabled = self.timer_sound_var.get()
        self.save_timer_config()

    def update_timer_display(self) -> None:
        """更新倒计时显示"""
        remaining = int(self.timer.remaining_seconds)
        hours = remaining // 3600
        minutes = (remaining % 3600) // 60
        seconds = remaining % 60
        time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        self.timer_time_var.set(time_str)

    def _update_timer_loop(self) -> None:
        """倒计时更新循环"""
        if self.timer.is_running:
            elapsed: float = time.time() - self.timer.start_time
            self.timer.remaining_seconds = max(0, self.timer.remaining_seconds - elapsed)

            self.update_timer_display()

            if self.timer.remaining_seconds <= 0:
                self._on_timer_complete()
            else:
                self.timer_job = self.root.after(100, self._update_timer_loop)

    def _on_timer_complete(self) -> None:
        """倒计时完成处理"""
        self.timer.is_running = False
        self.timer_start_btn.config(text="▶️ 开始")
        if hasattr(self, 'timer_status_var'):
            self.timer_status_var.set("⏰ 时间到！")

        self._start_timer_blink()

        if self.timer.sound_enabled:
            self.root.bell()

        preset_name: str = self.timer.preset_name if self.timer.preset_name else "倒计时"
        self.send_notification("⏰ 倒计时完成", preset_name)

    def _start_timer_blink(self) -> None:
        """开始闪烁提醒"""
        self.timer_is_blinking = True
        self._timer_blink_state = True
        self._timer_blink_loop()

    def _timer_blink_loop(self) -> None:
        """闪烁循环"""
        if not self.timer_is_blinking:
            return

        self._timer_blink_state = not self._timer_blink_state
        if self._timer_blink_state:
            self.timer_label.config(fg="#ff0000")
            self.timer_frame.config(bg="#330000")
        else:
            self.timer_label.config(fg=self.text_color)
            self.timer_frame.config(bg=self.bg_color)

        self.timer_blink_job = self.root.after(500, self._timer_blink_loop)

    def _stop_timer_blink(self) -> None:
        """停止闪烁"""
        self.timer_is_blinking = False
        if self.timer_blink_job:
            self.root.after_cancel(self.timer_blink_job)
            self.timer_blink_job = None
        self.timer_label.config(fg=self.text_color)
        self.timer_frame.config(bg=self.bg_color)

    def _start_timer_breath_effect(self) -> None:
        """启动计时器呼吸灯效果"""
        self.timer_breath_phase = 0.0
        self._update_timer_breath_effect()

    def _stop_timer_breath_effect(self) -> None:
        """停止计时器呼吸灯效果"""
        if getattr(self, 'timer_breath_job', None):
            self.root.after_cancel(self.timer_breath_job)
            self.timer_breath_job = None
        self.timer_label.config(fg=self.text_color)

    def _update_timer_breath_effect(self) -> None:
        """更新计时器呼吸灯效果"""
        if not self.timer.is_running:
            return

        self.timer_breath_phase += 0.1
        if self.timer_breath_phase > 2 * math.pi:
            self.timer_breath_phase -= 2 * math.pi

        breath_factor = 0.75 + 0.25 * math.sin(self.timer_breath_phase)

        if hasattr(self, 'seg_color_on'):
            r = int(self.seg_color_on[1:3], 16)
            g = int(self.seg_color_on[3:5], 16)
            b = int(self.seg_color_on[5:7], 16)

            r = int(r * breath_factor)
            g = int(g * breath_factor)
            b = int(b * breath_factor)

            breath_color = f"#{r:02x}{g:02x}{b:02x}"
            self.timer_label.config(fg=breath_color)

        self.timer_breath_job = self.root.after(50, self._update_timer_breath_effect)

    def save_timer_config(self) -> None:
        """保存倒计时配置"""
        timer_config = {
            "total_duration": self.timer.total_seconds,
            "remaining_time": self.timer.remaining_seconds,
            "sound_enabled": self.timer.sound_enabled,
            "last_preset": self.timer.preset_name
        }
        self.config["timer"] = timer_config
        self.save_config()


class WindowEventMixin:
    """窗口事件处理混入类"""

    def on_space_key(self, event: tk.Event) -> None:
        """空格键处理"""
        mode: str = self.mode_var.get()
        if mode == 'stopwatch':
            self.toggle_stopwatch()
        elif mode == 'timer':
            self.toggle_timer()

    def on_reset_key(self) -> None:
        """重置当前模式"""
        mode: str = self.mode_var.get()
        if mode == 'stopwatch':
            self.reset_stopwatch()
        elif mode == 'timer':
            self.reset_timer()

    def toggle_fullscreen(self) -> None:
        """切换全屏模式"""
        is_fullscreen: bool = self.config.get("window", {}).get("fullscreen", False)
        new_state: bool = not is_fullscreen

        self.root.attributes("-fullscreen", new_state)
        self.config["window"]["fullscreen"] = new_state
        self._update_button_states()
        self.save_config()

    def toggle_topmost(self) -> None:
        """切换窗口置顶"""
        is_topmost: bool = self.config.get("window", {}).get("always_on_top", False)
        new_state: bool = not is_topmost

        self.root.attributes("-topmost", new_state)
        self.config["window"]["always_on_top"] = new_state
        self._update_button_states()
        self.save_config()

    def _update_button_states(self) -> None:
        """更新按钮状态显示"""
        is_fullscreen: bool = self.config.get("window", {}).get("fullscreen", False)
        is_topmost: bool = self.config.get("window", {}).get("always_on_top", False)

        self.fullscreen_btn.config(text="❐ 退出全屏" if is_fullscreen else "🔲 全屏")
        self.topmost_btn.config(text="📍 取消置顶" if is_topmost else "📌 置顶")

    def on_close(self) -> None:
        """窗口关闭事件处理"""
        if self.stopwatch.is_running:
            self.stopwatch_stop()

        if self.timer.is_running:
            self.timer_stop()

        geometry: str = self.root.geometry()
        try:
            parts: List[str] = geometry.split("+")
            size_part: str = parts[0]
            width: int = int(size_part.split("x")[0])
            height: int = int(size_part.split("x")[1])

            self.config["window"]["width"] = width
            self.config["window"]["height"] = height
            resizable_state = self.root.resizable()
            self.config["window"]["resizable"] = bool(resizable_state[0]) if isinstance(resizable_state, tuple) else True

            if len(parts) >= 3:
                x: int = int(parts[1])
                y: int = int(parts[2])
                self.config["window"]["x"] = x
                self.config["window"]["y"] = y

            self.save_config()
        except Exception as e:
            print(f"⚠️  保存窗口配置失败：{e}")

        self.root.destroy()

    def stopwatch_stop(self) -> None:
        """停止秒表"""
        if self.stopwatch.is_running:
            current_time: float = time.time()
            elapsed: int = int((current_time - self.stopwatch.start_time) * 1000)
            self.stopwatch.elapsed_ms += elapsed
            self.stopwatch.is_running = False

            if self.stopwatch_job:
                self.root.after_cancel(self.stopwatch_job)
                self.stopwatch_job = None

            self.sw_start_btn.config(state=tk.NORMAL)
            self.sw_stop_btn.config(state=tk.DISABLED)
            self.sw_lap_btn.config(state=tk.DISABLED)

            if hasattr(self, 'stopwatch_time_var'):
                self.stopwatch_time_var.set(self._format_time_ms(self.stopwatch.elapsed_ms))


class ClockEvents(StopwatchMixin, TimerMixin, WindowEventMixin):
    """
    时钟事件处理类
    整合所有事件处理混入类
    """
    pass
