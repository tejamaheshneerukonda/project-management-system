@echo off
echo ========================================
echo  Simple Django Server with WebSockets
echo ========================================
echo.
echo This will start your Django server with WebSocket support.
echo Much simpler than using Daphne manually!
echo.
echo Stopping any existing servers...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8080') do (
    echo Stopping process %%a
    taskkill /PID %%a /F >nul 2>&1
)
echo.
echo Starting server with WebSocket support...
echo.
echo ✅ Server will be available at: http://127.0.0.1:8080
echo ✅ WebSocket will work at: ws://127.0.0.1:8080/ws/chat/room/ROOM_ID/
echo.
echo Press Ctrl+C to stop the server
echo.
daphne -b 127.0.0.1 -p 8080 project_manager.asgi:application
