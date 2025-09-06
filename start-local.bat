@echo off
echo Starting Horse Betting App locally...
echo.

echo Setting up environment variables...
set GCS_BUCKET_NAME=horse-betting-data-123
set GOOGLE_CLOUD_PROJECT=horse-betting-app-123
set GOOGLE_APPLICATION_CREDENTIALS=service-account-key.json
echo Environment variables set

echo Starting Backend Server...
start "Backend Server" cmd /k "cd /d %~dp0 && set GCS_BUCKET_NAME=horse-betting-data-123 && set GOOGLE_CLOUD_PROJECT=horse-betting-app-123 && set GOOGLE_APPLICATION_CREDENTIALS=service-account-key.json && python server.py"

echo Waiting for backend to start...
timeout /t 3 /nobreak >nul

echo Starting Frontend...
start "Frontend" cmd /k "cd /d %~dp0\horse-betting-frontend && npm start"

echo.
echo Both servers are starting...
echo Backend: http://localhost:5000
echo Frontend: http://localhost:3000
echo.
echo Press any key to close this window...
pause >nul 