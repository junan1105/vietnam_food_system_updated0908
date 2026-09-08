@echo off
echo Requesting Windows administrator permission...
powershell.exe -NoProfile -Command "Start-Process -Verb RunAs -FilePath powershell.exe -ArgumentList '-NoProfile -ExecutionPolicy Bypass -File %~dp0restart_admin.ps1' -Wait"
echo.
echo Done. Wait 5 seconds, then refresh https://order.angiavietnam.com/
pause
