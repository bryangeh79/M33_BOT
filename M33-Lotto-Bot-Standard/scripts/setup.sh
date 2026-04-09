#!/bin/bash
# M33 Lotto Bot Standard 安装脚本
# 版本: 1.0.0

set -e  # 遇到错误立即退出

echo "=========================================="
echo "🚀 M33 Lotto Bot Standard 安装开始"
echo "=========================================="

# 检查是否以root运行
if [ "$EUID" -ne 0 ]; then 
    echo "❌ 请使用 sudo 运行此脚本"
    exit 1
fi

# 定义变量
INSTALL_DIR="/opt/M33-Lotto-Bot-Standard"
LOG_DIR="/var/log/m33-standard"
SUPERVISOR_DIR="/etc/supervisor/conf.d"

echo "📁 创建目录结构..."

# 创建安装目录
mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

# 创建必要的目录
mkdir -p {configs,data,scripts,logs,supervisor}
mkdir -p "$LOG_DIR"

echo "🔧 创建10个客户配置模板..."

# 创建10个客户配置
for i in {01..10}; do
    CLIENT_DIR="configs/client_$i"
    mkdir -p "$CLIENT_DIR"
    
    # 创建.env模板（用户只需填写BOT_TOKEN）
    cat > "$CLIENT_DIR/.env.template" << EOF
# ===========================================
# M33 Lotto Bot Standard - 客户 $i 配置
# ===========================================
# 只需填写 BOT_TOKEN，其他自动生成
# ===========================================

# [必填] Telegram Bot Token
# 联系 @BotFather 创建新Bot获取
BOT_TOKEN=YOUR_BOT_TOKEN_HERE

# ===========================================
# 以下为系统自动生成，无需修改
# ===========================================
DB_PATH=$INSTALL_DIR/data/client_$i.db
LOG_PATH=$LOG_DIR/client_$i/app.log
CLIENT_NAME=client_$i
TIMEZONE=Asia/Ho_Chi_Minh
DEFAULT_LANGUAGE=vi
BOT_DISPLAY_NAME=M33 Lotto Bot
EOF
    
    # 创建settings.json
    cat > "$CLIENT_DIR/settings.json" << EOF
{
    "client_id": "$i",
    "features": {
        "enable_bet": true,
        "enable_report": true,
        "enable_settlement": true,
        "enable_admin": true
    },
    "ui": {
        "currency_symbol": "₫",
        "date_format": "YYYY-MM-DD"
    }
}
EOF
    
    # 创建空数据库文件
    touch "data/client_$i.db"
    
    echo "  ✅ 客户 $i 配置创建完成"
done

echo "⚙️ 创建Supervisor进程配置..."

# 创建Supervisor配置模板
cat > "supervisor/template.conf" << EOF
[program:m33-standard-client-XX]
command=python $INSTALL_DIR/src/app/main.py --config-dir $INSTALL_DIR/configs/client_XX
directory=$INSTALL_DIR
user=www-data
autostart=false
autorestart=true
startsecs=10
stopwaitsecs=30
stdout_logfile=$LOG_DIR/client_XX/stdout.log
stderr_logfile=$LOG_DIR/client_XX/stderr.log
environment=PYTHONPATH="$INSTALL_DIR",HOME="/tmp"
EOF

# 为每个客户生成Supervisor配置
for i in {01..10}; do
    sed "s/XX/$i/g" "supervisor/template.conf" > "$SUPERVISOR_DIR/m33-standard-client-$i.conf"
    echo "  ✅ 客户 $i Supervisor配置创建完成"
done

echo "📝 创建管理脚本..."

# 复制管理脚本（假设已存在）
if [ -f "scripts/activate.py" ]; then
    chmod +x scripts/activate.py
    echo "  ✅ activate.py 已设置可执行权限"
fi

if [ -f "scripts/manage.py" ]; then
    chmod +x scripts/manage.py
    echo "  ✅ manage.py 已设置可执行权限"
fi

echo "🔒 设置文件权限..."

# 设置权限
chown -R www-data:www-data "$INSTALL_DIR"
chmod 755 "$INSTALL_DIR"
chmod 755 "$INSTALL_DIR/scripts"
chmod 600 "$INSTALL_DIR/configs/client_"*/.env.template
chmod 644 "$INSTALL_DIR/data/"*.db
chmod 755 "$LOG_DIR"

echo "🔄 重新加载Supervisor配置..."

# 重新加载Supervisor
supervisorctl reread
supervisorctl update

echo "=========================================="
echo "✅ M33 Lotto Bot Standard 安装完成！"
echo "=========================================="
echo ""
echo "📋 下一步操作："
echo ""
echo "1. 部署M33 Bot源代码："
echo "   cp -r /path/to/m33-bot/src $INSTALL_DIR/"
echo ""
echo "2. 激活第一个客户："
echo "   cd $INSTALL_DIR"
echo "   python scripts/activate.py 01 YOUR_BOT_TOKEN"
echo ""
echo "3. 启动客户服务："
echo "   python scripts/manage.py start 01"
echo ""
echo "4. 验证运行状态："
echo "   python scripts/manage.py status 01"
echo ""
echo "5. 查看日志："
echo "   tail -f $LOG_DIR/client_01/stdout.log"
echo ""
echo "💡 提示："
echo "- 每个客户需要独立的Telegram Bot Token"
echo "- 使用 manage.py 脚本管理所有客户"
echo "- 定期备份 $INSTALL_DIR/data/ 目录"
echo "=========================================="