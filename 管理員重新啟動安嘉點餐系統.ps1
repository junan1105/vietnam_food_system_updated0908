$projectFolder = "C:\Users\tuana\Documents\Codex\2026-07-21\new-chat\outputs\vietnam_food_system_updated"
$pythonwPath = Join-Path $projectFolder ".venv\Scripts\pythonw.exe"

# 關閉目前佔用 Flask 連接埠的舊版程式。
$listeners = Get-NetTCPConnection -LocalPort 5000 -State Listen -ErrorAction SilentlyContinue
foreach ($listener in $listeners) {
    Stop-Process -Id $listener.OwningProcess -Force -ErrorAction SilentlyContinue
}

Start-Sleep -Seconds 2
Start-Process -FilePath $pythonwPath -ArgumentList "`"$projectFolder\app.py`"" -WorkingDirectory $projectFolder -WindowStyle Hidden
