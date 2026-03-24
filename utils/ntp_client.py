#!/usr/bin/env python3
"""
ClawClock - NTP 网络时间同步模块
================================

提供网络时间协议 (NTP) 客户端功能，用于同步系统时间。

功能:
- NTP 服务器查询
- 时间偏差计算
- 自动/手动同步
- 同步历史记录
"""

import socket
import struct
import time
import datetime
import threading
from typing import Optional, Tuple, Dict, List, Any
from dataclasses import dataclass, field
import json
import os

# Python 3.10+ socket.timeout is an alias of TimeoutError
# Use socket.timeout for compatibility
SocketTimeout = getattr(socket, 'timeout', TimeoutError)


# ==================== NTP 常量 ====================
# 常用 NTP 服务器池
NTP_SERVERS = [
    "pool.ntp.org",
    "time.google.com",
    "time.cloudflare.com",
    "time.apple.com",
    "cn.pool.ntp.org",      # 中国 NTP 服务器池
    "ntp.aliyun.com",       # 阿里云 NTP
    "ntp.tencent.com",      # 腾讯云 NTP
]

# 默认 NTP 服务器
DEFAULT_NTP_SERVER = "pool.ntp.org"

# NTP 端口
NTP_PORT = 123

# NTP 请求超时 (秒)
NTP_TIMEOUT = 5

# 自动同步间隔 (小时)
DEFAULT_AUTO_SYNC_INTERVAL = 24

# 时间偏差阈值 (秒)，超过此值建议同步
TIME_DRIFT_THRESHOLD = 1.0

# NTP 纪元 (1900-01-01 00:00:00 UTC)
NTP_TIMESTAMP_DELTA = 2208988800


@dataclass
class NTPResult:
    """NTP 查询结果数据类

    Attributes:
        success: 查询是否成功
        ntp_time: NTP 服务器返回的 UTC 时间
        local_time: 本地查询时的 UTC 时间
        offset: 时间偏差 (秒)，正数表示本地时间快
        delay: 网络延迟 (秒)
        server: 使用的 NTP 服务器
        error: 错误信息 (如果失败)
        query_time: 查询时间戳
    """
    success: bool
    ntp_time: Optional[datetime.datetime] = None
    local_time: Optional[datetime.datetime] = None
    offset: float = 0.0
    delay: float = 0.0
    server: str = ""
    error: Optional[str] = None
    query_time: datetime.datetime = field(default_factory=datetime.datetime.now)

    def __str__(self) -> str:
        if self.success:
            return (f"NTP 同步成功 | 服务器：{self.server} | "
                    f"偏差：{self.offset:+.3f}秒 | 延迟：{self.delay*1000:.1f}ms")
        else:
            return f"NTP 同步失败 | 服务器：{self.server} | 错误：{self.error}"


@dataclass
class SyncHistory:
    """同步历史记录数据类

    Attributes:
        timestamp: 同步时间
        server: NTP 服务器
        offset: 同步前的时间偏差
        adjusted: 是否进行了调整
    """
    timestamp: datetime.datetime
    server: str
    offset: float
    adjusted: bool


