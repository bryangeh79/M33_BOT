#!/bin/bash
# M33 Lotto Bot Standard - 数据库备份脚本
# 版本: 1.0.0

set -e

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }

# 配置
BACKUP_DIR="/opt/M33-Lotto-Bot-Standard/backups"
DATA_DIR="/opt/M33-Lotto-Bot-Standard/data"
LOG_DIR="/var/log/m33-standard"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_NAME="m33_backup_${TIMESTAMP}"
BACKUP_PATH="${BACKUP_DIR}/${BACKUP_NAME}"

echo "=========================================="
echo "📦 M33 Lotto Bot Standard 备份开始"
echo "=========================================="

# 检查目录
if [ ! -d "$DATA_DIR" ]; then
    print_error "数据目录不存在: $DATA_DIR"
    exit 1
fi

# 创建备份目录
mkdir -p "$BACKUP_PATH"
print_success "备份目录创建: $BACKUP_PATH"

# 备份数据库文件
echo ""
print_info "备份数据库文件..."
DB_COUNT=0
for db_file in "$DATA_DIR"/*.db; do
    if [ -f "$db_file" ]; then
        filename=$(basename "$db_file")
        cp "$db_file" "$BACKUP_PATH/${filename}"
        print_success "  $filename"
        DB_COUNT=$((DB_COUNT + 1))
    fi
done

if [ $DB_COUNT -eq 0 ]; then
    print_warning "未找到数据库文件"
else
    print_success "数据库备份完成: $DB_COUNT 个文件"
fi

# 备份配置文件
echo ""
print_info "备份配置文件..."
CONFIG_COUNT=0
for config_dir in /opt/M33-Lotto-Bot-Standard/configs/client_*; do
    if [ -d "$config_dir" ]; then
        client_id=$(basename "$config_dir" | sed 's/client_//')
        mkdir -p "$BACKUP_PATH/configs/client_${client_id}"
        
        # 备份.env文件（如果存在）
        if [ -f "$config_dir/.env" ]; then
            cp "$config_dir/.env" "$BACKUP_PATH/configs/client_${client_id}/.env"
            CONFIG_COUNT=$((CONFIG_COUNT + 1))
        fi
        
        # 备份settings.json
        if [ -f "$config_dir/settings.json" ]; then
            cp "$config_dir/settings.json" "$BACKUP_PATH/configs/client_${client_id}/settings.json"
            CONFIG_COUNT=$((CONFIG_COUNT + 1))
        fi
    fi
done

if [ $CONFIG_COUNT -eq 0 ]; then
    print_warning "未找到配置文件"
else
    print_success "配置文件备份完成: $CONFIG_COUNT 个文件"
fi

# 备份Supervisor配置
echo ""
print_info "备份Supervisor配置..."
SUPERVISOR_COUNT=0
mkdir -p "$BACKUP_PATH/supervisor"
for conf_file in /etc/supervisor/conf.d/m33-standard-client-*.conf; do
    if [ -f "$conf_file" ]; then
        cp "$conf_file" "$BACKUP_PATH/supervisor/"
        SUPERVISOR_COUNT=$((SUPERVISOR_COUNT + 1))
    fi
done

if [ $SUPERVISOR_COUNT -eq 0 ]; then
    print_warning "未找到Supervisor配置"
else
    print_success "Supervisor配置备份完成: $SUPERVISOR_COUNT 个文件"
fi

# 创建备份信息文件
echo ""
print_info "创建备份信息..."
cat > "$BACKUP_PATH/backup_info.txt" << EOF
M33 Lotto Bot Standard 备份信息
================================
备份时间: $(date)
备份名称: $BACKUP_NAME
备份目录: $BACKUP_PATH

统计信息:
- 数据库文件: $DB_COUNT 个
- 配置文件: $CONFIG_COUNT 个
- Supervisor配置: $SUPERVISOR_COUNT 个

系统信息:
- 主机名: $(hostname)
- 时间: $(date)
- 用户: $(whoami)

激活客户列表:
EOF

# 添加激活客户信息
for config_dir in /opt/M33-Lotto-Bot-Standard/configs/client_*; do
    if [ -d "$config_dir" ] && [ -f "$config_dir/.env" ]; then
        client_id=$(basename "$config_dir" | sed 's/client_//')
        if grep -q "BOT_TOKEN=" "$config_dir/.env" && ! grep -q "YOUR_BOT_TOKEN_HERE" "$config_dir/.env"; then
            echo "- 客户 $client_id: 已激活" >> "$BACKUP_PATH/backup_info.txt"
        else
            echo "- 客户 $client_id: 未激活" >> "$BACKUP_PATH/backup_info.txt"
        fi
    fi
done

print_success "备份信息文件创建完成"

# 压缩备份
echo ""
print_info "压缩备份文件..."
cd "$BACKUP_DIR"
tar -czf "${BACKUP_NAME}.tar.gz" "$BACKUP_NAME"
BACKUP_SIZE=$(du -h "${BACKUP_NAME}.tar.gz" | cut -f1)
print_success "备份压缩完成: ${BACKUP_NAME}.tar.gz ($BACKUP_SIZE)"

# 清理临时目录
rm -rf "$BACKUP_PATH"
print_success "临时文件已清理"

# 清理旧备份（保留最近7天）
echo ""
print_info "清理旧备份（保留最近7天）..."
find "$BACKUP_DIR" -name "m33_backup_*.tar.gz" -mtime +7 -delete 2>/dev/null || true
print_success "旧备份清理完成"

# 显示备份统计
echo ""
print_info "备份统计:"
echo "  备份文件: ${BACKUP_NAME}.tar.gz"
echo "  文件大小: $BACKUP_SIZE"
echo "  保存位置: $BACKUP_DIR"
echo "  数据库文件: $DB_COUNT 个"
echo "  配置文件: $CONFIG_COUNT 个"

# 创建恢复指南
cat > "$BACKUP_DIR/RESTORE_GUIDE.md" << 'EOF'
# M33 Lotto Bot Standard 恢复指南

## 恢复步骤

### 1. 停止所有服务
```bash
cd /opt/M33-Lotto-Bot-Standard
python scripts/manage.py stop-all
```

### 2. 解压备份文件
```bash
cd /opt/M33-Lotto-Bot-Standard/backups
tar -xzf m33_backup_YYYYMMDD_HHMMSS.tar.gz
```

### 3. 恢复数据库文件
```bash
# 复制数据库文件
cp -r m33_backup_YYYYMMDD_HHMMSS/data/* /opt/M33-Lotto-Bot-Standard/data/

# 设置权限
chown www-data:www-data /opt/M33-Lotto-Bot-Standard/data/*.db
chmod 644 /opt/M33-Lotto-Bot-Standard/data/*.db
```

### 4. 恢复配置文件（如果需要）
```bash
# 复制配置文件
cp -r m33_backup_YYYYMMDD_HHMMSS/configs/* /opt/M33-Lotto-Bot-Standard/configs/

# 设置权限
chmod 600 /opt/M33-Lotto-Bot-Standard/configs/client_*/.env
```

### 5. 恢复Supervisor配置（如果需要）
```bash
# 复制Supervisor配置
cp m33_backup_YYYYMMDD_HHMMSS/supervisor/*.conf /etc/supervisor/conf.d/

# 重新加载配置
supervisorctl reread
supervisorctl update
```

### 6. 启动服务
```bash
cd /opt/M33-Lotto-Bot-Standard
python scripts/manage.py start-all
```

### 7. 验证恢复
```bash
python scripts/manage.py status-all
```

## 注意事项
1. 恢复前确保已停止所有服务
2. 恢复后检查文件权限
3. 验证数据库完整性
4. 测试客户功能是否正常
EOF

print_success "恢复指南已创建: $BACKUP_DIR/RESTORE_GUIDE.md"

echo ""
echo "=========================================="
print_success "✅ 备份完成！"
echo "=========================================="
echo ""
print_info "备份文件: ${BACKUP_NAME}.tar.gz"
print_info "文件大小: $BACKUP_SIZE"
print_info "保存位置: $BACKUP_DIR"
echo ""
print_info "下次备份:"
echo "  手动运行: bash scripts/backup.sh"
echo "  定时任务: 添加cron job"
echo ""
print_info "恢复备份:"
echo "  查看: $BACKUP_DIR/RESTORE_GUIDE.md"
echo "=========================================="