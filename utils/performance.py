#!/usr/bin/env python3
"""
ClawClock - 性能监控模块
========================

提供关键路径的性能追踪和监控：
- 函数执行时间追踪
- 帧率监控
- 内存使用追踪
- 性能报告生成

使用示例:
    from utils.performance import PerformanceMonitor, performance_tracker

    # 方法 1: 装饰器方式
    @performance_tracker.track("update_clock")
    def update_clock(self):
        # ...

    # 方法 2: 上下文管理器
    with performance_tracker.track("draw_clock_face"):
        # ...

    # 方法 3: 直接调用
    with PerformanceTimer("operation_name"):
        # ...

    # 获取报告
    report = performance_tracker.get_report()
"""

import time
import functools
from typing import Dict, List, Optional, Any, Callable, TypeVar
from dataclasses import dataclass, field
from contextlib import contextmanager
import statistics

F = TypeVar('F', bound=Callable[..., Any])


@dataclass
class PerformanceRecord:
    """性能记录数据类"""
    name: str
    call_count: int = 0
    total_time: float = 0.0
    min_time: float = float('inf')
    max_time: float = 0.0
    times: List[float] = field(default_factory=list)
    max_samples: int = 1000  # 最大采样数

    def add_sample(self, elapsed: float) -> None:
        """添加采样"""
        self.call_count += 1
        self.total_time += elapsed
        self.min_time = min(self.min_time, elapsed)
        self.max_time = max(self.max_time, elapsed)

        if len(self.times) < self.max_samples:
            self.times.append(elapsed)

    @property
    def avg_time(self) -> float:
        """平均执行时间"""
        if self.call_count == 0:
            return 0.0
        return self.total_time / self.call_count

    @property
    def std_dev(self) -> float:
        """标准差"""
        if len(self.times) < 2:
            return 0.0
        return statistics.stdev(self.times)

    @property
    def percentile_95(self) -> float:
        """95 百分位数"""
        if not self.times:
            return 0.0
        sorted_times = sorted(self.times)
        idx = int(len(sorted_times) * 0.95)
        return sorted_times[min(idx, len(sorted_times) - 1)]

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "name": self.name,
            "call_count": self.call_count,
            "total_time_ms": round(self.total_time * 1000, 2),
            "avg_time_ms": round(self.avg_time * 1000, 2),
            "min_time_ms": round(self.min_time * 1000, 4) if self.min_time != float('inf') else 0,
            "max_time_ms": round(self.max_time * 1000, 4),
            "std_dev_ms": round(self.std_dev * 1000, 4),
            "p95_time_ms": round(self.percentile_95 * 1000, 4)
        }


class PerformanceTimer:
    """性能计时器上下文管理器"""

    def __init__(self, name: str, monitor: Optional['PerformanceMonitor'] = None):
        self.name = name
        self.monitor = monitor or PerformanceMonitor.get_instance()
        self.start_time: float = 0.0
        self.elapsed: float = 0.0

    def __enter__(self) -> 'PerformanceTimer':
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, *args: Any) -> None:
        self.elapsed = time.perf_counter() - self.start_time
        self.monitor.record(self.name, self.elapsed)

    @property
    def elapsed_ms(self) -> float:
        """返回毫秒单位的时间"""
        return self.elapsed * 1000


