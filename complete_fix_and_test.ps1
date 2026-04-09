# M33 Lotto Bot - 完整修复和测试脚本
# 在PowerShell中运行此脚本

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "M33 Lotto Bot 完整修复和测试" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# 1. 设置工作目录
$workspace = "C:\AI_WORKSPACE\M33-Lotto-Bot-VN"
Set-Location $workspace
Write-Host "工作目录: $(Get-Location)" -ForegroundColor Green

# 2. 设置Python环境
$env:PYTHONPATH = $workspace
Write-Host "设置PYTHONPATH: $env:PYTHONPATH" -ForegroundColor Green

# 3. 检查Bot 2配置
Write-Host "`n检查Bot 2配置..." -ForegroundColor Yellow
$bot2Config = "test_bot2_fix"
if (-not (Test-Path "$bot2Config\.env")) {
    Write-Host "创建Bot 2配置..." -ForegroundColor Gray
    New-Item -ItemType Directory -Path $bot2Config -Force | Out-Null
    
    @"
BOT_TOKEN=8226064460:AAH1dCFD6jmzz-fa3KPbBmdJvvuZtxhH9FM
DB_PATH=data\test_bot2_fix.db
CLIENT_NAME=test_bot2_fix
TIMEZONE=Asia/Ho_Chi_Minh
DEFAULT_ADMIN_USER_IDS=2063305617,6577170044
"@ | Out-File -FilePath "$bot2Config\.env" -Encoding UTF8
    
    Write-Host "✅ 创建Bot 2配置" -ForegroundColor Green
} else {
    Write-Host "✅ Bot 2配置已存在" -ForegroundColor Green
    Write-Host "配置内容:" -ForegroundColor Gray
    Get-Content "$bot2Config\.env"
}

# 4. 检查Bot 1配置
Write-Host "`n检查Bot 1配置..." -ForegroundColor Yellow
$bot1Config = "simple_test"
if (-not (Test-Path "$bot1Config\.env")) {
    Write-Host "创建Bot 1配置..." -ForegroundColor Gray
    New-Item -ItemType Directory -Path $bot1Config -Force | Out-Null
    
    @"
BOT_TOKEN=8713226156:AAGDHv1xd-lObWy7yAt_It7EBL3q225HMuw
DB_PATH=data\simple_test.db
CLIENT_NAME=simple_test
TIMEZONE=Asia/Ho_Chi_Minh
DEFAULT_ADMIN_USER_IDS=2063305617,6577170044
"@ | Out-File -FilePath "$bot1Config\.env" -Encoding UTF8
    
    Write-Host "✅ 创建Bot 1配置" -ForegroundColor Green
} else {
    Write-Host "✅ Bot 1配置已存在" -ForegroundColor Green
}

# 5. 确保目录存在
Write-Host "`n创建必要目录..." -ForegroundColor Yellow
$dirs = @("data", "logs")
foreach ($dir in $dirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "✅ 创建目录: $dir" -ForegroundColor Green
    } else {
        Write-Host "✅ 目录已存在: $dir" -ForegroundColor Green
    }
}

# 6. 验证Token
Write-Host "`n验证Bot 2 Token..." -ForegroundColor Yellow

# 创建Token检查脚本
$tokenCheckScript = @'
import requests
import sys

def check_token(token):
    print(f"验证Token: {token[:15]}...")
    
    try:
        url = f"https://api.telegram.org/bot{token}/getMe"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("ok"):
                bot = data["result"]
                print(f"✅ Token有效")
                print(f"   Bot ID: {bot.get('id')}")
                print(f"   用户名: @{bot.get('username')}")
                print(f"   名称: {bot.get('first_name')}")
                return True
            else:
                print(f"❌ API错误: {data.get('description')}")
                return False
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

if __name__ == "__main__":
    token = "8226064460:AAH1dCFD6jmzz-fa3KPbBmdJvvuZtxhH9FM"
    success = check_token(token)
    sys.exit(0 if success else 1)
