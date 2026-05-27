# Build mouse-macro into a single exe and zip it for GitHub release.
# Usage: powershell -ExecutionPolicy Bypass -File build.ps1

$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$DistDir = Join-Path $ProjectRoot "dist"
$ExeName = "mouse-macro.exe"
$ZipName = "mouse-macro.zip"

Write-Host "=== Cleaning previous build ==="
Remove-Item -Recurse -Force (Join-Path $ProjectRoot "build") -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force $DistDir -ErrorAction SilentlyContinue
Remove-Item -Force (Join-Path $ProjectRoot $ZipName) -ErrorAction SilentlyContinue

Write-Host "=== Running PyInstaller ==="
$ParentDir = Split-Path $ProjectRoot -Parent
conda run -n mouse-macro pyinstaller `
    --onefile `
    --windowed `
    --name "mouse-macro" `
    --paths "$ParentDir" `
    --hidden-import "pynput.keyboard._win32" `
    --hidden-import "pynput.mouse._win32" `
    --distpath $DistDir `
    --workpath (Join-Path $ProjectRoot "build") `
    (Join-Path $ProjectRoot "app.py")

if (-not (Test-Path (Join-Path $DistDir $ExeName))) {
    Write-Error "Build failed: exe not found"
    exit 1
}

Start-Sleep -Seconds 2
Write-Host "=== Creating ZIP ==="
Compress-Archive -Path (Join-Path $DistDir $ExeName) -DestinationPath (Join-Path $ProjectRoot $ZipName)

$ExeSize = [math]::Round((Get-Item (Join-Path $DistDir $ExeName)).Length / 1MB, 1)
$ZipSize = [math]::Round((Get-Item (Join-Path $ProjectRoot $ZipName)).Length / 1MB, 1)

Write-Host "=== Done ==="
Write-Host "exe : $DistDir\$ExeName ($ExeSize MB)"
Write-Host "zip : $ProjectRoot\$ZipName ($ZipSize MB)"
