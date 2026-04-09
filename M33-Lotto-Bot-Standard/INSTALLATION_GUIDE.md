# M33 Lotto Bot Standard 安装指南

## 📋 系统要求

### 服务器要求
- **操作系统**: Ubuntu 20.04+ / Debian 10+ / CentOS 8+
- **内存**: 至少 2GB RAM
- **存储**: 至少 10GB 可用空间
- **Python**: 3.8+
- **Supervisor**: 进程管理工具

### 软件依赖
- Python 3.8+
- SQLite3
- Git
- Supervisor
- pip3 (Python包管理)

## 🚀 完整安装步骤

### 步骤1: 服务器准备

```bash
# 更新系统
sudo apt update
sudo apt upgrade -y

# 安装基础软件
sudo apt install -y python3 python3-pip python3-venv git sqlite3 supervisor

# 创建系统用户
sudo useradd -m -s /bin/bash www-data
```

### 步骤2: 部署M33 Lotto Bot Standard

```bash
# 切换到安装目录
cd /opt

# 克隆M33 Lotto Bot Standard系统
sudo git clone <你的仓库地址> M33-Lotto-Bot-Standard

# 设置权限
sudo chown -R www-data:www-data M33-Lotto-Bot-Standard
sudo chmod 755 M33-Lotto-Bot-Standard

# 进入目录
cd M33-Lotto-Bot-Standard
```

### 步骤3: 运行安装脚本

```bash
# 运行安装脚本
sudo bash scripts/setup.sh
```

安装脚本会自动：
- 创建10个客户配置模板
- 设置Supervisor进程配置
- 创建必要的目录结构
- 设置文件权限

### 步骤4: 部署M33 Bot源代码

```bash
# 假设你的M33 Bot代码在 /path/to/m33-bot
sudo cp -r /path/to/m33-bot/src /opt/M33-Lotto-Bot-Standard/

# 设置权限
sudo chown -R www-data:www-data /opt/M33-Lotto-Bot-Standard/src
```

### 步骤5: 安装Python依赖

```bash
# 进入源代码目录
cd /opt/M33-Lotto-Bot-Standard/src

# 安装依赖（根据你的requirements.txt）
sudo pip3 install -r requirements.txt

# 安装额外依赖
sudo pip3 install python-telegram-bot python-dotenv httpx beautifulsoup4
```

## 🔧 配置M33 Bot支持多租户

### 修改 main.py 支持配置参数

按照 `scripts/MODIFY_MAIN_PY.md` 的指南修改 `src/app/main.py`：

1. 添加配置加载函数
2. 添加命令行参数解析
3. 修改Bot Token引用
4. 修改数据库连接

### 验证修改

```bash
# 测试配置加载
cd /opt/M33-Lotto-Bot-Standard
python scripts/config_loader.py --config-dir configs/client_01 --check

# 测试启动（应该会失败，因为还没有Token）
python src/app/main.py --config-dir configs/client_01
```

## 👥 添加第一个客户

### 步骤1: 创建Telegram Bot

