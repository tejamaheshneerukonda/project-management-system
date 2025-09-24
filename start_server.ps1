Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Django Server with WebSocket Support" -ForegroundColor Cyan  
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Stopping any existing servers on port 8080..." -ForegroundColor Yellow
$processes = Get-NetTCPConnection -LocalPort 8080 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess
if ($processes) {
    foreach ($pid in $processes) {
        try {
            Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
            Write-Host "Killed process $pid" -ForegroundColor Green
        } catch {
            Write-Host "Could not kill process $pid" -ForegroundColor Red
        }
    }
} else {
    Write-Host "No processes found on port 8080" -ForegroundColor Green
}

Write-Host ""
Write-Host "Starting Django server with WebSocket support..." -ForegroundColor Yellow
Write-Host ""

python manage.py runserver_websocket --reload
