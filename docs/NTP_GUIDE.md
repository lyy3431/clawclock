# 🌐 NTP 网络时间同步使用指南

ClawClock v1.7.0+ 内置了 NTP（Network Time Protocol）网络时间同步功能，可以自动校准本地时间，确保时钟显示的精确性。

---

## 📋 目录

- [功能介绍](#功能介绍)
- [快速开始](#快速开始)
- [配置选项](#配置选项)
- [使用方法](#使用方法)
- [状态说明](#状态说明)
- [常见问题](#常见问题)
- [技术细节](#技术细节)

---

## 功能介绍

### 为什么需要 NTP 同步？

- **系统时间可能不准确**：电脑的系统时间可能会有几秒甚至几分钟的偏差
- **自动校准**：NTP 可以从权威时间服务器获取精确时间
- **无需手动调整**：启用后自动定期同步，无需手动校准

### 核心特性

- ✅ **自动同步**：支持定时自动同步（默认每 24 小时）
- ✅ **多服务器支持**：内置全球和中国 NTP 服务器池
- ✅ **智能选择**：自动选择延迟最低的服务器
- ✅ **状态显示**：实时显示时间偏差状态
- ✅ **历史记录**：保存最近 100 次同步记录
- ✅ **后台运行**：同步在后台进行，不影响使用

---

## 快速开始

### 1. 启用 NTP 同步

打开 ClawClock，在界面右下角可以看到 NTP 状态标签：

```
NTP: 未同步
```

### 2. 首次同步

应用启动时会自动执行一次 NTP 同步（如果配置中启用了 NTP）。

### 3. 查看状态

同步完成后，状态标签会显示时间偏差：

```
NTP: ✓ 精确同步        (绿色，偏差 < 1ms)
NTP: ✓ 偏差 +0.050 秒   (绿色，偏差 < 100ms)
NTP: ⚠ 偏差 +1.500 秒   (橙色，偏差 > 1s)
NTP: ✗ 偏差 +5.000 秒   (红色，偏差 > 5s)
```

---

## 配置选项

在 `config.json` 中添加或修改 `ntp` 配置：

```json
{
  "ntp": {
    "enabled": true,              // 是否启用 NTP 同步
    "auto_sync": true,            // 是否自动同步
    "sync_interval_hours": 24,    // 自动同步间隔（小时）
    "server": "auto",             // NTP 服务器（auto=自动选择）
    "show_status": true           // 是否显示状态标签
  }
}
```

### 配置说明

| 选项 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `enabled` | boolean | false | 是否启用 NTP 同步功能 |
| `auto_sync` | boolean | false | 是否启用自动同步 |
| `sync_interval_hours` | integer | 24 | 自动同步间隔（小时） |
| `server` | string | "auto" | NTP 服务器地址，"auto" 表示自动选择 |
| `show_status` | boolean | true | 是否在 UI 显示状态标签 |

### 可用 NTP 服务器

**全球服务器池：**
- `pool.ntp.org` - 全球 NTP 服务器池（默认）
- `time.google.com` - Google 时间服务器
- `time.cloudflare.com` - Cloudflare 时间服务器
- `time.apple.com` - Apple 时间服务器

**中国服务器：**
- `cn.pool.ntp.org` - 中国 NTP 服务器池
- `ntp.aliyun.com` - 阿里云时间服务器（推荐）
- `ntp.tencent.com` - 腾讯云时间服务器

---

## 使用方法

### 手动同步（开发/调试）

在 Python 环境中：

```python
from utils.ntp_client import NTPSyncManager

# 创建管理器
manager = NTPSyncManager()

# 执行同步
result = manager.sync_now()

if result.success:
    print(f"同步成功！偏差：{result.offset:+.3f}秒")
    print(f"服务器：{result.server}")
    print(f"延迟：{result.delay*1000:.1f}ms")
else:
    print(f"同步失败：{result.error}")
```

### 检查时间偏差

```python
from utils.ntp_client import check_time_accuracy

is_accurate, offset = check_time_accuracy()

if is_accurate:
    print("时间准确")
else:
    print(f"时间偏差：{offset:+.3f}秒")
```

### 启用自动同步

```python
manager = NTPSyncManager()
manager.enable_auto_sync(interval_hours=12)  # 每 12 小时同步一次
```

---

## 状态说明

### 状态标签颜色

| 颜色 | 状态 | 说明 |
|------|------|------|
| 🟢 绿色 | ✓ 精确同步 | 偏差 < 1ms，时间非常准确 |
| 🟢 绿色 | ✓ 偏差 ±X.XXX 秒 | 偏差 < 100ms，时间准确 |
| 🟠 橙色 | ⚠ 偏差 ±X.XXX 秒 | 偏差 100ms-1s，建议同步 |
| 🔴 红色 | ✗ 偏差 ±X.XXX 秒 | 偏差 > 1s，需要立即同步 |
| ⚪ 灰色 | 未同步 | 尚未执行同步 |
| ⚪ 灰色 | 不可用 | NTP 模块不可用 |

### 同步历史

同步历史记录保存在 `ntp_history.json` 文件中，包含：

```json
{
  "history": [
    {
      "timestamp": "2026-03-24T12:30:45.123456",
      "server": "ntp.aliyun.com",
      "offset": 0.052,
      "adjusted": false
    }
  ],
  "auto_sync_enabled": true,
  "auto_sync_interval": 24
}
```

---

## 常见问题

### Q1: NTP 同步失败怎么办？

**可能原因：**
1. 网络连接问题
2. 防火墙阻止 NTP 端口（UDP 123）
3. NTP 服务器不可用

**解决方法：**
1. 检查网络连接
2. 更换 NTP 服务器（如 `ntp.aliyun.com`）
3. 检查防火墙设置

### Q2: 自动同步会影响性能吗？

不会。NTP 同步在后台线程执行，不会阻塞 UI。每次同步仅需几毫秒网络通信。

### Q3: 为什么时间还有偏差？

NTP 同步后，如果系统时间仍有偏差，可能是因为：
1. 系统硬件时钟电池老化
2. 操作系统时间同步服务冲突（如 Windows Time、systemd-timesyncd）
3. 虚拟机时间同步问题

**建议：** 缩短自动同步间隔（如 6 小时）

### Q4: 可以完全依赖 NTP 同步吗？

可以，但建议：
- 启用自动同步（每 24 小时）
- 定期检查同步状态
- 如果偏差持续较大，检查系统时间设置

### Q5: NTP 同步会修改系统时间吗？

**不会。** ClawClock 的 NTP 功能仅用于：
- 显示时间偏差
- 提醒用户时间不准确
- 为应用内部时间计算提供参考

如需修改系统时间，需要管理员权限并使用系统工具。

---

## 技术细节

### NTP 协议原理

NTP（Network Time Protocol）是一种用于同步计算机时间的协议。工作原理：

1. **客户端发送请求**：记录发送时间 T1
2. **服务器接收请求**：记录接收时间 T2
3. **服务器发送响应**：包含 T2 和发送时间 T3
4. **客户端接收响应**：记录接收时间 T4

**计算公式：**
- 网络延迟 = (T4 - T1) - (T3 - T2)
- 时间偏差 = [(T2 - T1) + (T3 - T4)] / 2

### 精度保证

- **时间戳精度**：使用 64 位 NTP 时间戳（32 位秒 + 32 位小数）
- **网络延迟补偿**：自动计算并补偿网络延迟
- **多次测量**：自动选择延迟最低的服务器
- **本地时区处理**：所有计算使用 UTC，显示时转换为本地时间

### 安全考虑

- **只读操作**：NTP 同步仅读取时间，不修改系统设置
- **无认证需求**：使用公开 NTP 服务器，无需认证
- **加密连接**：未来版本计划支持 NTS（NTP over TLS）

---

## 更新日志

- **v1.7.0** (2026-03-24) - 初始版本
  - ✅ NTP 客户端实现
  - ✅ 自动同步功能
  - ✅ UI 状态显示
  - ✅ 16 个单元测试

---

**最后更新**: 2026-03-24  
**适用版本**: ClawClock v1.7.0+
