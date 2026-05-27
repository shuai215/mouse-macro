@echo off
echo =================================
echo   Mouse Macro Launcher
echo =================================
echo.
echo [Y] Run as Administrator (recommended for games)
echo [N] Normal launch
echo.

choice /c YN /m "Enter Y or N"
if errorlevel 2 goto normal
if errorlevel 1 goto admin

:admin
echo.
echo Launching with admin rights...
powershell -Command "Start-Process -FilePath 'D:\python\envs\mouse-macro\python.exe' -ArgumentList '-m mouse_macro.app' -Verb RunAs"
exit

:normal
echo.
echo Normal launch...
D:\python\envs\mouse-macro\python.exe -m mouse_macro.app
exit
