param(
    [ValidateSet("Debug", "Release")]
    [string]$Configuration = "Debug"
)

$ErrorActionPreference = "Stop"

$solution = Join-Path $PSScriptRoot "BlinkReminder.Native.sln"

Write-Host "Restoring NuGet packages..." -ForegroundColor Cyan
dotnet restore $solution

Write-Host "Building $Configuration x64..." -ForegroundColor Cyan
dotnet build $solution -c $Configuration -p:Platform=x64

Write-Host "Done." -ForegroundColor Green
