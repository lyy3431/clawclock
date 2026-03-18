# ClawClock 日志系统模块
"""
提供日志记录功能
"""
import logging
import sys
from typing import Optional
from datetime import datetime


class ClockLogger:
    """ClawClock 日志记录器"""
    
    def __init__(self, name: str = "clawclock", level: int = logging.INFO):
        """
        初始化日志记录器
        
        Args:
            name: 日志名称
            level: 日志级别
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        # 避免重复添加处理器
        if not self.logger.handlers:
            # 控制台输出
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(level)
            
            # 日志格式
            formatter = logging.Formatter(
                '[%(asctime)s] [%(levelname)s] %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            console_handler.setFormatter(formatter)
            
            self.logger.addHandler(console_handler)
        
        self._context = {}
    
    def set_context(self, **kwargs) -> None:
        """设置上下文"""
        self._context.update(kwargs)
    
    def clear_context(self) -> None:
        """清空上下文"""
        self._context.clear()
    
    def _format_message(self, message: str) -> str:
        """格式化消息"""
        if self._context:
            context_str = " ".join(f"{k}={v}" for k, v in self._context.items())
            return f"[{context_str}] {message}"
        return message
    
    def debug(self, message: str, **kwargs) -> None:
        """调试日志"""
        self.logger.debug(self._format_message(message))
    
    def info(self, message: str, **kwargs) -> None:
        """信息日志"""
        self.logger.info(self._format_message(message))
    
    def warning(self, message: str, **kwargs) -> None:
        """警告日志"""
        self.logger.warning(self._format_message(message))
    
    def error(self, message: str, **kwargs) -> None:
        """错误日志"""
        self.logger.error(self._format_message(message))
    
    def critical(self, message: str, **kwargs) -> None:
        """严重错误日志"""
        self.logger.critical(self._format_message(message))


# 全局日志记录器实例
_logger: Optional[ClockLogger] = None


def get_logger(name: str = "clawclock") -> ClockLogger:
    """获取全局日志记录器"""
    global _logger
    if _logger is None:
        _logger = ClockLogger(name)
    return _logger


def debug(message: str, **kwargs) -> None:
    """调试日志"""
    get_logger().debug(message, **kwargs)


def info(message: str, **kwargs) -> None:
    """信息日志"""
    get_logger().info(message, **kwargs)


def warning(message: str, **kwargs) -> None:
    """警告日志"""
    get_logger().warning(message, **kwargs)


def error(message: str, **kwargs) -> None:
    """错误日志"""
    get_logger().error(message, **kwargs)


def critical(message: str, **kwargs) -> None:
    """严重错误日志"""
    get_logger().critical(message, **kwargs)
