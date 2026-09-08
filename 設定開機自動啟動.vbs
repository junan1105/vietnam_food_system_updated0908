' 只需執行一次：登入 Windows 後自動在背景啟動點餐系統。
Option Explicit

Dim shell, projectFolder, launcherPath
Set shell = CreateObject("WScript.Shell")
projectFolder = "C:\Users\tuana\Documents\Codex\2026-07-21\new-chat\outputs\vietnam_food_system_updated"
launcherPath = projectFolder & "\啟動安嘉點餐系統.vbs"

shell.RegWrite "HKCU\Software\Microsoft\Windows\CurrentVersion\Run\AnGiaVietnamFood", Chr(34) & launcherPath & Chr(34), "REG_SZ"
MsgBox "已設定：登入 Windows 後將自動在背景啟動安嘉點餐系統。", 64, "安嘉點餐系統"
