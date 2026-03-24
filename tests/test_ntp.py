#!/usr/bin/env python3
"""
ClawClock - NTP 时间同步测试
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import datetime
import socket
from utils.ntp_client import (
    NTPClient, NTPResult, NTPSyncManager, SyncHistory,
    NTP_SERVERS, DEFAULT_NTP_SERVER
)


class TestNTPResult(unittest.TestCase):
    """测试 NTPResult 数据类"""

    def test_success_result_str(self):
        """测试成功结果的字符串表示"""
        result = NTPResult(
            success=True,
            ntp_time=datetime.datetime.now(),
            local_time=datetime.datetime.now(),
            offset=0.5,
            delay=0.03,
            server="pool.ntp.org"
        )
        result_str = str(result)
        self.assertIn("成功", result_str)
        self.assertIn("pool.ntp.org", result_str)
        self.assertIn("+0.500", result_str)

    def test_failure_result_str(self):
        """测试失败结果的字符串表示"""
        result = NTPResult(
            success=False,
            server="pool.ntp.org",
            error="连接超时"
        )
        result_str = str(result)
        self.assertIn("失败", result_str)
        self.assertIn("连接超时", result_str)


class TestNTPClient(unittest.TestCase):
    """测试 NTPClient 类"""

    def test_init_default_servers(self):
        """测试初始化时使用默认服务器列表"""
        client = NTPClient()
        self.assertEqual(client.servers, NTP_SERVERS)

    def test_init_custom_servers(self):
        """测试初始化时使用自定义服务器列表"""
        custom_servers = ["time.google.com", "time.cloudflare.com"]
        client = NTPClient(servers=custom_servers)
        self.assertEqual(client.servers, custom_servers)

    @patch('utils.ntp_client.socket')
    def test_get_time_success(self, mock_socket):
        """测试成功获取 NTP 时间"""
        # Mock socket
        mock_sock = MagicMock()
        mock_socket.socket.return_value = mock_sock
        mock_socket.gethostbyname.return_value = "1.2.3.4"
        
        # Mock NTP response (48 bytes)
        mock_response = bytes(48)
        mock_sock.recvfrom.return_value = (mock_response, ("1.2.3.4", 123))

        client = NTPClient()
        result = client.get_time("pool.ntp.org")

        self.assertIsInstance(result, NTPResult)
        mock_sock.sendto.assert_called_once()

    @patch('utils.ntp_client.socket')
    def test_get_time_dns_failure(self, mock_socket):
        """测试 DNS 解析失败"""
        mock_socket.gethostbyname.side_effect = socket.gaierror("DNS 解析失败")
        mock_socket.inet_aton.side_effect = socket.error("Invalid IP")

        client = NTPClient()
        result = client.get_time("invalid.server")

        self.assertFalse(result.success)
        self.assertIn("DNS", result.error)

    @patch('utils.ntp_client.socket')
    def test_get_time_timeout(self, mock_socket):
        """测试 NTP 请求超时"""
        mock_socket.gethostbyname.return_value = "1.2.3.4"
        mock_sock = MagicMock()
        mock_socket.socket.return_value = mock_sock
        mock_sock.sendto.side_effect = socket.timeout("超时")

        client = NTPClient()
        result = client.get_time("pool.ntp.org")

        self.assertFalse(result.success)
        self.assertIn("超时", result.error)


class TestNTPSyncManager(unittest.TestCase):
    """测试 NTPSyncManager 类"""

    @patch('utils.ntp_client.NTPClient')
    def test_init(self, mock_ntp_client):
        """测试初始化"""
        manager = NTPSyncManager(history_file="/tmp/test_ntp.json")
        self.assertIsNotNone(manager.client)
        self.assertEqual(manager.history_file, "/tmp/test_ntp.json")
        self.assertFalse(manager.auto_sync_enabled)

    @patch('utils.ntp_client.NTPClient')
    @patch('utils.ntp_client.os.path.exists')
    def test_load_history(self, mock_exists, mock_ntp_client):
        """测试加载历史"""
        mock_exists.return_value = False
        manager = NTPSyncManager()
        manager.load_history()
        self.assertEqual(manager.history, [])

    @patch('utils.ntp_client.NTPClient')
    def test_sync_now_success(self, mock_ntp_client):
        """测试立即同步成功"""
        # Mock NTP client
        mock_client = MagicMock()
        mock_ntp_client.return_value = mock_client
        mock_client.get_best_time.return_value = NTPResult(
            success=True,
            ntp_time=datetime.datetime.now(),
            offset=0.1,
            delay=0.02,
            server="pool.ntp.org"
        )

        manager = NTPSyncManager()
        result = manager.sync_now()

        self.assertTrue(result.success)
        self.assertIsNotNone(manager.last_sync_result)
        self.assertIsNotNone(manager.last_sync_time)

    @patch('utils.ntp_client.NTPClient')
    def test_check_time_drift(self, mock_ntp_client):
        """测试时间偏差检查"""
        mock_client = MagicMock()
        mock_ntp_client.return_value = mock_client
        
        # 偏差小于阈值
        mock_client.get_best_time.return_value = NTPResult(
            success=True,
            offset=0.5,  # < 1.0 阈值
            server="pool.ntp.org"
        )

        manager = NTPSyncManager()
        needs_adjust, offset = manager.check_time_drift()
        self.assertFalse(needs_adjust)
        self.assertEqual(offset, 0.5)

        # 偏差大于阈值
        mock_client.get_best_time.return_value = NTPResult(
            success=True,
            offset=2.5,  # > 1.0 阈值
            server="pool.ntp.org"
        )
        needs_adjust, offset = manager.check_time_drift()
        self.assertTrue(needs_adjust)
        self.assertEqual(offset, 2.5)

    @patch('utils.ntp_client.NTPClient')
    def test_get_sync_status(self, mock_ntp_client):
        """测试获取同步状态"""
        manager = NTPSyncManager()
        status = manager.get_sync_status()
        
        self.assertIn('auto_sync_enabled', status)
        self.assertIn('auto_sync_interval', status)
        self.assertIn('total_sync_count', status)
        self.assertFalse(status['auto_sync_enabled'])
        self.assertEqual(status['auto_sync_interval'], 24)


class TestNTPHelperFunctions(unittest.TestCase):
    """测试 NTP 工具函数"""

    @patch('utils.ntp_client.NTPClient')
    def test_get_ntp_time_success(self, mock_ntp_client):
        """测试获取 NTP 时间工具函数"""
        mock_client = MagicMock()
        mock_ntp_client.return_value = mock_client
        mock_client.get_time.return_value = NTPResult(
            success=True,
            ntp_time=datetime.datetime(2026, 3, 24, 12, 0, 0),
            server="pool.ntp.org"
        )

        from utils.ntp_client import get_ntp_time
        ntp_time = get_ntp_time()
        
        self.assertIsNotNone(ntp_time)
        self.assertEqual(ntp_time.year, 2026)

    @patch('utils.ntp_client.NTPSyncManager')
    def test_check_time_accuracy_accurate(self, mock_manager):
        """测试时间准确性检查 - 准确"""
        mock_mgr = MagicMock()
        mock_manager.return_value = mock_mgr
        mock_mgr.sync_now.return_value = NTPResult(
            success=True,
            offset=0.0005,  # < 0.001 精确
            server="pool.ntp.org"
        )

        from utils.ntp_client import check_time_accuracy
        is_accurate, offset = check_time_accuracy()
        
        self.assertTrue(is_accurate)
        self.assertEqual(offset, 0.0005)

    @patch('utils.ntp_client.NTPSyncManager')
    def test_check_time_accuracy_drift(self, mock_manager):
        """测试时间准确性检查 - 有偏差"""
        mock_mgr = MagicMock()
        mock_manager.return_value = mock_mgr
        mock_mgr.sync_now.return_value = NTPResult(
            success=True,
            offset=1.5,  # > 1.0 需要调整
            server="pool.ntp.org"
        )

        from utils.ntp_client import check_time_accuracy
        is_accurate, offset = check_time_accuracy()
        
        self.assertFalse(is_accurate)
        self.assertEqual(offset, 1.5)


class TestNTPIntegration(unittest.TestCase):
    """NTP 集成测试"""

    @patch('utils.ntp_client.NTPClient')
    def test_full_sync_workflow(self, mock_ntp_client):
        """测试完整同步工作流程"""
        # Mock NTP client
        mock_client = MagicMock()
        mock_ntp_client.return_value = mock_client
        mock_client.get_best_time.return_value = NTPResult(
            success=True,
            ntp_time=datetime.datetime.now(),
            offset=0.2,
            delay=0.025,
            server="ntp.aliyun.com"
        )

        # 创建管理器
        manager = NTPSyncManager(history_file="/tmp/test_ntp_full.json")
        
        # 执行同步
        result = manager.sync_now()
        self.assertTrue(result.success)
        
        # 检查状态
        status = manager.get_sync_status()
        self.assertEqual(status['total_sync_count'], 1)
        self.assertIsNotNone(status['last_sync_time'])
        
        # 检查历史
        history = manager.get_history()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0].server, "ntp.aliyun.com")
        self.assertAlmostEqual(history[0].offset, 0.2, places=2)


if __name__ == '__main__':
    unittest.main()
