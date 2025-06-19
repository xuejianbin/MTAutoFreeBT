# MTAutoFreeBT Web管理界面

## 概述

MTAutoFreeBT Web管理界面提供了一个现代化的Web界面来管理和监控自动种子下载系统。通过Web界面，您可以：

- 查看系统运行状态和统计数据
- 管理下载策略配置
- 查看种子下载历史
- 监控系统日志
- 配置系统参数

## 功能特性

### 📊 仪表板
- 实时显示系统运行状态
- 统计图表展示下载趋势
- 策略使用情况分析
- 一键启动/停止系统

### 📋 种子管理
- 查看所有种子记录
- 按条件筛选种子
- 查看种子详细信息
- 导出种子数据

### ⚙️ 策略管理
- 创建和编辑下载策略
- 设置当前使用的策略
- 策略配置可视化
- 策略效果分析

### 📝 系统日志
- 实时查看系统日志
- 按级别筛选日志
- 日志搜索功能
- 日志导出功能

### 🔧 系统设置
- 配置基本参数
- QBittorrent连接设置
- 通知服务配置
- 系统信息查看

## 安装和运行

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

创建 `.env` 文件并配置以下参数：

```env
# Web应用配置
WEB_HOST=0.0.0.0
WEB_PORT=5000
WEB_DEBUG=False
SECRET_KEY=your-secret-key-here

# QBittorrent配置
QB_HOST=http://localhost:8080
QB_USERNAME=admin
QB_PASSWORD=adminadmin

# 策略配置
STRATEGY_CONFIG_FILE=strategies/config_example.json

# 其他配置（可选）
APIKEY=your-mt-api-key
DOWNLOADPATH=/download/PT刷流
BOT_TOKEN=your-telegram-bot-token
CHAT_ID=your-chat-id
```

### 3. 启动Web应用

```bash
# 方式1：直接运行
python start_web.py

# 方式2：使用Flask开发服务器
python web_app.py

# 方式3：使用生产服务器（推荐）
gunicorn -w 4 -b 0.0.0.0:5000 web_app:app
```

### 4. 访问Web界面

打开浏览器访问：`http://localhost:5000`

## 数据库

Web应用使用SQLite数据库存储数据，数据库文件位于：`mt_auto_freebt.db`

### 数据表结构

#### TorrentRecord（种子记录表）
- `id`: 主键
- `torrent_id`: 种子ID
- `name`: 种子名称
- `size`: 文件大小
- `discount`: 折扣信息
- `discount_end_time`: 折扣结束时间
- `seeders`: 做种数
- `leechers`: 下载数
- `download_decision`: 下载决策
- `strategy_used`: 使用的策略
- `priority_score`: 优先级分数
- `created_at`: 创建时间

#### SystemLog（系统日志表）
- `id`: 主键
- `level`: 日志级别
- `message`: 日志消息
- `created_at`: 创建时间

#### StrategyConfig（策略配置表）
- `id`: 主键
- `name`: 策略名称
- `config_data`: 配置数据（JSON）
- `is_active`: 是否激活
- `created_at`: 创建时间
- `updated_at`: 更新时间

## API接口

### 统计接口
- `GET /api/stats` - 获取统计数据

### 种子接口
- `GET /api/torrents` - 获取种子列表
- `GET /api/torrents/export` - 导出种子数据

### 策略接口
- `GET /api/strategies` - 获取策略列表
- `PUT /api/strategies/<name>` - 更新策略

### 系统接口
- `POST /api/system/start` - 启动系统
- `POST /api/system/stop` - 停止系统

### 日志接口
- `GET /api/logs` - 获取系统日志
- `GET /api/logs/export` - 导出日志

## 使用说明

### 1. 首次使用

1. 启动Web应用
2. 访问Web界面
3. 在"系统设置"中配置QBittorrent连接
4. 在"策略管理"中创建或选择下载策略
5. 在"仪表板"中启动系统

### 2. 策略配置

策略配置支持以下类型：

#### 大小策略
- 设置文件大小范围
- 配置磁盘空间要求

#### 比率策略
- 设置做种数要求
- 配置比率范围
- 偏好高做种数选项

#### 时间策略
- 设置发布时间限制
- 配置免费时间要求
- 时间衰减因子

#### 复合策略
- 组合多个基础策略
- 支持AND/OR/加权平均组合

### 3. 监控和维护

- 定期查看仪表板了解系统状态
- 通过日志页面排查问题
- 根据统计数据调整策略配置
- 定期备份数据库文件

## 故障排除

### 常见问题

1. **Web界面无法访问**
   - 检查端口是否被占用
   - 确认防火墙设置
   - 查看应用日志

2. **数据库错误**
   - 检查数据库文件权限
   - 确认磁盘空间充足
   - 尝试重新初始化数据库

3. **策略不生效**
   - 检查策略配置是否正确
   - 确认策略已设为当前策略
   - 查看系统日志了解执行情况

4. **QBittorrent连接失败**
   - 检查QBittorrent是否运行
   - 确认Web UI地址和端口
   - 验证用户名和密码

### 日志查看

应用日志文件位置：
- Web应用日志：`logs/web_app.log`
- 系统运行日志：通过Web界面查看

## 开发说明

### 项目结构
```
app/
├── web_app.py          # Web应用主文件
├── start_web.py        # 启动脚本
├── templates/          # HTML模板
│   ├── base.html       # 基础模板
│   ├── dashboard.html  # 仪表板
│   ├── torrents.html   # 种子列表
│   ├── strategies.html # 策略管理
│   ├── logs.html       # 系统日志
│   └── settings.html   # 系统设置
├── static/             # 静态文件
└── requirements.txt    # 依赖列表
```

### 扩展开发

如需添加新功能：

1. 在 `web_app.py` 中添加新的路由
2. 创建对应的HTML模板
3. 添加必要的API接口
4. 更新数据库模型（如需要）

## 许可证

本项目采用MIT许可证，详见LICENSE文件。 