class NTPClient:
    """NTP 客户端

    用于查询 NTP 服务器时间并计算本地时间偏差。

    Usage:
        client = NTPClient()
        result = client.get_time()
        if result.success:
            print(f"时间偏差：{result.offset}秒")
    """

    def __init__(self, servers: Optional[List[str]] = None):
        """初始化 NTP 客户端

        Args:
            servers: NTP 服务器列表，默认使用内置服务器池
        """
        self.servers = servers or NTP_SERVERS.copy()
        self._socket: Optional[socket.socket] = None

    def _create_socket(self) -> socket.socket:
        """创建 UDP 套接字"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(NTP_TIMEOUT)
        return sock

    def _build_ntp_packet(self) -> bytes:
        """构建 NTP 请求包

        NTP 包格式 (48 字节):
        - LI (2 bits): 闰秒指示器
        - VN (3 bits): 版本号 (设为 3)
        - Mode (3 bits): 模式 (3=客户端)
        - Stratum (8 bits): 层级
        - Poll (8 bits): 轮询间隔
        - Precision (8 bits): 精度
        - Root Delay (32 bits)
        - Root Dispersion (32 bits)
        - Reference ID (32 bits)
        - Reference Timestamp (64 bits)
        - Origin Timestamp (64 bits)
        - Receive Timestamp (64 bits)
        - Transmit Timestamp (64 bits)

        Returns:
            bytes: NTP 请求包
        """
        # 构建 NTP 包头部
        # LI=0 (无闰秒), VN=3 (版本 3), Mode=3 (客户端)
        header = 0b00011011  # 0x1B
        return struct.pack('!B', header) + bytes(47)  # 48 字节 NTP 包

    def _parse_ntp_response(self, data: bytes, 
                            send_time: float) -> Tuple[datetime.datetime, float, float]:
        """解析 NTP 响应包

        使用简化方法：仅计算往返延迟和估算偏差
        完整的 NTP 需要 4 个时间戳，但简单模式服务器只返回部分数据

        Args:
            data: NTP 响应数据
            send_time: 发送请求时的本地时间戳

        Returns:
            Tuple[datetime.datetime, float, float]:
                (NTP 时间，时间偏差，网络延迟)
        """
        if len(data) < 48:
            raise ValueError("NTP 响应数据过短")

        # 获取返回时的本地时间
        return_time = time.time()
        
        # 计算往返时间 (RTT)
        rtt = return_time - send_time
        
        # 估算单程延迟
        delay = rtt / 2
        
        # 解析服务器的 Transmit Timestamp (字节 40-47)
        # 如果服务器返回有效时间
        transmit_timestamp = struct.unpack('!Q', data[40:48])[0]
        
        if transmit_timestamp > 0:
            # 有效 NTP 时间戳
            server_time = (transmit_timestamp / 2**32) - NTP_TIMESTAMP_DELTA
            ntp_datetime = datetime.datetime.fromtimestamp(server_time, tz=datetime.timezone.utc)
            
            # 计算时间偏差
            # offset = server_time - (send_time + return_time) / 2
            avg_local_time = (send_time + return_time) / 2
            offset = server_time - avg_local_time
        else:
            # 服务器返回零时间（简化模式），使用本地时间估算
            ntp_datetime = datetime.datetime.fromtimestamp(return_time - delay, tz=datetime.timezone.utc)
            offset = 0.0

        return ntp_datetime, offset, delay

    def get_time(self, server: Optional[str] = None) -> NTPResult:
        """从 NTP 服务器获取时间

        Args:
            server: NTP 服务器地址，默认自动选择

        Returns:
            NTPResult: NTP 查询结果
        """
        server = server or self.servers[0]

        try:
            # 解析服务器地址
            socket.inet_aton(server)  # 检查是否为 IP
            server_addr = server
        except (OSError, ValueError):
            # 域名解析
            try:
                server_addr = socket.gethostbyname(server)
            except Exception as e:
                return NTPResult(
                    success=False,
                    server=server,
                    error=f"DNS 解析失败：{e}"
                )

        try:
            self._socket = self._create_socket()
            
            # 记录发送时间
            send_time = time.time()
            local_datetime = datetime.datetime.fromtimestamp(send_time, tz=datetime.timezone.utc)

            # 发送 NTP 请求
            packet = self._build_ntp_packet()
            self._socket.sendto(packet, (server_addr, NTP_PORT))

            # 接收响应
            data, _ = self._socket.recvfrom(1024)

            # 解析响应
            ntp_time, offset, delay = self._parse_ntp_response(data, send_time)

            return NTPResult(
                success=True,
                ntp_time=ntp_time,
                local_time=local_datetime,
                offset=offset,
                delay=delay,
                server=server
            )

        except SocketTimeout:
            return NTPResult(
                success=False,
                server=server,
                error="NTP 服务器响应超时"
            )
        except (OSError, IOError) as e:
            return NTPResult(
                success=False,
                server=server,
                error=f"网络错误：{e}"
            )
        except Exception as e:
            return NTPResult(
                success=False,
                server=server,
                error=f"未知错误：{e}"
            )
        finally:
            if self._socket:
                self._socket.close()
                self._socket = None

    def get_time_from_multiple(self, count: int = 3) -> List[NTPResult]:
        """从多个 NTP 服务器获取时间

        Args:
            count: 尝试的服务器数量

        Returns:
            List[NTPResult]: 所有查询结果
        """
        results = []
        servers_to_try = self.servers[:min(count, len(self.servers))]

        for server in servers_to_try:
            result = self.get_time(server)
            results.append(result)
            if result.success:
                break

        return results

    def get_best_time(self) -> NTPResult:
        """获取最佳的 NTP 时间（从多个服务器中选择）

        策略：
        1. 优先选择成功的结果
        2. 在成功结果中选择延迟最低的

        Returns:
            NTPResult: 最佳 NTP 查询结果
        """
        results = self.get_time_from_multiple(3)

        # 筛选成功的结果
        successful = [r for r in results if r.success]

        if not successful:
            # 全部失败，返回第一个错误结果
            return results[0] if results else NTPResult(
                success=False,
                error="所有 NTP 服务器均不可用"
            )

        # 选择延迟最低的结果
        best = min(successful, key=lambda r: r.delay)
        return best


class NTPSyncManager:
    """NTP 同步管理器

    管理 NTP 同步的配置、历史记录和自动同步。

    Usage:
        manager = NTPSyncManager()
        manager.load_history()
        
        # 手动同步
        result = manager.sync_now()
        
        # 启用自动同步
        manager.enable_auto_sync(interval_hours=24)
    """

    def __init__(self, history_file: str = "ntp_history.json"):
        """初始化同步管理器

        Args:
            history_file: 历史记录文件路径
        """
        self.history_file = history_file
        self.client = NTPClient()
        self.history: List[SyncHistory] = []
        self.auto_sync_enabled = False
        self.auto_sync_interval = DEFAULT_AUTO_SYNC_INTERVAL  # 小时
        self._auto_sync_thread: Optional[threading.Thread] = None
        self._stop_auto_sync = False
        self.last_sync_result: Optional[NTPResult] = None
        self.last_sync_time: Optional[datetime.datetime] = None

    def load_history(self) -> None:
        """加载同步历史"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.history = [
                        SyncHistory(
                            timestamp=datetime.datetime.fromisoformat(h['timestamp']),
                            server=h['server'],
                            offset=h['offset'],
                            adjusted=h['adjusted']
                        )
                        for h in data.get('history', [])
                    ]
                    self.auto_sync_enabled = data.get('auto_sync_enabled', False)
                    self.auto_sync_interval = data.get('auto_sync_interval', DEFAULT_AUTO_SYNC_INTERVAL)
            except (json.JSONDecodeError, IOError, KeyError) as e:
                print(f"⚠️  NTP 历史加载失败：{e}")
                self.history = []

    def save_history(self) -> bool:
        """保存同步历史"""
        try:
            data = {
                'history': [
                    {
                        'timestamp': h.timestamp.isoformat(),
                        'server': h.server,
                        'offset': h.offset,
                        'adjusted': h.adjusted
                    }
                    for h in self.history[-100:]  # 只保留最近 100 条
                ],
                'auto_sync_enabled': self.auto_sync_enabled,
                'auto_sync_interval': self.auto_sync_interval
            }
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except IOError as e:
            print(f"⚠️  NTP 历史保存失败：{e}")
            return False

    def sync_now(self, server: Optional[str] = None) -> NTPResult:
        """立即执行 NTP 同步

        Args:
            server: 指定 NTP 服务器，默认自动选择

        Returns:
            NTPResult: 同步结果
        """
        result = self.client.get_time(server) if server else self.client.get_best_time()
        
        if result.success:
            self.last_sync_result = result
            self.last_sync_time = datetime.datetime.now()
            
            # 记录历史
            self.history.append(SyncHistory(
                timestamp=self.last_sync_time,
                server=result.server,
                offset=result.offset,
                adjusted=False  # 仅查询，未调整系统时间
            ))
            self.save_history()

        return result

    def check_time_drift(self) -> Tuple[bool, float]:
        """检查时间偏差是否超过阈值

        Returns:
            Tuple[bool, float]: (是否需要调整，偏差秒数)
        """
        result = self.sync_now()
        if result.success:
            needs_adjustment = abs(result.offset) > TIME_DRIFT_THRESHOLD
            return needs_adjustment, result.offset
        return False, 0.0

    def enable_auto_sync(self, interval_hours: int = DEFAULT_AUTO_SYNC_INTERVAL) -> None:
        """启用自动同步

        Args:
            interval_hours: 同步间隔 (小时)
        """
        self.auto_sync_enabled = True
        self.auto_sync_interval = interval_hours
        self._start_auto_sync_thread()
        self.save_history()

    def disable_auto_sync(self) -> None:
        """禁用自动同步"""
        self.auto_sync_enabled = False
        self._stop_auto_sync_thread()
        self.save_history()

    def _start_auto_sync_thread(self) -> None:
        """启动自动同步线程"""
        if self._auto_sync_thread and self._auto_sync_thread.is_alive():
            return

        self._stop_auto_sync = False
        self._auto_sync_thread = threading.Thread(target=self._auto_sync_loop, daemon=True)
        self._auto_sync_thread.start()

    def _stop_auto_sync_thread(self) -> None:
        """停止自动同步线程"""
        self._stop_auto_sync = True
        if self._auto_sync_thread:
            self._auto_sync_thread.join(timeout=5)
            self._auto_sync_thread = None

    def _auto_sync_loop(self) -> None:
        """自动同步循环"""
        while not self._stop_auto_sync:
            # 等待到下次同步时间
            for _ in range(int(self.auto_sync_interval * 3600)):
                if self._stop_auto_sync:
                    break
                time.sleep(1)

            if not self._stop_auto_sync:
                self.sync_now()

    def get_sync_status(self) -> Dict[str, Any]:
        """获取同步状态

        Returns:
            Dict[str, Any]: 同步状态信息
        """
        return {
            'auto_sync_enabled': self.auto_sync_enabled,
            'auto_sync_interval': self.auto_sync_interval,
            'last_sync_time': self.last_sync_time.isoformat() if self.last_sync_time else None,
            'last_sync_offset': self.last_sync_result.offset if self.last_sync_result else None,
            'last_sync_server': self.last_sync_result.server if self.last_sync_result else None,
            'total_sync_count': len(self.history),
            'successful_sync_count': len([h for h in self.history if abs(h.offset) < 10])
        }

    def get_history(self, limit: int = 10) -> List[SyncHistory]:
        """获取同步历史

        Args:
            limit: 返回记录数量

        Returns:
            List[SyncHistory]: 同步历史记录
        """
        return self.history[-limit:]


