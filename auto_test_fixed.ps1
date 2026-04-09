# M33 Lotto Bot - 自动测试脚本（修复版）
# 使用现有Bot Token自动创建测试配置

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "M33 Lotto Bot - 自动测试脚本" -ForegroundColor Cyan
Write-Host "使用现有Bot Token创建测试配置" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# 步骤1: 读取现有.env文件
Write-Host "`n步骤1: 读取现有配置" -ForegroundColor Yellow
$existingEnvPath = ".env"
if (-not (Test-Path $existingEnvPath)) {
    Write-Host "❌ 错误: 未找到 .env 文件" -ForegroundColor Red
    Write-Host "请在项目根目录创建 .env 文件，包含BOT_TOKEN" -ForegroundColor Yellow
    exit 1
}

# 读取现有配置
$envContent = Get-Content $existingEnvPath -Raw
Write-Host "✅ 找到现有 .env 文件" -ForegroundColor Green

# 提取BOT_TOKEN
$botTokenLine = $envContent -split "`n" | Where-Object { $_ -match "^BOT_TOKEN=" } | Select-Object -First 1
if (-not $botTokenLine) {
    Write-Host "❌ 错误: 未找到 BOT_TOKEN" -ForegroundColor Red
    exit 1
}

$botToken = $botTokenLine -replace "^BOT_TOKEN=", ""
$botToken = $botToken.Trim()
Write-Host "✅ 提取BOT_TOKEN: $($botToken.Substring(0, [Math]::Min(15, $botToken.Length)))..." -ForegroundColor Green

# 提取DEFAULT_ADMIN_USER_IDS（如果有）
$adminIdsLine = $envContent -split "`n" | Where-Object { $_ -match "^DEFAULT_ADMIN_USER_IDS=" } | Select-Object -First 1
if ($adminIdsLine) {
    $adminIds = $adminIdsLine -replace "^DEFAULT_ADMIN_USER_IDS=", ""
    $adminIds = $adminIds.Trim()
    Write-Host "✅ 提取ADMIN_USER_IDS: $adminIds" -ForegroundColor Green
} else {
    $adminIds = ""
    Write-Host "⚠ 未找到 DEFAULT_ADMIN_USER_IDS" -ForegroundColor Yellow
}

# 步骤2: 创建测试配置目录
Write-Host "`n步骤2: 创建测试配置" -ForegroundColor Yellow

# 清理旧的测试目录
$testDirs = @("test_client_a", "test_client_b", "test_client_c")
foreach ($dir in $testDirs) {
    if (Test-Path $dir) {
        Remove-Item -Path $dir -Recurse -Force -ErrorAction SilentlyContinue
        Write-Host "  清理旧目录: $dir" -ForegroundColor Gray
    }
}

# 创建3个测试客户配置
$clientConfigs = @(
    @{
        Name = "test_client_a"
        DisplayName = "测试客户A"
        DbPath = "data\test_client_a.db"
    },
    @{
        Name = "test_client_b" 
        DisplayName = "测试客户B"
        DbPath = "data\test_client_b.db"
    },
    @{
        Name = "test_client_c"
        DisplayName = "测试客户C"
        DbPath = "data\test_client_c.db"
    }
)

foreach ($client in $clientConfigs) {
    $clientDir = $client.Name
    New-Item -ItemType Directory -Path $clientDir -Force | Out-Null
    
    # 创建.env文件
    $envContent = @"
# ===========================================
# M33 Lotto Bot - 测试配置: $($client.DisplayName)
# ===========================================
# 创建时间: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
# ===========================================

# Bot配置
BOT_TOKEN=$botToken

# 管理员配置
DEFAULT_ADMIN_USER_IDS=$adminIds

# ===========================================
# 多租户特定配置
# ===========================================
DB_PATH=$($client.DbPath)
LOG_PATH=logs\$($client.Name).log
CLIENT_NAME=$($client.Name)
CLIENT_DISPLAY_NAME=$($client.DisplayName)
TIMEZONE=Asia/Ho_Chi_Minh
DEFAULT_LANGUAGE=vi
BOT_DISPLAY_NAME=M33 Lotto Bot ($($client.DisplayName))
# ===========================================
"@
    
    $envContent | Out-File -FilePath "$clientDir\.env" -Encoding UTF8
    Write-Host "✅ 创建配置: $clientDir\.env" -ForegroundColor Green
    
    # 确保数据库目录存在
    $dbDir = Split-Path $client.DbPath -Parent
    if ($dbDir -and -not (Test-Path $dbDir)) {
        New-Item -ItemType Directory -Path $dbDir -Force | Out-Null
        Write-Host "   创建数据库目录: $dbDir" -ForegroundColor Gray
    }
    
    # 确保日志目录存在
    $logDir = "logs"
    if (-not (Test-Path $logDir)) {
        New-Item -ItemType Directory -Path $logDir -Force | Out-Null
        Write-Host "   创建日志目录: $logDir" -ForegroundColor Gray
    }
}

# 步骤3: 验证配置（使用单独的Python文件）
Write-Host "`n步骤3: 验证配置" -ForegroundColor Yellow

# 创建验证Python脚本
$pythonValidationScript = @'
import os
import sys

print("验证测试配置...")

test_dirs = ["test_client_a", "test_client_b", "test_client_c"]
all_valid = True

