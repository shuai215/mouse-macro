Write-Host "================================="
Write-Host "  Mouse Macro Launcher"
Write-Host "================================="
Write-Host ""
Write-Host "[Y] Run as Administrator (recommended for games)"
Write-Host "[N] Normal launch"
Write-Host ""

$choice = Read-Host "Enter Y or N"

if ($choice -eq "Y" -or $choice -eq "y") {
    Write-Host "Launching with admin rights..."
    Start-Process -FilePath "D:\python\envs\mouse-macro\python.exe" -ArgumentList "-m mouse_macro.app" -Verb RunAs
} else {
    Write-Host "Normal launch..."
    & D:\python\envs\mouse-macro\python.exe -m mouse_macro.app
}
