# qBittorrent API 客户端

这是一个专门封装 qBittorrent Web API 的 Python 客户端类，提供了简洁易用的接口来管理 qBittorrent。

## 功能特性

- 🔐 自动登录管理
- 📁 种子添加（URL 和文件两种方式）
- 💾 磁盘空间查询
- 📊 种子信息获取和管理
- ⏸️ 种子暂停/恢复
- 🗑️ 种子删除
- 📈 实时状态监控
- 🛡️ 完善的错误处理
- 📝 详细的日志记录

## 安装依赖

```bash
pip install requests
```

## 基本使用

### 1. 环境变量配置（推荐）

设置以下环境变量：

```bash
export QBURL="http://192.168.66.10:10000"
export QBUSER="admin"
export QBPWD="adminadmin"
```

### 2. 基本使用示例

```python
from qbittorrent_client import QBittorrentClient

# 使用环境变量配置
with QBittorrentClient() as qb:
    if not qb.login():
        print("登录失败")
        exit(1)
    
    # 获取磁盘空间
    disk_space = qb.get_disk_space()
    if disk_space:
        print(f"磁盘剩余空间: {disk_space / 1024 / 1024 / 1024:.2f} GB")
    
    # 添加种子
    success = qb.add_torrent_by_url(
        url="https://example.com/torrent.torrent",
        save_path="/download/PT刷流",
        tags="MT刷流"
    )
```

## API 方法详解

### 认证相关

- `login() -> bool`: 登录到 qBittorrent Web UI
- `logout()`: 登出并清理会话
- `is_logged_in() -> bool`: 检查是否已登录

### 系统信息

- `get_disk_space() -> Optional[int]`: 获取磁盘剩余空间（字节）
- `get_sync_maindata() -> Optional[Dict]`: 获取同步数据

### 种子管理

- `add_torrent_by_url(url, save_path, tags) -> bool`: 通过 URL 添加种子
- `add_torrent_by_file(content, filename, save_path, tags) -> bool`: 通过文件添加种子
- `get_torrents() -> Optional[List[Dict]]`: 获取所有种子信息
- `pause_torrent(hash) -> bool`: 暂停种子
- `resume_torrent(hash) -> bool`: 恢复种子
- `delete_torrent(hash, delete_files) -> bool`: 删除种子

## 注意事项

1. 大部分操作都需要先登录
2. 建议使用 `with` 语句自动管理会话
3. 所有方法都包含完善的错误处理
4. 包含完整的类型提示 