'@

$tokenCheckScript | Out-File -FilePath "check_token.py" -Encoding UTF8
python check_token.py
$tokenResult = $LASTEXITCODE
Remove-Item -FilePath "check_token.py" -Force

if ($tokenResult -ne 0) {
    Write-Host "❌ Bot 2 Token无效，请检查" -ForegroundColor Red
    Write-Host "在@BotFather中检查Bot状态和隐私设置" -ForegroundColor Yellow
    exit 1
}

# 7. 测试启动Bot 2
Write-Host "`n测试启动Bot 2..." -ForegroundColor Yellow
Write-Host "命令: python src\app\main.py --config-dir $bot2Config" -ForegroundColor Gray
Write-Host "按Ctrl+C停止测试" -ForegroundColor Yellow
Write-Host "-" * 50 -ForegroundColor Gray

Write-Host "`n🚀 开始测试Bot 2..." -ForegroundColor Cyan
Write-Host "如果看到以下输出表示成功:" -ForegroundColor Gray
Write-Host "  ✅ 配置加载完成" -ForegroundColor Gray
Write-Host "  ✅ BOT_TOKEN loaded" -ForegroundColor Gray  
Write-Host "  ✅ Database ready" -ForegroundColor Gray
Write-Host "  ▶ Starting polling ..." -ForegroundColor Gray
Write-Host "`n在Telegram中给Bot 2发送/start测试" -ForegroundColor Gray
Write-Host "观察控制台是否显示接收消息" -ForegroundColor Gray
Write-Host "按Ctrl+C停止" -ForegroundColor Yellow
Write-Host "-" * 50 -ForegroundColor Gray

# 直接启动Bot 2
try {
    python src\app\main.py --config-dir $bot2Config
} catch {
    Write-Host "❌ 启动失败: $_" -ForegroundColor Red
}

Write-Host "`n==========================================" -ForegroundColor Cyan
Write-Host "测试完成！" -ForegroundColor Cyan

if ($tokenResult -eq 0) {
    Write-Host "✅ Token验证通过" -ForegroundColor Green
    Write-Host "✅ 配置检查通过" -ForegroundColor Green
    Write-Host "🚀 如果Bot 2响应，多租户测试成功！" -ForegroundColor Green
} else {
    Write-Host "❌ 需要修复Token问题" -ForegroundColor Red
}

Write-Host "==========================================" -ForegroundColor Cyan

# 8. 创建简化启动脚本
Write-Host "`n创建简化启动脚本..." -ForegroundColor Yellow

$simpleLaunch = @'
# 启动Bot 2简化脚本
Write-Host "启动Bot 2..." -ForegroundColor Cyan
Write-Host "Token: 8226064460:AAH1dCFD6jmzz-fa3KPbBmdJvvuZtxhH9FM" -ForegroundColor Gray
Write-Host "数据库: data\test_bot2_fix.db" -ForegroundColor Gray
Write-Host "按Ctrl+C停止" -ForegroundColor Yellow
Write-Host "-" * 50 -ForegroundColor Gray

cd C:\AI_WORKSPACE\M33-Lotto-Bot-VN
$env:PYTHONPATH = "C:\AI_WORKSPACE\M33-Lotto-Bot-VN"
python src\app\main.py --config-dir test_bot2_fix
'@

$simpleLaunch | Out-File -FilePath "launch_bot2_simple.ps1" -Encoding UTF8
Write-Host "✅ 创建简化启动脚本: launch_bot2_simple.ps1" -ForegroundColor Green
Write-Host "   运行: .\launch_bot2_simple.ps1" -ForegroundColor Gray

Write-Host "`n🎯 下一步:" -ForegroundColor Cyan
Write-Host "1. 如果Bot 2测试成功，多租户功能验证完成" -ForegroundColor Gray
Write-Host "2. 可以测试两个Bot同时运行" -ForegroundColor Gray
Write-Host "3. 准备Phase V3步骤2: 服务器部署" -ForegroundColor Gray