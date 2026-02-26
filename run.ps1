$ErrorActionPreference = "Stop"
Set-Location (Split-Path -Parent $MyInvocation.MyCommand.Path)

Write-Host ""
Write-Host "Launching ASTS Kernel..." -ForegroundColor Cyan
Write-Host ""

python main.py

Write-Host ""
Write-Host "ASTS COMPLETE" -ForegroundColor Green
