# Start Flask API backend
Write-Host "Starting Flask API on http://localhost:5000 ..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList '-NoExit', '-Command', 'cd e:\hca_project_1\api; python app.py'

# Give Flask a moment to initialize
Start-Sleep -Seconds 2

# Start React frontend
Write-Host "Starting React frontend on http://localhost:5173 ..." -ForegroundColor Green
Set-Location e:\hca_project_1\frontend
npm run dev
