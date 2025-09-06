# Setup Google Cloud Storage Environment Variables for Lekours
Write-Host "Setting up Google Cloud Storage environment..." -ForegroundColor Green

# Set environment variables for current session
$env:GOOGLE_CLOUD_PROJECT = "horse-betting-app-123"
$env:GCS_BUCKET_NAME = "horse-betting-data-123"  # You may need to change this to your actual bucket name
$env:GOOGLE_APPLICATION_CREDENTIALS = "service-account-key.json"

Write-Host "Environment variables set:" -ForegroundColor Yellow
Write-Host "GOOGLE_CLOUD_PROJECT: $env:GOOGLE_CLOUD_PROJECT" -ForegroundColor Cyan
Write-Host "GCS_BUCKET_NAME: $env:GCS_BUCKET_NAME" -ForegroundColor Cyan
Write-Host "GOOGLE_APPLICATION_CREDENTIALS: $env:GOOGLE_APPLICATION_CREDENTIALS" -ForegroundColor Cyan

Write-Host "`nTo make these permanent, add them to your system environment variables or .env file" -ForegroundColor Yellow
Write-Host "Starting the server..." -ForegroundColor Green

# Start the Flask server with the environment set
python server.py

