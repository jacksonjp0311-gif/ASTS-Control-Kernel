# Local verification for ASTS Control Kernel.
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

Write-Host "ASTS / test"
Write-Host "-----------"

& python -m unittest discover -s tests -v
if ($LASTEXITCODE -ne 0) { throw "unittest failed" }

Write-Host ""
Write-Host "[OK] ASTS unit + session smoke"
