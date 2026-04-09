# 简单测试脚本 - 创建测试配置

Write-Host "M33 Lotto Bot - 简单测试脚本" -ForegroundColor Cyan
Write-Host "==============================" -ForegroundColor Cyan

# 1. 检查.env文件
if (-not (Test-Path ".env")) {
    Write-Host "❌ 错误: 未找到 .env 文件" -ForegroundColor Red
    exit 1
}

# 2. 读取BOT_TOKEN
$envContent = Get-Content ".env" -Raw
$botTokenLine = $envContent -split "`n" | Where-Object { $_ -match "^BOT_TOKEN=" } | Select-Object -First 1

if (-not $botTokenLine) {
    Write-Host "❌ 错误: 未找到 BOT_TOKEN" -ForegroundColor Red
    exit 1
}

$botToken = $botTokenLine -replace "^BOT_TOKEN=", ""
$botToken = $botToken.Trim()
Write-Host "✅ 使用BOT_TOKEN: $($botToken.Substring(0, [Math]::Min(15, $botToken.Length)))..." -ForegroundColor Green

# 3. 创建测试配置
$testDir = "simple_test_client"
if (Test-Path $testDir) {
    Remove-Item -Path $testDir -Recurse -Force
}

New-Item -ItemType Directory -Path $testDir -Force | Out-Null

# 创建.env文件
$newEnvContent = @"
BOT_TOKEN=$botToken
DB_PATH=data\simple_test.db
CLIENT_NAME=simple_test
TIMEZONE=Asia/Ho_Chi_Minh
"@

$newEnvContent | Out-File -FilePath "$testDir\.env" -Encoding UTF8
Write-Host "✅ 创建测试配置: $testDir\.env" -ForegroundColor Green

# 4. 确保目录存在
if (-not (Test-Path "data")) {
    New-Item -ItemType Directory -Path "data" -Force | Out-Null
    Write-Host "✅ 创建data目录" -ForegroundColor Green
}

if (-not (Test-Path "logs")) {
    New-Item -ItemType Directory -Path "logs" -Force | Out-Null
    Write-Host "✅ 创建logs目录" -ForegroundColor Green
}

# 5. 显示测试命令
Write-Host "`n🚀 测试命令:" -ForegroundColor Cyan
Write-Host "python src\app\main.py --config-dir $testDir" -ForegroundColor Yellow

Write-Host "`n📋 验证步骤:" -ForegroundColor Cyan
Write-Host "1. 运行上面的命令" -ForegroundColor Gray
Write-Host "2. 观察启动日志" -ForegroundColor Gray
Write-Host "3. 在Telegram中测试Bot" -ForegroundColor Gray
Write-Host "4. 按Ctrl+C停止" -ForegroundColor Gray

Write-Host "`n✅ 完成！现在可以测试了。" -ForegroundColor Green