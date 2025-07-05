Write-Host "Starting Telegram Reminder Bot..." -ForegroundColor Green
Write-Host ""
Write-Host "Make sure you have set your TELEGRAM_BOT_TOKEN environment variable" -ForegroundColor Yellow
Write-Host "or the bot will use the default token from the code." -ForegroundColor Yellow
Write-Host ""
Write-Host "Press Ctrl+C to stop the bot" -ForegroundColor Cyan
Write-Host ""

# Kill any existing Python processes that might be running the bot
try {
    Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
    Write-Host "Stopped existing Python processes" -ForegroundColor Yellow
    Start-Sleep -Seconds 2
} catch {
    Write-Host "No existing Python processes found" -ForegroundColor Gray
}

# Run the bot
try {
    .\.venv\Scripts\python.exe main.py
} catch {
    Write-Host "Error running the bot: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "Bot stopped. Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") 