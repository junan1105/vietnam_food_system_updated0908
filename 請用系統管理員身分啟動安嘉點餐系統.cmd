@echo off
setlocal
set "PROJECT=C:\Users\tuana\Documents\Codex\2026-07-21\new-chat\outputs\vietnam_food_system_updated"

echo.
echo 正在要求 Windows 系統管理員權限，請在跳出的視窗按「是」。
powershell.exe -NoProfile -ExecutionPolicy Bypass -Command "Start-Process PowerShell.exe -Verb RunAs -ArgumentList '-NoProfile -ExecutionPolicy Bypass -File ""%PROJECT%\管理員重新啟動安嘉點餐系統.ps1""'"

echo.
echo 已送出啟動要求。請等待約 5 秒後，重新整理 order.angiavietnam.com。
pause
