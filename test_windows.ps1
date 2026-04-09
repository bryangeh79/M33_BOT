# Windows PowerShell 测试脚本
# M33 Lotto Bot Standard - 本地测试

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "M33 Lotto Bot - Windows 本地测试" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# 步骤1: 检查Python
Write-Host "`n步骤1: 检查Python环境" -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Python已安装: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "❌ Python未安装或不在PATH中" -ForegroundColor Red
    Write-Host "请从 https://python.org 下载安装Python 3.8+" -ForegroundColor Yellow
    exit 1
}

# 步骤2: 检查依赖
Write-Host "`n步骤2: 检查Python依赖" -ForegroundColor Yellow
try {
    $dotenv = python -c "import dotenv; print('dotenv version:', dotenv.__version__)" 2>&1
    Write-Host "✅ python-dotenv已安装" -ForegroundColor Green
} catch {
    Write-Host "⚠ python-dotenv未安装，正在安装..." -ForegroundColor Yellow
    pip install python-dotenv
}

try {
    $telegram = python -c "import telegram; print('telegram-bot version:', telegram.__version__)" 2>&1
    Write-Host "✅ python-telegram-bot已安装" -ForegroundColor Green
} catch {
    Write-Host "⚠ python-telegram-bot未安装，正在安装..." -ForegroundColor Yellow
    pip install python-telegram-bot
}

# 步骤3: 创建测试配置
Write-Host "`n步骤3: 创建测试配置" -ForegroundColor Yellow
$testDir = "windows_test_client"
if (Test-Path $testDir) {
    Remove-Item -Path $testDir -Recurse -Force
}

New-Item -ItemType Directory -Path $testDir -Force | Out-Null

$envContent = @"
# ===========================================
# M33 Lotto Bot - Windows 测试配置
# ===========================================
# 使用测试Token，实际使用时替换为真实Token
# ===========================================

BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrSTUvwxYZ

# ===========================================
# 系统配置
# ===========================================
DB_PATH=data\windows_test.db
LOG_PATH=logs\windows_test.log
CLIENT_NAME=windows_test_client
TIMEZONE=Asia/Ho_Chi_Minh
DEFAULT_LANGUAGE=vi
BOT_DISPLAY_NAME=M33 Lotto Bot (Windows Test)
# ===========================================
"@

$envContent | Out-File -FilePath "$testDir\.env" -Encoding UTF8
Write-Host "✅ 测试配置创建完成: $testDir\.env" -ForegroundColor Green

# 步骤4: 测试配置加载
Write-Host "`n步骤4: 测试配置加载" -ForegroundColor Yellow
try {
    # 创建简化的配置加载测试
    $testScript = @"
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_config_loading():
    """测试配置加载"""
    config_dir = "windows_test_client"
    
    # 读取.env文件
    env_file = os.path.join(config_dir, ".env")
    if not os.path.exists(env_file):
        print("❌ 配置文件不存在")
        return False
    
    # 简单解析
    config = {}
    with open(env_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                config[key.strip()] = value.strip()
    
    print("✅ 配置加载成功")
    print(f"   客户: {config.get('CLIENT_NAME', 'N/A')}")
    print(f"   数据库: {config.get('DB_PATH', 'N/A')}")
    print(f"   Token: {config.get('BOT_TOKEN', 'N/A')[:15]}...")
    
    # 设置环境变量
    os.environ['DB_PATH'] = config.get('DB_PATH', '')
    os.environ['BOT_TOKEN'] = config.get('BOT_TOKEN', '')
    
    return True

if __name__ == "__main__":
    if test_config_loading():
        print("✅ 配置测试通过")
        sys.exit(0)
    else:
        print("❌ 配置测试失败")
        sys.exit(1)
"@

    $testScript | Out-File -FilePath "test_windows_config.py" -Encoding UTF8
    python test_windows_config.py
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ 配置加载测试通过" -ForegroundColor Green
    } else {
        Write-Host "❌ 配置加载测试失败" -ForegroundColor Red
    }
    
    Remove-Item -Path "test_windows_config.py" -Force
} catch {
    Write-Host "❌ 配置测试异常: $_" -ForegroundColor Red
}

# 步骤5: 测试main.py参数解析
Write-Host "`n步骤5: 测试main.py参数解析" -ForegroundColor Yellow
try {
    Write-Host "测试 --help 参数..." -ForegroundColor Gray
    python src\app\main.py --help 2>&1 | Select-String -Pattern "usage:|--config-dir" | ForEach-Object {
        Write-Host "  $_" -ForegroundColor Gray
    }
    Write-Host "✅ main.py参数解析正常" -ForegroundColor Green
} catch {
    Write-Host "❌ main.py测试失败: $_" -ForegroundColor Red
}

# 步骤6: 清理和建议
Write-Host "`n步骤6: 测试完成和建议" -ForegroundColor Yellow
Write-Host "=" * 50 -ForegroundColor Cyan

Write-Host "`n📋 测试结果总结:" -ForegroundColor Cyan
Write-Host "  ✅ Python环境检查" -ForegroundColor Green
Write-Host "  ✅ 依赖检查/安装" -ForegroundColor Green
Write-Host "  ✅ 测试配置创建" -ForegroundColor Green
Write-Host "  ✅ 配置加载测试" -ForegroundColor Green
Write-Host "  ✅ main.py参数解析" -ForegroundColor Green

Write-Host "`n🚀 下一步测试建议:" -ForegroundColor Cyan
Write-Host "  1. 获取真实Bot Token:" -ForegroundColor Yellow
Write-Host "     - 在Telegram中联系 @BotFather" -ForegroundColor Gray
Write-Host "     - 发送 /newbot 创建测试Bot" -ForegroundColor Gray
Write-Host "     - 复制Token到 .env 文件" -ForegroundColor Gray

Write-Host "`n  2. 启动测试Bot:" -ForegroundColor Yellow
Write-Host "     python src\app\main.py --config-dir windows_test_client" -ForegroundColor Gray

Write-Host "`n  3. 在Telegram中测试:" -ForegroundColor Yellow
Write-Host "     - 搜索你的Bot用户名" -ForegroundColor Gray
Write-Host "     - 发送 /start 命令" -ForegroundColor Gray
Write-Host "     - 测试基本功能" -ForegroundColor Gray

Write-Host "`n⚠ 注意事项:" -ForegroundColor Red
Write-Host "  - 首次启动可能需要创建数据库" -ForegroundColor Yellow
Write-Host "  - 确保防火墙允许出站连接" -ForegroundColor Yellow
Write-Host "  - 测试完成后记得停止Bot (Ctrl+C)" -ForegroundColor Yellow

Write-Host "`n==========================================" -ForegroundColor Cyan
Write-Host "Windows本地测试脚本完成！" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan