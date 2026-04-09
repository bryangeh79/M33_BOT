# M33 Lotto Bot 测试启动脚本

Write-Host "启动M33 Lotto Bot测试..." -ForegroundColor Cyan
Write-Host "工作目录: C:\AI_WORKSPACE\M33-Lotto-Bot-VN" -ForegroundColor Gray

# 切换到项目目录
Set-Location "C:\AI_WORKSPACE\M33-Lotto-Bot-VN"

# 检查目录
Write-Host "`n检查项目结构..." -ForegroundColor Yellow
if (-not (Test-Path "src")) {
    Write-Host "❌ 错误: 未找到src目录" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path "src\app\main.py")) {
    Write-Host "❌ 错误: 未找到main.py" -ForegroundColor Red
    exit 1
}

Write-Host "✅ 项目结构正常" -ForegroundColor Green

# 检查测试配置
Write-Host "`n检查测试配置..." -ForegroundColor Yellow
$testDir = "simple_test"
if (-not (Test-Path $testDir)) {
    Write-Host "❌ 错误: 未找到测试配置目录" -ForegroundColor Red
    Write-Host "请先创建测试配置: mkdir simple_test" -ForegroundColor Yellow
    exit 1
}

if (-not (Test-Path "$testDir\.env")) {
    Write-Host "❌ 错误: 未找到.env文件" -ForegroundColor Red
    Write-Host "请在$testDir目录创建.env文件" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ 测试配置正常" -ForegroundColor Green

# 设置Python路径
Write-Host "`n设置Python环境..." -ForegroundColor Yellow
$env:PYTHONPATH = "C:\AI_WORKSPACE\M33-Lotto-Bot-VN"
Write-Host "✅ 设置PYTHONPATH: $env:PYTHONPATH" -ForegroundColor Green

# 检查Python依赖
Write-Host "`n检查Python依赖..." -ForegroundColor Yellow
try {
    $result = python -c "import telegram; import dotenv; print('✅ 依赖检查通过')" 2>&1
    Write-Host $result -ForegroundColor Green
} catch {
    Write-Host "⚠ 依赖可能未安装" -ForegroundColor Yellow
    Write-Host "运行: pip install python-telegram-bot python-dotenv" -ForegroundColor Gray
}

# 启动Bot
Write-Host "`n🚀 启动Bot..." -ForegroundColor Cyan
Write-Host "命令: python src\app\main.py --config-dir $testDir" -ForegroundColor Gray
Write-Host "按 Ctrl+C 停止" -ForegroundColor Yellow
Write-Host "-" * 50 -ForegroundColor Gray

try {
    python src\app\main.py --config-dir $testDir
} catch {
    Write-Host "❌ 启动失败: $_" -ForegroundColor Red
}

Write-Host "`n测试完成。" -ForegroundColor Cyan