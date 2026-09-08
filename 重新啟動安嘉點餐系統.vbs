' 雙擊此檔案即可停止目前佔用 5000 埠的網站，再於背景啟動最新版本。
Option Explicit

Dim shell, projectFolder, pythonwPath, command
Set shell = CreateObject("WScript.Shell")
projectFolder = "C:\Users\tuana\Documents\Codex\2026-07-21\new-chat\outputs\vietnam_food_system_updated"
pythonwPath = projectFolder & "\.venv\Scripts\pythonw.exe"

command = "powershell.exe -NoProfile -WindowStyle Hidden -Command " & Chr(34) & _
  "$listener = Get-NetTCPConnection -LocalPort 5000 -State Listen -ErrorAction SilentlyContinue; " & _
  "if ($listener) { taskkill.exe /PID $listener.OwningProcess /T /F | Out-Null }; " & _
  "Start-Sleep -Seconds 1; " & _
  "Start-Process -FilePath '" & pythonwPath & "' -ArgumentList '""" & projectFolder & "\app.py"""' -WorkingDirectory '" & projectFolder & "' -WindowStyle Hidden" & Chr(34)

shell.Run command, 0, False
