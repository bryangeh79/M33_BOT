# M33 Lotto Bot - 简单多租户测试脚本
# 纯英文，无编码问题

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "M33 Lotto Bot Multi-Tenant Test" -ForegroundColor Cyan
Write-Host "Setup two independent Bots" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# Step 1: Check working directory
Write-Host "`nStep 1: Check working directory" -ForegroundColor Yellow
$projectDir = "C:\AI_WORKSPACE\M33-Lotto-Bot-VN"
if ((Get-Location).Path -ne $projectDir) {
    Write-Host "Switching to project directory: $projectDir" -ForegroundColor Gray
    Set-Location $projectDir
}
Write-Host "OK Working directory: $(Get-Location)" -ForegroundColor Green

# Step 2: Create Bot 2 config
Write-Host "`nStep 2: Create Bot 2 configuration" -ForegroundColor Yellow

$bot2ConfigDir = "real_client_02"
if (Test-Path $bot2ConfigDir) {
    Remove-Item -Path $bot2ConfigDir -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "Cleaned old config directory" -ForegroundColor Gray
}

New-Item -ItemType Directory -Path $bot2ConfigDir -Force | Out-Null

# Bot 2 config - using your provided Token
$bot2EnvContent = @"
# M33 Lotto Bot - Bot 2 Test Config
# Token: 8226064460:AAH1dCFD6jmzz-fa3KPbBmdJvvuZtxhH9FM

BOT_TOKEN=8226064460:AAH1dCFD6jmzz-fa3KPbBmdJvvuZtxhH9FM
DEFAULT_ADMIN_USER_IDS=2063305617,6577170044

# Multi-tenant config
DB_PATH=data\real_client_02.db
LOG_PATH=logs\real_client_02.log
CLIENT_NAME=real_client_02
CLIENT_DISPLAY_NAME=Test Client 02
TIMEZONE=Asia/Ho_Chi_Minh
DEFAULT_LANGUAGE=vi
BOT_DISPLAY_NAME=M33 Lotto Bot (Client 02)
"@

$bot2EnvContent | Out-File -FilePath "$bot2ConfigDir\.env" -Encoding UTF8
Write-Host "OK Created Bot 2 config: $bot2ConfigDir\.env" -ForegroundColor Green

# Step 3: Ensure directories exist
Write-Host "`nStep 3: Create necessary directories" -ForegroundColor Yellow

$dirsToCreate = @("data", "logs")
foreach ($dir in $dirsToCreate) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "OK Created directory: $dir" -ForegroundColor Green
    } else {
        Write-Host "OK Directory exists: $dir" -ForegroundColor Green
    }
}

# Step 4: Set Python environment
Write-Host "`nStep 4: Set Python environment" -ForegroundColor Yellow
$env:PYTHONPATH = "C:\AI_WORKSPACE\M33-Lotto-Bot-VN"
Write-Host "OK Set PYTHONPATH: $env:PYTHONPATH" -ForegroundColor Green

# Step 5: Show test commands
Write-Host "`nStep 5: Test commands" -ForegroundColor Yellow
Write-Host "=" * 50 -ForegroundColor Cyan

Write-Host "`nBot 1 (Original):" -ForegroundColor Green
Write-Host "  Config: simple_test" -ForegroundColor Gray
Write-Host "  Token: 8713226156:AAGDHv1xd-lObWy7yAt_It7EBL3q225HMuw" -ForegroundColor Gray
Write-Host "  Database: data\simple_test.db" -ForegroundColor Gray
Write-Host "  Command: python src\app\main.py --config-dir simple_test" -ForegroundColor Gray

Write-Host "`nBot 2 (New):" -ForegroundColor Green
Write-Host "  Config: real_client_02" -ForegroundColor Gray
Write-Host "  Token: 8226064460:AAH1dCFD6jmzz-fa3KPbBmdJvvuZtxhH9FM" -ForegroundColor Gray
Write-Host "  Database: data\real_client_02.db" -ForegroundColor Gray
Write-Host "  Command: python src\app\main.py --config-dir real_client_02" -ForegroundColor Gray

Write-Host "`nTest Bot 2 now:" -ForegroundColor Yellow
Write-Host "python src\app\main.py --config-dir real_client_02" -ForegroundColor White -BackgroundColor DarkBlue

Write-Host "`nTelegram test:" -ForegroundColor Cyan
Write-Host "  1. Search for your new Bot (name from @BotFather)" -ForegroundColor Gray
Write-Host "  2. Send /start" -ForegroundColor Gray
Write-Host "  3. Send /myid" -ForegroundColor Gray
Write-Host "  4. Test other features" -ForegroundColor Gray

Write-Host "`nPress Ctrl+C to stop the Bot" -ForegroundColor Yellow

Write-Host "`n==========================================" -ForegroundColor Cyan
Write-Host "Setup complete! Ready to test." -ForegroundColor Cyan
Write-Host "Run the command above to start Bot 2." -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# Create simple launch script
$launchScript = @'
# Launch Bot 2
Write-Host "Starting Bot 2..." -ForegroundColor Cyan
Write-Host "Token: 8226064460:AAH1dCFD6jmzz-fa3KPbBmdJvvuZtxhH9FM" -ForegroundColor Gray
Write-Host "Database: data\real_client_02.db" -ForegroundColor Gray
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host "-" * 50 -ForegroundColor Gray

$env:PYTHONPATH = "C:\AI_WORKSPACE\M33-Lotto-Bot-VN"
python src\app\main.py --config-dir real_client_02
'@

$launchScript | Out-File -FilePath "launch_bot2.ps1" -Encoding UTF8
Write-Host "`nCreated launch script: launch_bot2.ps1" -ForegroundColor Green
Write-Host "Run: .\launch_bot2.ps1 to start Bot 2" -ForegroundColor Gray