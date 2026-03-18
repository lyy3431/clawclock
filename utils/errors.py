# ClawClock 错误处理模块
"""
统一的错误处理机制
"""
from typing import Optional


class ClockError(Exception):
    """ClawClock 基础异常类"""
    pass


class ConfigError(ClockError):
    """配置错误"""
    def __init__(self, message: str, config_key: Optional[str] = None):
        super().__init__(f"配置错误: {message}")
        self.config_key = config_key


class ThemeError(ClockError):
    """主题错误"""
    def __init__(self, message: str, theme_name: Optional[str] = None):
        super().__init__(f"主题错误: {message}")
        self.theme_name = theme_name


class AlarmError(ClockError):
    """闹钟错误"""
    def __init__(self, message: str, alarm_time: Optional[str] = None):
        super().__init__(f"闹钟错误: {message}")
        self.alarm_time = alarm_time


class TimerError(ClockError):
    """倒计时错误"""
    def __init__(self, message: str, preset_name: Optional[str] = None):
        super().__init__(f"倒计时错误: {message}")
        self.preset_name = preset_name


class IOError(ClockError):
    """IO错误"""
    def __init__(self, message: str, file_path: Optional[str] = None):
        super().__init__(f"IO错误: {message}")
        self.file_path = file_path


def validate_time_format(time_str: str) -> bool:
    """
    验证时间格式
    
    Args:
        time_str: 时间字符串 (HH:MM 或 HH:MM:SS)
        
    Returns:
        是否有效
    """
    import re
    pattern = r'^([01]\d|2[0-3]):([0-5]\d)(:([0-5]\d))?$'
    return bool(re.match(pattern, time_str))


def validate_preset_time(hours: int, minutes: int, seconds: int) -> None:
    """
    验证预设时间
    
    Args:
        hours: 小时
        minutes: 分钟
        seconds: 秒
        
    Raises:
        TimerError: 时间超出范围
    """
    if not (0 <= hours <= 99):
        raise TimerError("小时超出范围 (0-99)")
    if not (0 <= minutes <= 59):
        raise TimerError("分钟超出范围 (0-59)")
    if not (0 <= seconds <= 59):
        raise TimerError("秒超出范围 (0-59)")


def safe_execute(func, *args, default=None, error_handler=None):
    """
    安全执行函数
    
    Args:
        func: 待执行的函数
        *args: 函数参数
        default: 出错时的默认返回值
        error_handler: 错误处理函数
        
    Returns:
        函数返回值或默认值
    """
    try:
        return func(*args)
    except Exception as e:
        if error_handler:
            error_handler(e)
        return default


class ErrorLogger:
    """错误日志记录器"""
    
    def __init__(self):
        self.errors = []
    
    def log(self, error: Exception, context: Optional[dict] = None) -> None:
        """
        记录错误
        
        Args:
            error: 异常对象
            context: 上下文信息
        """
        error_info = {
            "type": type(error).__name__,
            "message": str(error),
            "context": context or {}
        }
        self.errors.append(error_info)
        print(f"❌ {error_info['type']}: {error_info['message']}")
    
    def get_errors(self) -> list:
        """获取所有错误"""
        return self.errors
    
    def clear(self) -> None:
        """清空错误日志"""
        self.errors = []


# 全局错误记录器实例
_error_logger = ErrorLogger()


def get_error_logger() -> ErrorLogger:
    """获取全局错误记录器"""
    return _error_logger


def log_error(error: Exception, context: Optional[dict] = None) -> None:
    """记录错误"""
    get_error_logger().log(error, context)
