# M33 Lotto Bot Standard - 快速开始

## 🎯 5分钟快速部署

### 步骤1: 安装系统
```bash
# 1. 下载系统
cd /opt
sudo git clone <你的仓库> M33-Lotto-Bot-Standard
cd M33-Lotto-Bot-Standard

# 2. 运行安装脚本
sudo bash scripts/setup.sh
```

### 步骤2: 部署M33 Bot代码
```bash
# 复制你的M33 Bot源代码
sudo cp -r /path/to/your/m33-bot/src /opt/M33-Lotto-Bot-Standard/

# 安装Python依赖
cd /opt/M33-Lotto-Bot-Standard/src
sudo pip3 install python-telegram-bot python-dotenv httpx beautifulsoup4
```

### 步骤3: 修改main.py支持多租户
按照 `scripts/MODIFY_MAIN_PY.md` 指南修改 `src/app/main.py`。

### 步骤4: 添加第一个客户
```bash
cd /opt/M33-Lotto-Bot-Standard

# 1. 创建Telegram Bot（联系 @BotFather）
# 2. 获取Token（格式: 1234567890:ABCdef...）

# 3. 激活客户01
python scripts/activate.py 01 YOUR_BOT_TOKEN

# 4. 启动服务
python scripts/manage.py start 01

# 5. 验证运行
python scripts/manage.py status 01
```

### 步骤5: 测试Bot
1. 在Telegram中搜索你的Bot
2. 发送 `/start`
3. 测试功能

## 📋 常用命令速查

### 客户管理
```bash
# 激活新客户
python scripts/activate.py <编号> <Token>

# 启动客户
python scripts/manage.py start <编号>

# 停止客户
python scripts/manage.py stop <编号>

# 重启客户
python scripts/manage.py restart <编号>

# 查看状态
python scripts/manage.py status <编号>
```

### 批量操作
```bash
# 启动所有已激活客户
python scripts/manage.py start-all

# 停止所有客户
python scripts/manage.py stop-all

# 重启所有已激活客户
python scripts/manage.py restart-all

# 查看所有状态
python scripts/manage.py status-all
```

### 系统管理
```bash
# 备份所有数据
bash scripts/backup.sh

# 查看系统信息
python scripts/manage.py info

# 检查配置
python scripts/config_loader.py --config-dir configs/client_01 --check
```

## 🔧 故障快速修复

### Bot无法启动？
```bash
# 1. 检查Token
cat configs/client_01/.env | grep BOT_TOKEN

# 2. 检查Supervisor状态
sudo supervisorctl status m33-standard-client-01

# 3. 查看错误日志
tail -f /var/log/m33-standard/client_01/stderr.log
```

### 数据库错误？
```bash
# 修复权限
sudo chown www-data:www-data data/client_01.db
sudo chmod 644 data/client_01.db
```

### 所有客户都挂了？
```bash
# 重启Supervisor
sudo systemctl restart supervisor

# 重新启动所有客户
python scripts/manage.py start-all
```

## 🚀 扩展客户

### 添加第二个客户
```bash
# 1. 创建新Bot（@BotFather）
# 2. 获取新Token

# 3. 激活客户02
python scripts/activate.py 02 NEW_TOKEN

# 4. 启动
python scripts/manage.py start 02
```

### 添加更多客户（03-10）
重复上述步骤，只需更改编号。

## 💾 备份策略

### 每日自动备份
```bash
# 编辑cron
sudo crontab -e

# 添加（每天凌晨3点备份）
0 3 * * * cd /opt/M33-Lotto-Bot-Standard && bash scripts/backup.sh >> /var/log/m33-backup.log 2>&1
```

### 手动备份
```bash
cd /opt/M33-Lotto-Bot-Standard
bash scripts/backup.sh
```

## 📞 紧急情况

### 快速恢复所有服务
```bash
# 1. 停止所有
python scripts/manage.py stop-all

# 2. 从备份恢复（如果需要）
# 参考 backups/RESTORE_GUIDE.md

# 3. 重新启动
python scripts/manage.py start-all
```

### 重置单个客户
```bash
# 1. 停止客户
python scripts/manage.py stop 01

# 2. 删除数据库（谨慎！）
sudo rm data/client_01.db
touch data/client_01.db
sudo chown www-data:www-data data/client_01.db

# 3. 重新启动
python scripts/manage.py start 01
```

## 🎉 恭喜！

你的 M33 Lotto Bot Standard 系统已经运行起来了！

### 下一步建议
1. ✅ 测试所有客户功能
2. ⏰ 设置自动备份
3. 👁️ 建立简单监控
4. 📈 开始服务客户

### 需要帮助？
- 查看详细文档：`README.md`
- 安装指南：`INSTALLATION_GUIDE.md`
- 修改指南：`scripts/MODIFY_MAIN_PY.md`
- 恢复指南：`backups/RESTORE_GUIDE.md`

祝业务顺利！ 🚀