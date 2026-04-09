# M33 Lotto Bot - 多租户完整测试脚本
# 你只需要运行这个脚本，我会处理所有配置

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "M33 Lotto Bot 多租户测试" -ForegroundColor Cyan
Write-Host "配置两个独立Bot同时运行" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# 步骤1: 确保在正确目录
Write-Host "`n步骤1: 检查工作目录" -ForegroundColor Yellow
$projectDir = "C:\AI_WORKSPACE\M33-Lotto-Bot-VN"
if ((Get-Location).Path -ne $projectDir) {
    Write-Host "切换到项目目录: $projectDir" -ForegroundColor Gray
    Set-Location $projectDir
}
Write-Host "✅ 工作目录: $(Get-Location)" -ForegroundColor Green

# 步骤2: 创建Bot 2配置
Write-Host "`n步骤2: 创建Bot 2配置" -ForegroundColor Yellow

$bot2ConfigDir = "real_client_02"
if (Test-Path $bot2ConfigDir) {
    Remove-Item -Path $bot2ConfigDir -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "清理旧配置目录" -ForegroundColor Gray
}

New-Item -ItemType Directory -Path $bot2ConfigDir -Force | Out-Null

# Bot 2配置 - 使用你提供的Token
$bot2EnvContent = @"
# ===========================================
# M33 Lotto Bot - Bot 2 测试配置
# ===========================================
# Token: 8226064460:AAH1dCFD6jmzz-fa3KPbBmdJvvuZtxhH9FM
# ===========================================

BOT_TOKEN=8226064460:AAH1dCFD6jmzz-fa3KPbBmdJvvuZtxhH9FM
DEFAULT_ADMIN_USER_IDS=2063305617,6577170044

# ===========================================
# 多租户配置
# ===========================================
DB_PATH=data\real_client_02.db
LOG_PATH=logs\real_client_02.log
CLIENT_NAME=real_client_02
CLIENT_DISPLAY_NAME=测试客户02
TIMEZONE=Asia/Ho_Chi_Minh
DEFAULT_LANGUAGE=vi
BOT_DISPLAY_NAME=M33 Lotto Bot (客户02)
# ===========================================
"@

$bot2EnvContent | Out-File -FilePath "$bot2ConfigDir\.env" -Encoding UTF8
Write-Host "✅ 创建Bot 2配置: $bot2ConfigDir\.env" -ForegroundColor Green

# 步骤3: 确保Bot 1配置存在
Write-Host "`n步骤3: 检查Bot 1配置" -ForegroundColor Yellow

$bot1ConfigDir = "simple_test"
if (-not (Test-Path "$bot1ConfigDir\.env")) {
    Write-Host "创建Bot 1配置..." -ForegroundColor Gray
    
    New-Item -ItemType Directory -Path $bot1ConfigDir -Force | Out-Null
    
    $bot1EnvContent = @"
# ===========================================
# M33 Lotto Bot - Bot 1 测试配置
# ===========================================
# Token: 8713226156:AAGDHv1xd-lObWy7yAt_It7EBL3q225HMuw
# ===========================================

BOT_TOKEN=8713226156:AAGDHv1xd-lObWy7yAt_It7EBL3q225HMuw
DEFAULT_ADMIN_USER_IDS=2063305617,6577170044

# ===========================================
# 多租户配置
# ===========================================
DB_PATH=data\simple_test.db
LOG_PATH=logs\simple_test.log
CLIENT_NAME=simple_test
CLIENT_DISPLAY_NAME=测试客户01
TIMEZONE=Asia/Ho_Chi_Minh
DEFAULT_LANGUAGE=vi
BOT_DISPLAY_NAME=M33 Lotto Bot (客户01)
# ===========================================
"@
    
    $bot1EnvContent | Out-File -FilePath "$bot1ConfigDir\.env" -Encoding UTF8
    Write-Host "✅ 创建Bot 1配置: $bot1ConfigDir\.env" -ForegroundColor Green
} else {
    Write-Host "✅ Bot 1配置已存在: $bot1ConfigDir\.env" -ForegroundColor Green
}

# 步骤4: 确保目录存在
Write-Host "`n步骤4: 创建必要目录" -ForegroundColor Yellow

$dirsToCreate = @("data", "logs")
foreach ($dir in $dirsToCreate) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "✅ 创建目录: $dir" -ForegroundColor Green
    } else {
        Write-Host "✅ 目录已存在: $dir" -ForegroundColor Green
    }
}

# 步骤5: 设置Python环境
Write-Host "`n步骤5: 设置Python环境" -ForegroundColor Yellow
$env:PYTHONPATH = "C:\AI_WORKSPACE\M33-Lotto-Bot-VN"
Write-Host "✅ 设置PYTHONPATH: $env:PYTHONPATH" -ForegroundColor Green

# 检查Python依赖
Write-Host "`n检查Python依赖..." -ForegroundColor Gray
try {
    $depCheck = python -c "import telegram, dotenv; print('✅ 依赖正常')" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host $depCheck -ForegroundColor Green
    } else {
        Write-Host "⚠ 可能需要安装依赖" -ForegroundColor Yellow
        Write-Host "运行: pip install python-telegram-bot python-dotenv" -ForegroundColor Gray
    }
} catch {
    Write-Host "⚠ 依赖检查失败" -ForegroundColor Yellow
}

