# Launch Bot 2
Write-Host "Starting Bot 2..." -ForegroundColor Cyan
Write-Host "Token: 8226064460:AAH1dCFD6jmzz-fa3KPbBmdJvvuZtxhH9FM" -ForegroundColor Gray
Write-Host "Database: data\real_client_02.db" -ForegroundColor Gray
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host "-" * 50 -ForegroundColor Gray

$env:PYTHONPATH = "C:\AI_WORKSPACE\M33-Lotto-Bot-VN"
python src\app\main.py --config-dir real_client_02
