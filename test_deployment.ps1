# Script de test automatisé - LOCAL / DOCKER / AZURE
# Usage: .\test_deployment.ps1 -Environment "local|docker|azure"

param(
    [ValidateSet("local", "docker", "azure")]
    [string]$Environment = "local"
)

$endpoints = @{
    "local"  = "http://127.0.0.1:5000"
    "docker" = "http://localhost:5000"
    "azure"  = "https://yolov11-app.azurewebsites.net"
}

$endpoint = $endpoints[$Environment]

Write-Host "TEST DEPLOYMENT - $($Environment.ToUpper())" -ForegroundColor Cyan
Write-Host ""

# Health Check
Write-Host "1. Health Check..." -ForegroundColor Yellow
try {
    $health = Invoke-WebRequest -Uri "$endpoint/api/health" -Method GET -TimeoutSec 30
    Write-Host "OK - Status: $($health.StatusCode)" -ForegroundColor Green
}
catch {
    Write-Host "FAILED: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Test Inference
Write-Host "2. Test Inference..." -ForegroundColor Yellow

$imagePath = "test/images/04_JPG.rf.4935d8061ad1c13154d00829b507412c.jpg"

if (Test-Path $imagePath) {
    try {
        $form = @{
            image = Get-Item -Path $imagePath
            confidence = 0.5
        }
        
        $response = Invoke-WebRequest -Uri "$endpoint/api/predict" -Method POST -Form $form -TimeoutSec 60
        $data = $response.Content | ConvertFrom-Json
        
        Write-Host "OK - Status: $($response.StatusCode)" -ForegroundColor Green
        Write-Host "  Void Rate: $($data.result.void_rate)%" -ForegroundColor Cyan
        Write-Host "  Chip Area: $($data.result.chip_area) pixels" -ForegroundColor Cyan
        Write-Host "  Holes Area: $($data.result.holes_area) pixels" -ForegroundColor Cyan
    }
    catch {
        Write-Host "FAILED: $_" -ForegroundColor Red
        exit 1
    }
}
else {
    Write-Host "Image not found: $imagePath" -ForegroundColor Red
}

Write-Host ""
Write-Host "TEST COMPLETED SUCCESSFULLY" -ForegroundColor Green
Write-Host "URL: $endpoint" -ForegroundColor Cyan