1. 在Telegram中联系 [@BotFather](https://t.me/BotFather)
2. 发送 `/newbot`
3. 设置Bot名称（如: `客户A彩票机器人`）
4. 设置用户名（如: `ClientA_LottoBot`）
5. 复制生成的Token（格式: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`）

### 步骤2: 激活客户

```bash
cd /opt/M33-Lotto-Bot-Standard

# 激活客户01
python scripts/activate.py 01 你的BotToken
```

### 步骤3: 启动服务

```bash
# 启动客户01
python scripts/manage.py start 01

# 查看状态
python scripts/manage.py status 01

# 查看日志
tail -f /var/log/m33-standard/client_01/stdout.log
```

### 步骤4: 测试Bot

1. 在Telegram中搜索你的Bot用户名
2. 发送 `/start`
3. 测试基本功能

## 📊 日常管理

### 查看所有客户状态
```bash
python scripts/manage.py status-all
```

### 启动所有已激活客户
```bash
python scripts/manage.py start-all
```

### 停止所有客户
```bash
python scripts/manage.py stop-all
```

### 重启单个客户
```bash
python scripts/manage.py restart 01
```

### 添加新客户
```bash
# 创建新Bot，获取Token
# 激活新客户（假设用02号席位）
python scripts/activate.py 02 新Token

# 启动新客户
python scripts/manage.py start 02
```

## 💾 备份与恢复

### 手动备份
```bash
cd /opt/M33-Lotto-Bot-Standard
bash scripts/backup.sh
```

### 自动备份（cron job）
```bash
# 编辑cron
sudo crontab -e

# 添加每天凌晨3点备份
0 3 * * * cd /opt/M33-Lotto-Bot-Standard && bash scripts/backup.sh >> /var/log/m33-backup.log 2>&1
```

### 恢复备份
参考 `backups/RESTORE_GUIDE.md`

## 🔍 故障排除

### 常见问题1: Bot无法启动
```bash
# 检查Token是否正确
cat configs/client_01/.env | grep BOT_TOKEN

# 检查Supervisor状态
sudo supervisorctl status m33-standard-client-01

# 查看错误日志
tail -f /var/log/m33-standard/client_01/stderr.log
```

### 常见问题2: 数据库错误
```bash
# 检查数据库文件权限
ls -la data/client_01.db

# 修复权限
sudo chown www-data:www-data data/client_01.db
sudo chmod 644 data/client_01.db
```

### 常见问题3: Python依赖问题
```bash
# 重新安装依赖
cd src
sudo pip3 install -r requirements.txt --upgrade
```

### 常见问题4: Supervisor问题
```bash
# 重新加载配置
sudo supervisorctl reread
sudo supervisorctl update

# 重启Supervisor服务
sudo systemctl restart supervisor
```

## 📈 监控与维护

### 监控磁盘空间
```bash
# 查看数据库大小
du -sh data/*.db

# 查看日志大小
du -sh /var/log/m33-standard/
```

### 清理旧日志
```bash
# 清理30天前的日志
find /var/log/m33-standard -name "*.log" -mtime +30 -delete
```

### 监控进程状态
```bash
# 实时监控
watch -n 5 'python scripts/manage.py status-all'
```

## 🔄 系统更新

### 更新M33 Bot代码
```bash
# 备份当前状态
python scripts/manage.py stop-all
bash scripts/backup.sh

# 更新代码
cd /opt/M33-Lotto-Bot-Standard/src
git pull

# 重新启动
cd ..
python scripts/manage.py start-all
```

### 更新M33 Lotto Bot Standard系统
```bash
# 备份
bash scripts/backup.sh

# 更新系统
cd /opt/M33-Lotto-Bot-Standard
git pull

# 重新运行安装脚本
sudo bash scripts/setup.sh

# 重启所有客户
python scripts/manage.py restart-all
```

## 🎯 最佳实践

### 安全建议
1. **定期更换Bot Token**：每3-6个月更换一次
2. **限制数据库访问**：只允许www-data用户访问
3. **启用防火墙**：只开放必要端口
4. **定期备份**：每天自动备份
5. **监控日志**：定期检查错误日志

### 性能优化
1. **数据库优化**：定期清理旧数据
2. **日志轮转**：配置logrotate
3. **内存监控**：监控Python进程内存使用
4. **连接池**：优化数据库连接

### 客户管理
1. **文档记录**：记录每个客户的配置信息
2. **定期检查**：每月检查所有客户运行状态
3. **客户沟通**：建立清晰的沟通渠道
4. **服务协议**：明确服务范围和责任

## 📞 技术支持

### 获取帮助
1. 查看日志文件
2. 使用 `manage.py info` 查看系统信息
3. 检查Supervisor状态

### 紧急恢复
```bash
# 停止所有服务
python scripts/manage.py stop-all

# 从最新备份恢复
bash scripts/backup.sh  # 先备份当前状态
# 然后按照 RESTORE_GUIDE.md 恢复

# 重新启动
python scripts/manage.py start-all
```

### 联系支持
- 问题反馈: <你的联系方式>
- 紧急问题: <紧急联系方式>
- 文档更新: <文档仓库>

## 🎉 完成！

现在你的 M33 Lotto Bot Standard 系统已经安装完成，可以开始为客户提供服务了！

### 下一步
1. 测试所有客户功能
2. 设置自动备份
3. 建立监控告警
4. 制定客户上线流程

祝你的业务顺利！ 🚀