class PerformanceMonitor:
    """
    性能监控器

    单例模式，提供全局性能追踪功能
    """

    _instance: Optional['PerformanceMonitor'] = None
    _records: Dict[str, PerformanceRecord]
    _enabled: bool
    _frame_times: List[float]
    _fps_sample_count: int = 60  # FPS 采样帧数

    def __init__(self):
        self._records = {}
        self._enabled = True
        self._frame_times = []
        self._start_time = time.time()

    @classmethod
    def get_instance(cls) -> 'PerformanceMonitor':
        """获取单例实例"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        """重置监控器"""
        cls._instance = None

    def enable(self) -> None:
        """启用监控"""
        self._enabled = True

    def disable(self) -> None:
        """禁用监控"""
        self._enabled = False

    def record(self, name: str, elapsed: float) -> None:
        """
        记录性能数据

        Args:
            name: 操作名称
            elapsed: 执行时间（秒）
        """
        if not self._enabled:
            return

        if name not in self._records:
            self._records[name] = PerformanceRecord(name=name)

        self._records[name].add_sample(elapsed)

    def track(self, name: str) -> PerformanceTimer:
        """
        创建追踪器

        Args:
            name: 操作名称

        Returns:
            PerformanceTimer 上下文管理器
        """
        return PerformanceTimer(name, self)

    def track_function(self, name: Optional[str] = None) -> Callable[[F], F]:
        """
        函数追踪装饰器

        Args:
            name: 追踪名称（默认为函数名）

        Returns:
            装饰器函数
        """
        def decorator(func: F) -> F:
            track_name = name or func.__name__

            @functools.wraps(func)
            def wrapper(*args: Any, **kwargs: Any) -> Any:
                with self.track(track_name):
                    return func(*args, **kwargs)

            return wrapper  # type: ignore

        return decorator

    def record_frame(self, frame_time: float) -> None:
        """
        记录帧时间

        Args:
            frame_time: 帧时间（秒）
        """
        if not self._enabled:
            return

        self._frame_times.append(frame_time)
        if len(self._frame_times) > self._fps_sample_count:
            self._frame_times.pop(0)

    def get_fps(self) -> float:
        """获取当前帧率"""
        if not self._frame_times:
            return 0.0

        avg_frame_time = sum(self._frame_times) / len(self._frame_times)
        if avg_frame_time <= 0:
            return 0.0

        return 1.0 / avg_frame_time

    def get_record(self, name: str) -> Optional[PerformanceRecord]:
        """获取特定记录"""
        return self._records.get(name)

    def get_all_records(self) -> Dict[str, PerformanceRecord]:
        """获取所有记录"""
        return self._records.copy()

    def get_slowest(self, count: int = 10) -> List[PerformanceRecord]:
        """获取最慢的操作"""
        records = [r for r in self._records.values() if r.call_count > 0]
        records.sort(key=lambda r: r.avg_time, reverse=True)
        return records[:count]

    def get_report(self) -> Dict[str, Any]:
        """
        生成性能报告

        Returns:
            性能报告字典
        """
        running_time = time.time() - self._start_time

        return {
            "running_time_seconds": round(running_time, 2),
            "total_operations": len(self._records),
            "total_calls": sum(r.call_count for r in self._records.values()),
            "current_fps": round(self.get_fps(), 2),
            "operations": [r.to_dict() for r in self._records.values()],
            "slowest_operations": [r.to_dict() for r in self.get_slowest(5)]
        }

    def print_report(self) -> None:
        """打印性能报告到控制台"""
        report = self.get_report()

        print("\n" + "=" * 60)
        print("ClawClock 性能报告")
        print("=" * 60)
        print(f"运行时间：{report['running_time_seconds']:.2f} 秒")
        print(f"追踪操作数：{report['total_operations']}")
        print(f"总调用次数：{report['total_calls']}")
        print(f"当前帧率：{report['current_fps']:.2f} FPS")
        print()

        if report['slowest_operations']:
            print("最慢的操作 (Top 5):")
            print("-" * 60)
            print(f"{'名称':<30} {'调用':>6} {'平均':>10} {'最大':>10} {'P95':>10}")
            print("-" * 60)

            for op in report['slowest_operations']:
                print(f"{op['name']:<30} {op['call_count']:>6} "
                      f"{op['avg_time_ms']:>8.2f}ms {op['max_time_ms']:>8.2f}ms "
                      f"{op['p95_time_ms']:>8.2f}ms")

            print()

        # 显示所有操作
        print("所有操作详情:")
        print("-" * 60)
        for record in self._records.values():
            data = record.to_dict()
            print(f"{data['name']}: {data['call_count']} 次调用，"
                  f"平均 {data['avg_time_ms']:.2f}ms, "
                  f"总计 {data['total_time_ms']:.2f}ms")

        print("=" * 60)


# 全局性能监控实例
performance_tracker = PerformanceMonitor.get_instance()


def track_performance(name: Optional[str] = None) -> Callable[[F], F]:
    """
    性能追踪装饰器

    用法:
        @track_performance()
        def my_function():
            pass

        @track_performance("custom_name")
        def another_function():
            pass
    """
    return performance_tracker.track_function(name)


@contextmanager
def measure_time(name: str):
    """
    测量时间的上下文管理器

    用法:
        with measure_time("operation"):
            # 执行的代码
    """
    with performance_tracker.track(name):
        yield


# 时钟应用特定的性能监控
class ClockPerformanceMonitor:
    """时钟应用性能监控"""

    def __init__(self):
        self.monitor = performance_tracker
        self._last_frame_time = time.perf_counter()

    def start_frame(self) -> None:
        """标记帧开始"""
        self._last_frame_time = time.perf_counter()

    def end_frame(self) -> None:
        """标记帧结束并记录"""
        frame_time = time.perf_counter() - self._last_frame_time
        self.monitor.record_frame(frame_time)
        self.monitor.record("frame_time", frame_time)

    def track_update_clock(self, func: F) -> F:
        """追踪时钟更新函数"""
        return self.monitor.track_function("update_clock")(func)

    def track_draw_analog(self, func: F) -> F:
        """追踪模拟时钟绘制"""
        return self.monitor.track_function("draw_analog_clock")(func)

    def track_draw_digital(self, func: F) -> F:
        """追踪数字时钟绘制"""
        return self.monitor.track_function("draw_digital_clock")(func)

    def track_render(self, func: F) -> F:
        """追踪渲染函数"""
        return self.monitor.track_function("render")(func)


# 导出
__all__ = [
    'PerformanceMonitor',
    'PerformanceTimer',
    'PerformanceRecord',
    'performance_tracker',
    'track_performance',
    'measure_time',
    'ClockPerformanceMonitor',
]
