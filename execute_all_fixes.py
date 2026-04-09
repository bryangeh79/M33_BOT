#!/usr/bin/env python3
"""
执行所有修复和测试
"""

import os
import sys
import subprocess
import time
from pathlib import Path

print("=" * 60)
print("M33 Lotto Bot - 执行所有修复和测试")
print("=" * 60)

# 设置工作目录
workspace = "C:\\AI_WORKSPACE\\M33-Lotto-Bot-VN"
print(f"工作目录: {workspace}")

# 由于我在沙箱中，无法直接访问Windows路径
# 我将创建修复脚本供你在Windows上运行

# 创建完整的修复和测试脚本
fix_script = '''# M33 Lotto Bot - 完整修复和测试脚本
# 在PowerShell中运行此脚本

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "M33 Lotto Bot 完整修复和测试" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# 1. 设置工作目录
$workspace = "C:\\AI_WORKSPACE\\M33-Lotto-Bot-VN"
Set-Location $workspace
Write-Host "工作目录: $(Get-Location)" -ForegroundColor Green

# 2. 设置Python环境
$env:PYTHONPATH = $workspace
Write-Host "设置PYTHONPATH: $env:PYTHONPATH" -ForegroundColor Green

# 3. 检查Bot 2配置
Write-Host "`n检查Bot 2配置..." -ForegroundColor Yellow
$bot2Config = "test_bot2_fix"
if (-not (Test-Path "$bot2Config\\.env")) {
    Write-Host "创建Bot 2配置..." -ForegroundColor Gray
    New-Item -ItemType Directory -Path $bot2Config -Force | Out-Null
    
    @"
BOT_TOKEN=8226064460:AAH1dCFD6jmzz-fa3KPbBmdJvvuZtxhH9FM
DB_PATH=data\\test_bot2_fix.db
CLIENT_NAME=test_bot2_fix
TIMEZONE=Asia/Ho_Chi_Minh
DEFAULT_ADMIN_USER_IDS=2063305617,6577170044
"@ | Out-File -FilePath "$bot2Config\\.env" -Encoding UTF8
    
    Write-Host "✅ 创建Bot 2配置" -ForegroundColor Green
} else {
    Write-Host "✅ Bot 2配置已存在" -ForegroundColor Green
}

# 4. 检查Bot 1配置
Write-Host "`n检查Bot 1配置..." -ForegroundColor Yellow
$bot1Config = "simple_test"
if (-not (Test-Path "$bot1Config\\.env")) {
    Write-Host "创建Bot 1配置..." -ForegroundColor Gray
    New-Item -ItemType Directory -Path $bot1Config -Force | Out-Null
    
    @"
BOT_TOKEN=8713226156:AAGDHv1xd-lObWy7yAt_It7EBL3q225HMuw
DB_PATH=data\\simple_test.db
CLIENT_NAME=simple_test
TIMEZONE=Asia/Ho_Chi_Minh
DEFAULT_ADMIN_USER_IDS=2063305617,6577170044
"@ | Out-File -FilePath "$bot1Config\\.env" -Encoding UTF8
    
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
    }
}

# 6. 验证Token
Write-Host "`n验证Bot 2 Token..." -ForegroundColor Yellow
$tokenCheck = @"
import requests
import sys

token = "8226064460:AAH1dCFD6jmzz-fa3KPbBmdJvvuZtxhH9FM"
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
            sys.exit(0)
        else:
            print(f"❌ API错误: {data.get('description')}")
            sys.exit(1)
    else:
        print(f"❌ HTTP错误: {response.status_code}")
        sys.exit(1)
        
except Exception as e:
    print(f"❌ 错误: {e}")
    sys.exit(1)
"@

$tokenCheck | Out-File -FilePath "check_token.py" -Encoding UTF8
python check_token.py
$tokenValid = $LASTEXITCODE -eq 0
Remove-Item -FilePath "check_token.py" -Force

if (-not $tokenValid) {
    Write-Host "❌ Bot 2 Token无效，请检查" -ForegroundColor Red
    exit 1
}

# 7. 测试启动Bot 2
Write-Host "`n测试启动Bot 2..." -ForegroundColor Yellow
Write-Host "命令: python src\\app\\main.py --config-dir $bot2Config" -ForegroundColor Gray
Write-Host "按Ctrl+C停止测试" -ForegroundColor Yellow
Write-Host "-" * 50 -ForegroundColor Gray

# 创建测试脚本
$testScript = @'
import sys
import os
import threading
import time

# 设置环境
workspace = "C:\\\\AI_WORKSPACE\\\\M33-Lotto-Bot-VN"
os.environ["PYTHONPATH"] = workspace
sys.path.insert(0, workspace)

# 导入main
from src.app.main import main

# 设置参数
sys.argv = ["main.py", "--config-dir", "test_bot2_fix"]

print("启动Bot 2测试...")
try:
    # 在新线程中运行main
    def run_bot():
        try:
            main()
        except KeyboardInterrupt:
            print("Bot停止")
        except Exception as e:
            print(f"Bot错误: {e}")
    
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    # 等待启动
    print("等待Bot启动...")
    time.sleep(10)
    
    print("✅ Bot 2启动测试完成")
    print("现在可以在Telegram中测试Bot 2")
    print("按Ctrl+C停止")
    
    # 保持运行
    while True:
        time.sleep(1)
        
except KeyboardInterrupt:
    print("测试停止")
except Exception as e:
    print(f"测试错误: {e}")
'@

$testScript | Out-File -FilePath "test_bot2.py" -Encoding UTF8

Write-Host "`n运行测试脚本..." -ForegroundColor Cyan
Write-Host "如果看到'Starting polling ...'表示成功" -ForegroundColor Gray
Write-Host "在Telegram中给Bot 2发送/start测试" -ForegroundColor Gray
Write-Host "按Ctrl+C停止测试" -ForegroundColor Yellow

python test_bot2.py

# 清理
Remove-Item -FilePath "test_bot2.py" -Force -ErrorAction SilentlyContinue

Write-Host "`n==========================================" -ForegroundColor Cyan
Write-Host "测试完成！" -ForegroundColor Cyan
Write-Host "如果Bot 2响应，多租户测试成功！" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Cyan
'''

