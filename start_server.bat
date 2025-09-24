@echo off
echo ========================================
echo  Django Server with WebSocket Support
echo ========================================
echo.
echo Stopping any existing servers on port 8080...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8080') do (
    echo Killing process %%a
    taskkill /PID %%a /F >nul 2>&1
)
echo.
echo Starting Django server with WebSocket support...
echo.
python manage.py runserver_websocket --reload
