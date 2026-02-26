$ErrorActionPreference = "Stop"
$ROOT = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ROOT

Write-Host ""
Write-Host "ASTS ALL-IN-ONE" -ForegroundColor Cyan
Write-Host "Root: $ROOT" -ForegroundColor DarkGray
Write-Host ""

if (!(Test-Path ".\main.py")) {
    Write-Host "Missing main.py — run the entrypoint lock script first." -ForegroundColor Red
    exit 1
}
python main.py