# 保存脚本
script_path = "complete_fix_and_test.ps1"
with open(script_path, "w", encoding="utf-8") as f:
    f.write(fix_script)

print(f"✅ 创建完整修复脚本: {script_path}")
print()
print("🎯 下一步：")
print("1. 在Windows PowerShell中运行此脚本")
print("2. 脚本会自动：")
print("   - 设置Python环境")
print("   - 检查/创建Bot配置")
print("   - 验证Token有效性")
print("   - 启动Bot 2测试")
print("3. 在Telegram中测试Bot 2响应")
print()
print("🚀 运行命令:")
print(f"cd C:\\AI_WORKSPACE\\M33-Lotto-Bot-VN")
print(f".\\{script_path}")
print()
print("📋 测试成功标志:")
print("- Bot 2启动无错误")
print("- 显示'Starting polling ...'")
print("- Telegram中Bot 2响应命令")
print("- 两个Bot可以独立运行")

# 同时创建简化的测试命令
simple_cmds = '''# 简化测试命令
cd C:\\AI_WORKSPACE\\M33-Lotto-Bot-VN
$env:PYTHONPATH = "C:\\AI_WORKSPACE\\M33-Lotto-Bot-VN"
python src\\app\\main.py --config-dir test_bot2_fix
'''

with open("simple_test_cmd.txt", "w", encoding="utf-8") as f:
    f.write(simple_cmds)

print(f"\n✅ 也创建了简化命令: simple_test_cmd.txt")
print("=" * 60)