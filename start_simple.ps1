Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Simple Django Server with WebSockets" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "This will start your Django server with WebSocket support." -ForegroundColor Yellow
Write-Host "Much simpler than using Daphne manually!" -ForegroundColor Yellow
Write-Host ""

Write-Host "Stopping any existing servers..." -ForegroundColor Yellow
$processes = Get-NetTCPConnection -LocalPort 8080 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess
if ($processes) {
    foreach ($pid in $processes) {
        try {
            Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
            Write-Host "Stopped process $pid" -ForegroundColor Green
        } catch {
            Write-Host "Could not stop process $pid" -ForegroundColor Red
        }
    }
} else {
    Write-Host "No processes found on port 8080" -ForegroundColor Green
}

Write-Host ""
Write-Host "Starting server with WebSocket support..." -ForegroundColor Yellow
Write-Host ""
Write-Host "✅ Server will be available at: http://127.0.0.1:8080" -ForegroundColor Green
Write-Host "✅ WebSocket will work at: ws://127.0.0.1:8080/ws/chat/room/ROOM_ID/" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Cyan
Write-Host ""

daphne -b 127.0.0.1 -p 8080 project_manager.asgi:application
