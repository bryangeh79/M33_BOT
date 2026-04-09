# Bot 2诊断脚本

Write-Host "Diagnosing Bot 2 issues..." -ForegroundColor Cyan
Write-Host "=" * 50 -ForegroundColor Gray

# 1. 检查配置
Write-Host "`n1. Checking Bot 2 configuration..." -ForegroundColor Yellow
if (Test-Path "real_client_02\.env") {
    $envContent = Get-Content "real_client_02\.env" -Raw
    Write-Host "OK Config file exists" -ForegroundColor Green
    
    # 提取Token
    $tokenLine = $envContent -split "`n" | Where-Object { $_ -match "^BOT_TOKEN=" } | Select-Object -First 1
    if ($tokenLine) {
        $token = $tokenLine -replace "^BOT_TOKEN=", ""
        $token = $token.Trim()
        Write-Host "OK Token found: $($token.Substring(0, [Math]::Min(20, $token.Length)))..." -ForegroundColor Green
    } else {
        Write-Host "ERROR: No BOT_TOKEN found in .env" -ForegroundColor Red
    }
} else {
    Write-Host "ERROR: Config file not found" -ForegroundColor Red
}

# 2. 检查数据库文件
Write-Host "`n2. Checking database..." -ForegroundColor Yellow
if (Test-Path "data\real_client_02.db") {
    $dbSize = (Get-Item "data\real_client_02.db").Length
    Write-Host "OK Database exists: $dbSize bytes" -ForegroundColor Green
} else {
    Write-Host "WARNING: Database not created yet" -ForegroundColor Yellow
}

# 3. 检查日志
Write-Host "`n3. Checking logs..." -ForegroundColor Yellow
if (Test-Path "logs") {
    $logFiles = Get-ChildItem "logs\*real_client_02*" -ErrorAction SilentlyContinue
    if ($logFiles) {
        Write-Host "OK Log files found:" -ForegroundColor Green
        $logFiles | ForEach-Object { Write-Host "  - $($_.Name)" -ForegroundColor Gray }
    } else {
        Write-Host "WARNING: No log files for Bot 2" -ForegroundColor Yellow
    }
} else {
    Write-Host "WARNING: Logs directory not found" -ForegroundColor Yellow
}

# 4. 测试Telegram API
Write-Host "`n4. Testing Telegram API connection..." -ForegroundColor Yellow
try {
    # 创建测试脚本
    $testScript = @'
import requests
import sys

token = "8226064460:AAH1dCFD6jmzz-fa3KPbBmdJvvuZtxhH9FM"
url = f"https://api.telegram.org/bot{token}/getMe"

try:
    print(f"Testing token: {token[:15]}...")
    response = requests.get(url, timeout=10)
    
    if response.status_code == 200:
        data = response.json()
        if data.get("ok"):
            bot_info = data.get("result", {})
            print(f"SUCCESS: Bot is active")
            print(f"  Bot ID: {bot_info.get('id')}")
            print(f"  Username: @{bot_info.get('username')}")
            print(f"  Name: {bot_info.get('first_name')}")
        else:
            print(f"ERROR: API returned not OK: {data}")
    else:
        print(f"ERROR: HTTP {response.status_code}")
        print(f"Response: {response.text}")
        
except requests.exceptions.ConnectionError:
    print("ERROR: Cannot connect to Telegram API")
    print("Check your internet connection")
except Exception as e:
    print(f"ERROR: {e}")
'@
    
    $testScript | Out-File -FilePath "test_api.py" -Encoding UTF8
    python test_api.py
    Remove-Item -FilePath "test_api.py" -Force
    
} catch {
    Write-Host "ERROR: Failed to test API" -ForegroundColor Red
}

# 5. 建议
Write-Host "`n5. Troubleshooting suggestions:" -ForegroundColor Cyan
Write-Host "  A. Check Bot privacy settings in @BotFather:" -ForegroundColor Gray
Write-Host "     /mybots -> Select Bot -> Bot Settings -> Group Privacy -> DISABLED" -ForegroundColor Gray

Write-Host "`n  B. Send a message to the Bot and check:" -ForegroundColor Gray
Write-Host "     1. Open Telegram" -ForegroundColor Gray
Write-Host "     2. Search for your new Bot" -ForegroundColor Gray
Write-Host "     3. Send /start" -ForegroundColor Gray
Write-Host "     4. Check Bot 2 console for logs" -ForegroundColor Gray

Write-Host "`n  C. Restart Bot 2:" -ForegroundColor Gray
Write-Host "     Press Ctrl+C to stop" -ForegroundColor Gray
Write-Host "     Then run: python src\app\main.py --config-dir real_client_02" -ForegroundColor Gray

Write-Host "`n  D. Check if Bot 1 is interfering:" -ForegroundColor Gray
Write-Host "     Make sure only one instance per Token is running" -ForegroundColor Gray

Write-Host "`n=" * 50 -ForegroundColor Gray
Write-Host "Run this diagnosis and share the results." -ForegroundColor Cyan