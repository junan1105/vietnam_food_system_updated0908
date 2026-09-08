' 雙擊此檔案即可在背景啟動 Flask；不會顯示命令提示字元視窗。
Option Explicit

Dim shell, projectFolder, pythonwPath, command
Set shell = CreateObject("WScript.Shell")
projectFolder = "C:\Users\tuana\Documents\Codex\2026-07-21\new-chat\outputs\vietnam_food_system_updated"
pythonwPath = projectFolder & "\.venv\Scripts\pythonw.exe"

shell.CurrentDirectory = projectFolder
command = Chr(34) & pythonwPath & Chr(34) & " " & Chr(34) & projectFolder & "\app.py" & Chr(34)
shell.Run command, 0, False
