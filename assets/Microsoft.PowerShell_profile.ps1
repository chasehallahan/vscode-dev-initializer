if ($env:VIRTUAL_ENV) {
    Write-Host "Virtual environment ACTIVE" -ForegroundColor Green
}
else {
    Write-Host "NO virtual environment active" -ForegroundColor Yellow
}
