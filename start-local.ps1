Write-Host "Starting Horse Betting App locally..." -ForegroundColor Green
Write-Host ""

# Check if Python is available
try {
    $pythonPath = "C:\Users\ITServiceDesk\AppData\Local\Programs\Python\Python313\python.exe"
    if (Test-Path $pythonPath) {
        Write-Host "✓ Python found at: $pythonPath" -ForegroundColor Green
    } else {
        Write-Host "✗ Python not found at expected path. Please update the script." -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "✗ Python not found. Please install Python and update the script path." -ForegroundColor Red
    exit 1
}

# Check if Node.js is available
try {
    node --version | Out-Null
    Write-Host "✓ Node.js found" -ForegroundColor Green
} catch {
    Write-Host "✗ Node.js not found. Please install Node.js and add it to PATH." -ForegroundColor Red
    exit 1
}

# Check if npm is available
try {
    npm --version | Out-Null
    Write-Host "✓ npm found" -ForegroundColor Green
} catch {
    Write-Host "✗ npm not found. Please install Node.js and add it to PATH." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Starting Backend Server..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot'; & '$pythonPath' server.py"

Write-Host "Waiting for backend to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

Write-Host "Starting Frontend..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\horse-betting-frontend'; npm start"

Write-Host ""
Write-Host "Both servers are starting..." -ForegroundColor Green
Write-Host "Backend: http://localhost:5000" -ForegroundColor Cyan
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press any key to close this window..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") 