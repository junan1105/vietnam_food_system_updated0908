Option Explicit

Dim shell, projectFolder, scriptPath
Set shell = CreateObject("Shell.Application")
projectFolder = "C:\Users\tuana\Documents\Codex\2026-07-21\new-chat\outputs\vietnam_food_system_updated"
scriptPath = projectFolder & "\管理員重新啟動安嘉點餐系統.ps1"

' 以管理員權限停止舊版 5000 連接埠，再背景啟動目前專案。
shell.ShellExecute "powershell.exe", "-NoProfile -ExecutionPolicy Bypass -File """ & scriptPath & """", "", "runas", 0
