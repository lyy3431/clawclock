#!/usr/bin/env python3
"""
ClawClock - 闹钟管理模块
========================

负责闹钟相关功能：
- 闹钟触发和提醒
- 闹钟管理对话框
- 系统通知
"""

import time
import tkinter as tk
from tkinter import messagebox
from typing import Optional, Any, List, Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from clock import ClockApp

from clock_core import Alarm


class AlarmUIMixin:
    """闹钟 UI 和事件处理混入类"""

    # 闹钟列表框
    alarm_listbox: tk.Listbox

    def _trigger_alarm(self, alarm: Alarm) -> None:
        """触发闹钟（渐入铃声）"""
        label_text: str = f"闹钟时间到！\n\n{alarm.time}"
        if alarm.label:
            label_text += f"\n{alarm.label}"

        # 显示闹钟对话框
        dialog: tk.Toplevel = tk.Toplevel(self.root)
        dialog.title("⏰ 闹钟")
        dialog.geometry("300x200")
        dialog.attributes("-topmost", True)

        # 居中显示
        dialog_x: int = int(self.root.winfo_x() + self.root.winfo_width() / 2 - 150)
        dialog_y: int = int(self.root.winfo_y() + self.root.winfo_height() / 2 - 100)
        dialog.geometry(f"300x200+{dialog_x}+{dialog_y}")

        label: tk.Label = tk.Label(dialog, text=label_text, font=("Arial", 16), pady=20)
        label.pack()

        def stop_alarm() -> None:
            self.alarm_triggered = False
            dialog.destroy()

        btn_frame: tk.Frame = tk.Frame(dialog)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="停止闹钟", command=stop_alarm, width=10).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="稍后提醒",
                  command=lambda: self._snooze_alarm(dialog, alarm), width=10).pack(side=tk.LEFT, padx=10)

        # 渐入铃声：蜂鸣 3 次，每次间隔 1 秒
        for i in range(3):
            try:
                self.root.bell()
            except Exception:
                pass
            if i < 2:
                time.sleep(1)

        # 发送系统通知
        self.send_notification("⏰ 闹钟提醒", f"{alarm.time} - {alarm.label}" if alarm.label else alarm.time)

    def _snooze_alarm(self, dialog: tk.Toplevel, alarm: Alarm) -> None:
        """稍后提醒（小睡功能）"""
        self.alarm_triggered = False
        dialog.destroy()

        def snooze_callback() -> None:
            self.alarm_triggered = True
            self.root.after(0, self._trigger_alarm, alarm)

        snooze_ms: int = alarm.snooze_minutes * 60 * 1000
        self.root.after(snooze_ms, snooze_callback)

    def send_notification(self, title: str, message: str) -> None:
        """发送系统通知（Linux notify-send）"""
        try:
            import subprocess
            subprocess.run(['notify-send', title, message], timeout=2, capture_output=True)
        except Exception:
            pass

    def show_alarm_dialog(self) -> None:
        """显示闹钟管理对话框"""
        dialog: tk.Toplevel = tk.Toplevel(self.root)
        dialog.title("⏰ 闹钟管理")
        dialog.geometry("400x300")
        dialog.attributes("-topmost", True)

        # 居中显示
        dialog_x: int = int(self.root.winfo_x() + self.root.winfo_width() / 2 - 200)
        dialog_y: int = int(self.root.winfo_y() + self.root.winfo_height() / 2 - 150)
        dialog.geometry(f"400x300+{dialog_x}+{dialog_y}")

        # 闹钟列表框架
        list_frame: tk.Frame = tk.Frame(dialog)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 创建列表框
        scrollbar: tk.Scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.alarm_listbox = tk.Listbox(list_frame, height=8, yscrollcommand=scrollbar.set)
        self.alarm_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.alarm_listbox.yview)

        # 填充闹钟列表
        self._refresh_alarm_listbox()

        # 按钮框架
        btn_frame: tk.Frame = tk.Frame(dialog)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="添加闹钟",
                  command=lambda: self._add_alarm_from_dialog(dialog)).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="删除选中",
                  command=lambda: self._delete_selected_alarm(dialog)).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="切换状态",
                  command=lambda: self._toggle_selected_alarm(dialog)).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="关闭", command=dialog.destroy).pack(side=tk.RIGHT, padx=5)

    def _refresh_alarm_listbox(self) -> None:
        """刷新闹钟列表框"""
        self.alarm_listbox.delete(0, tk.END)
        day_labels: List[str] = ["一", "二", "三", "四", "五", "六", "日"]
        for i, alarm in enumerate(self.alarms):
            status: str = "✓" if alarm.enabled else "✗"
            label: str = f"{status} {alarm.time}"
            if alarm.label:
                label += f" - {alarm.label}"
            if alarm.repeat_days:
                days_str: str = "".join(day_labels[d] for d in sorted(alarm.repeat_days))
                label += f" [{days_str}]"
            else:
                label += " [仅一次]"
            self.alarm_listbox.insert(tk.END, label)

    def _add_alarm_from_dialog(self, dialog: tk.Toplevel) -> None:
        """从对话框添加闹钟（带重复周期选择）"""
        add_dialog: tk.Toplevel = tk.Toplevel(dialog)
        add_dialog.title("添加闹钟")
        add_dialog.geometry("350x280")
        add_dialog.attributes("-topmost", True)

        # 时间输入
        tk.Label(add_dialog, text="时间 (HH:MM):").pack(pady=5)
        time_entry: tk.Entry = tk.Entry(add_dialog)
        time_entry.pack(pady=5)
        time_entry.insert(0, "07:00")

        # 标签输入
        tk.Label(add_dialog, text="标签 (可选):").pack(pady=5)
        label_entry: tk.Entry = tk.Entry(add_dialog)
        label_entry.pack(pady=5)

        # 重复周期选择
        tk.Label(add_dialog, text="重复周期:").pack(pady=(10, 5))

        # 快捷按钮
        quick_frame: tk.Frame = tk.Frame(add_dialog)
        quick_frame.pack(pady=5)

        repeat_vars: List[tk.BooleanVar] = [tk.BooleanVar() for _ in range(7)]

        def set_weekdays() -> None:
            for i in range(7):
                repeat_vars[i].set(i < 5)

        def set_weekends() -> None:
            for i in range(7):
                repeat_vars[i].set(i >= 5)

        def set_everyday() -> None:
            for i in range(7):
                repeat_vars[i].set(True)

        tk.Button(quick_frame, text="工作日", command=set_weekdays, width=8).pack(side=tk.LEFT, padx=2)
        tk.Button(quick_frame, text="周末", command=set_weekends, width=8).pack(side=tk.LEFT, padx=2)
        tk.Button(quick_frame, text="每天", command=set_everyday, width=8).pack(side=tk.LEFT, padx=2)

        # 7 个复选框（周一到周日）
        days_frame: tk.Frame = tk.Frame(add_dialog)
        days_frame.pack(pady=5)

        day_labels: List[str] = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        for i in range(7):
            cb: tk.Checkbutton = tk.Checkbutton(days_frame, text=day_labels[i], variable=repeat_vars[i])
            cb.pack(side=tk.LEFT, padx=3)

        def add() -> None:
            time_str: str = time_entry.get().strip()
            label: str = label_entry.get().strip()
            selected_days: List[int] = [i for i in range(7) if repeat_vars[i].get()]
            if self.add_alarm(time_str, label, selected_days):
                self._refresh_alarm_listbox()
                add_dialog.destroy()
            else:
                messagebox.showerror("错误", "无效的时间格式，请使用 HH:MM 格式")

        tk.Button(add_dialog, text="添加", command=add).pack(pady=10)

    def _delete_selected_alarm(self, dialog: tk.Toplevel) -> None:
        """删除选中的闹钟"""
        selection = self.alarm_listbox.curselection()
        if selection:
            index = selection[0]
            self.remove_alarm(index)
            self._refresh_alarm_listbox()
        else:
            messagebox.showwarning("提示", "请先选择一个闹钟")

    def _toggle_selected_alarm(self, dialog: tk.Toplevel) -> None:
        """切换选中闹钟的状态"""
        selection = self.alarm_listbox.curselection()
        if selection:
            index = selection[0]
            self.toggle_alarm(index)
            self._refresh_alarm_listbox()
        else:
            messagebox.showwarning("提示", "请先选择一个闹钟")
