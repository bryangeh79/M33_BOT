# M33 Lotto Bot Standard
## 标准版多租户部署系统

### 📦 系统特性
- **10客户预配置席位**：开箱即用
- **一键激活**：只需填写Bot Token
- **智能管理**：批量/个别操作支持
- **完全隔离**：每个客户独立数据库、进程、日志
- **统一维护**：代码更新一次，所有客户生效

### 🚀 快速开始

#### 1. 系统安装
```bash
# 克隆项目
cd /opt
git clone <your-repo> M33-Lotto-Bot-Standard
cd M33-Lotto-Bot-Standard

# 运行安装脚本
bash scripts/setup.sh
```

#### 2. 激活第一个客户
```bash
# 步骤1：创建Bot（联系 @BotFather）
# 获取Token格式：1234567890:ABCdefGHIjklMNOpqrsTUVwxyz

# 步骤2：激活客户（只需Token）
python scripts/activate.py 01 1234567890:ABCdef...

# 步骤3：启动服务
python scripts/manage.py start 01

# 步骤4：验证运行
python scripts/manage.py status 01
```

### 📊 客户管理

#### 激活新客户
```bash
# 只需这一条命令
python scripts/activate.py <编号> <Token>

# 示例：激活客户02
python scripts/activate.py 02 9876543210:ZYXwvuts...
```

#### 启动/停止服务
```bash
# 启动单个客户
python scripts/manage.py start 01

# 启动多个客户
python scripts/manage.py start 01 02 03

# 启动所有已激活客户
python scripts/manage.py start-all

# 停止单个客户
python scripts/manage.py stop 01

# 停止所有客户
python scripts/manage.py stop-all

# 重启客户
python scripts/manage.py restart 01

# 查看状态
python scripts/manage.py status-all
```

### 📁 目录结构
```
M33-Lotto-Bot-Standard/
├── configs/                    # 客户配置
│   ├── client_01/             # 客户01配置
│   ├── client_02/             # 客户02配置
│   ├── ...                    # 客户03-09
│   └── client_10/             # 客户10配置
├── data/                      # 数据库文件
│   ├── client_01.db           # 客户01数据库
│   ├── client_02.db           # 客户02数据库
│   └── ...
├── supervisor/                # 进程管理配置
├── scripts/                   # 管理脚本
│   ├── setup.sh              # 安装脚本
│   ├── activate.py           # 激活脚本
│   └── manage.py             # 管理脚本
├── src/                      # M33 Bot源代码
└── logs/                     # 系统日志（自动创建）
```

### 🔧 维护命令

#### 代码更新
```bash
# 更新所有客户代码
cd /opt/M33-Lotto-Bot-Standard
git pull
python scripts/manage.py restart-all
```

#### 日志查看
```bash
# 查看客户01日志
tail -f /var/log/m33-standard/client_01/stdout.log

# 查看错误日志
tail -f /var/log/m33-standard/client_01/stderr.log
```

#### 备份数据库
```bash
# 备份所有客户数据库
bash scripts/backup.sh
```

### 💰 计费建议
- **标准版**：$50/月/客户
- **设置费**：$100（一次性）
- **客户上限**：10个/服务器（可扩展）

### ⚠️ 注意事项
1. 每个客户需要独立的Telegram Bot Token
2. 建议定期备份 `/opt/M33-Lotto-Bot-Standard/data/` 目录
3. 监控服务器资源使用情况
4. 保持系统更新以获得最新功能和安全修复

### 📞 技术支持
- 系统问题：检查日志文件
- 客户问题：通过Telegram群处理
- 紧急重启：`python scripts/manage.py restart-all`

---
**版本**: 1.0.0  
**最后更新**: 2026-04-07  
**作者**: M33 Bot Team