# ==================== 全局工具函数 ====================

def get_ntp_time(server: str = DEFAULT_NTP_SERVER) -> Optional[datetime.datetime]:
    """便捷函数：获取 NTP 时间

    Args:
        server: NTP 服务器地址

    Returns:
        Optional[datetime.datetime]: NTP 时间，失败返回 None
    """
    client = NTPClient()
    result = client.get_time(server)
    return result.ntp_time if result.success else None


def check_time_accuracy() -> Tuple[bool, float]:
    """便捷函数：检查时间准确性

    Returns:
        Tuple[bool, float]: (时间是否准确，偏差秒数)
    """
    manager = NTPSyncManager()
    result = manager.sync_now()
    if result.success:
        is_accurate = abs(result.offset) < TIME_DRIFT_THRESHOLD
        return is_accurate, result.offset
    return True, 0.0


# ==================== 测试代码 ====================

if __name__ == "__main__":
    print("🕐 ClawClock NTP 时间同步测试")
    print("=" * 50)

    # 测试 1: 基本 NTP 查询
    print("\n【测试 1】基本 NTP 查询")
    client = NTPClient()
    result = client.get_time("ntp.aliyun.com")
    print(result)

    # 测试 2: 自动选择最佳服务器
    print("\n【测试 2】自动选择最佳服务器")
    best_result = client.get_best_time()
    print(best_result)

    # 测试 3: 同步管理器
    print("\n【测试 3】同步管理器")
    manager = NTPSyncManager()
    manager.load_history()
    status = manager.get_sync_status()
    print(f"同步状态：{status}")

    # 测试 4: 检查时间偏差
    print("\n【测试 4】检查时间偏差")
    needs_adjust, offset = manager.check_time_drift()
    print(f"需要调整：{needs_adjust}, 偏差：{offset:+.3f}秒")