# 步骤6: 生成测试命令
Write-Host "`n步骤6: 测试命令生成" -ForegroundColor Yellow
Write-Host "=" * 50 -ForegroundColor Cyan

Write-Host "`n📋 两个Bot配置详情:" -ForegroundColor Cyan

Write-Host "`n🤖 Bot 1 (原有):" -ForegroundColor Green
Write-Host "   配置目录: simple_test" -ForegroundColor Gray
Write-Host "   Token: 8713226156:AAGDHv1xd-lObWy7yAt_It7EBL3q225HMuw" -ForegroundColor Gray
Write-Host "   数据库: data\simple_test.db" -ForegroundColor Gray
Write-Host "   启动命令: python src\app\main.py --config-dir simple_test" -ForegroundColor Gray

Write-Host "`n🤖 Bot 2 (新建):" -ForegroundColor Green
Write-Host "   配置目录: real_client_02" -ForegroundColor Gray
Write-Host "   Token: 8226064460:AAH1dCFD6jmzz-fa3KPbBmdJvvuZtxhH9FM" -ForegroundColor Gray
Write-Host "   数据库: data\real_client_02.db" -ForegroundColor Gray
Write-Host "   启动命令: python src\app\main.py --config-dir real_client_02" -ForegroundColor Gray

Write-Host "`n🚀 测试方案:" -ForegroundColor Cyan

Write-Host "`n方案A: 先启动Bot 2 (推荐)" -ForegroundColor Yellow
Write-Host "   1. 运行下面的'启动Bot 2'命令" -ForegroundColor Gray
Write-Host "   2. 观察启动是否成功" -ForegroundColor Gray
Write-Host "   3. 在Telegram中搜索新Bot测试" -ForegroundColor Gray

Write-Host "`n方案B: 同时运行两个Bot" -ForegroundColor Yellow
Write-Host "   需要两个PowerShell窗口:" -ForegroundColor Gray
Write-Host "   窗口1: python src\app\main.py --config-dir simple_test" -ForegroundColor Gray
Write-Host "   窗口2: python src\app\main.py --config-dir real_client_02" -ForegroundColor Gray

Write-Host "`n🔧 快速测试命令:" -ForegroundColor Cyan

Write-Host "`n启动Bot 2:" -ForegroundColor Yellow
Write-Host "python src\app\main.py --config-dir real_client_02" -ForegroundColor White -BackgroundColor DarkBlue

Write-Host "`n启动Bot 1:" -ForegroundColor Yellow
Write-Host "python src\app\main.py --config-dir simple_test" -ForegroundColor White -BackgroundColor DarkBlue

Write-Host "`n📱 Telegram测试步骤:" -ForegroundColor Cyan
Write-Host "   1. 搜索'Bot 2' (你在@BotFather设置的名字)" -ForegroundColor Gray
Write-Host "   2. 发送 /start" -ForegroundColor Gray
Write-Host "   3. 发送 /myid 验证" -ForegroundColor Gray
Write-Host "   4. 测试其他功能" -ForegroundColor Gray

Write-Host "`n⚠ 注意事项:" -ForegroundColor Red
Write-Host "   - 确保两个Bot使用不同的Token" -ForegroundColor Yellow
Write-Host "   - 两个数据库文件独立: simple_test.db vs real_client_02.db" -ForegroundColor Yellow
Write-Host "   - 按 Ctrl+C 停止Bot" -ForegroundColor Yellow
Write-Host "   - 首次启动可能需要时间初始化数据库" -ForegroundColor Yellow

Write-Host "`n✅ 配置完成！" -ForegroundColor Green
Write-Host "现在可以运行测试命令了。" -ForegroundColor Green

Write-Host "`n==========================================" -ForegroundColor Cyan
Write-Host "多租户测试准备完成！" -ForegroundColor Cyan
Write-Host "运行上面的命令开始测试。" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# 步骤7: 创建一键启动脚本
Write-Host "`n步骤7: 创建一键启动脚本" -ForegroundColor Yellow

$launchBot2Script = @'
# 一键启动Bot 2
Write-Host "启动Bot 2..." -ForegroundColor Cyan
Write-Host "Token: 8226064460:AAH1dCFD6jmzz-fa3KPbBmdJvvuZtxhH9FM" -ForegroundColor Gray
Write-Host "数据库: data\real_client_02.db" -ForegroundColor Gray
Write-Host "按 Ctrl+C 停止" -ForegroundColor Yellow
Write-Host "-" * 50 -ForegroundColor Gray

$env:PYTHONPATH = "C:\AI_WORKSPACE\M33-Lotto-Bot-VN"
python src\app\main.py --config-dir real_client_02
'@

$launchBot2Script | Out-File -FilePath "launch_bot2.ps1" -Encoding UTF8
Write-Host "✅ 创建一键启动脚本: launch_bot2.ps1" -ForegroundColor Green
Write-Host "   运行: .\launch_bot2.ps1 启动Bot 2" -ForegroundColor Gray

Write-Host "`n🚀 现在运行测试命令吧！" -ForegroundColor Green