for test_dir in test_dirs:
    print(f"\n检查配置: {test_dir}")
    
    env_file = os.path.join(test_dir, ".env")
    if not os.path.exists(env_file):
        print(f"  ❌ 配置文件不存在: {env_file}")
        all_valid = False
        continue
    
    # 读取配置
    config = {}
    with open(env_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and '=' in line and not line.startswith('#'):
                key, value = line.split('=', 1)
                config[key.strip()] = value.strip()
    
    # 验证必要配置
    required = ['BOT_TOKEN', 'DB_PATH', 'CLIENT_NAME']
    for key in required:
        if key not in config or not config[key]:
            print(f"  ❌ 缺少配置: {key}")
            all_valid = False
        else:
            if key == 'BOT_TOKEN':
                print(f"  ✅ {key}: {config[key][:15]}...")
            else:
                print(f"  ✅ {key}: {config[key]}")
    
    # 检查数据库路径
    db_path = config.get('DB_PATH', '')
    if db_path:
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
            print(f"  ✅ 创建数据库目录: {db_dir}")

if all_valid:
    print("\n✅ 所有测试配置验证通过")
    sys.exit(0)
else:
    print("\n❌ 配置验证失败")
    sys.exit(1)
'@

$pythonValidationScript | Out-File -FilePath "validate_test_configs.py" -Encoding UTF8
python validate_test_configs.py
$validationResult = $LASTEXITCODE
Remove-Item -FilePath "validate_test_configs.py" -Force

if ($validationResult -ne 0) {
    Write-Host "❌ 配置验证失败" -ForegroundColor Red
    exit 1
}

# 步骤4: 生成测试命令
Write-Host "`n步骤4: 测试命令生成" -ForegroundColor Yellow
Write-Host "=" * 50 -ForegroundColor Cyan

Write-Host "`n🎯 测试方案选择:" -ForegroundColor Cyan

Write-Host "`n方案1: 单个客户测试（推荐开始）" -ForegroundColor Green
Write-Host "  命令: python src\app\main.py --config-dir test_client_a" -ForegroundColor Gray
Write-Host "  数据库: data\test_client_a.db" -ForegroundColor Gray
Write-Host "  日志: logs\test_client_a.log" -ForegroundColor Gray

Write-Host "`n方案2: 多客户同时测试（高级）" -ForegroundColor Green
Write-Host "  需要打开多个PowerShell窗口:" -ForegroundColor Gray
Write-Host "  窗口1: python src\app\main.py --config-dir test_client_a" -ForegroundColor Gray
Write-Host "  窗口2: python src\app\main.py --config-dir test_client_b" -ForegroundColor Gray
Write-Host "  窗口3: python src\app\main.py --config-dir test_client_c" -ForegroundColor Gray

Write-Host "`n方案3: 对比测试（原有vs新方式）" -ForegroundColor Green
Write-Host "  原有方式: python src\app\main.py" -ForegroundColor Gray
Write-Host "  新方式: python src\app\main.py --config-dir test_client_a" -ForegroundColor Gray

Write-Host "`n🔧 快速测试命令:" -ForegroundColor Cyan
Write-Host "  # 测试客户A" -ForegroundColor Yellow
Write-Host "  python src\app\main.py --config-dir test_client_a" -ForegroundColor Gray

Write-Host "`n  # 测试客户B" -ForegroundColor Yellow
Write-Host "  python src\app\main.py --config-dir test_client_b" -ForegroundColor Gray

Write-Host "`n  # 测试原有方式" -ForegroundColor Yellow
Write-Host "  python src\app\main.py" -ForegroundColor Gray

Write-Host "`n📋 验证要点:" -ForegroundColor Cyan
Write-Host "  1. 观察启动日志，确认无错误" -ForegroundColor Gray
Write-Host "  2. 检查数据库文件是否创建" -ForegroundColor Gray
Write-Host "  3. 在Telegram中测试Bot响应" -ForegroundColor Gray
Write-Host "  4. 验证不同客户使用不同数据库" -ForegroundColor Gray

Write-Host "`n⚠ 注意事项:" -ForegroundColor Red
Write-Host "  - 确保Python依赖已安装: python-telegram-bot, python-dotenv" -ForegroundColor Yellow
Write-Host "  - 首次启动可能需要时间初始化数据库" -ForegroundColor Yellow
Write-Host "  - 按 Ctrl+C 停止Bot" -ForegroundColor Yellow
Write-Host "  - 测试完成后可以删除测试目录" -ForegroundColor Yellow

Write-Host "`n🧹 清理命令:" -ForegroundColor Gray
Write-Host "  # 删除测试配置" -ForegroundColor DarkGray
Write-Host "  Remove-Item -Path test_client_a,test_client_b,test_client_c -Recurse -Force" -ForegroundColor DarkGray
Write-Host "  # 删除测试数据库" -ForegroundColor DarkGray
Write-Host "  Remove-Item -Path data\test_*.db -Force -ErrorAction SilentlyContinue" -ForegroundColor DarkGray

Write-Host "`n==========================================" -ForegroundColor Cyan
Write-Host "自动测试脚本完成！" -ForegroundColor Cyan
Write-Host "已创建3个测试客户配置。" -ForegroundColor Cyan
Write-Host "现在可以开始测试！" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# 步骤5: 创建一键测试脚本
Write-Host "`n步骤5: 创建一键测试脚本" -ForegroundColor Yellow

$quickTestScript = @'
# 一键测试脚本 - test_client_a
Write-Host "启动测试客户A..." -ForegroundColor Cyan
Write-Host "命令: python src\app\main.py --config-dir test_client_a" -ForegroundColor Gray
Write-Host "按 Ctrl+C 停止" -ForegroundColor Yellow
Write-Host "-" * 50 -ForegroundColor Gray

python src\app\main.py --config-dir test_client_a
'@

$quickTestScript | Out-File -FilePath "quick_test.ps1" -Encoding UTF8
Write-Host "✅ 创建一键测试脚本: quick_test.ps1" -ForegroundColor Green
Write-Host "   运行: .\quick_test.ps1 启动测试客户A" -ForegroundColor Gray

Write-Host "`n🚀 开始测试吧！建议从方案1开始。" -ForegroundColor Green