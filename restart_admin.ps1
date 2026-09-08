$projectFolder = Split-Path -Parent $MyInvocation.MyCommand.Path
$pythonwPath = Join-Path $projectFolder ".venv\Scripts\pythonw.exe"
$userApiKey = [Environment]::GetEnvironmentVariable("OPENAI_API_KEY", "User")
if ($userApiKey) { $env:OPENAI_API_KEY = $userApiKey }

$listeners = Get-NetTCPConnection -LocalPort 5000 -State Listen -ErrorAction SilentlyContinue
foreach ($listener in $listeners) {
    Stop-Process -Id $listener.OwningProcess -Force -ErrorAction SilentlyContinue
}

Start-Sleep -Seconds 2
Start-Process -FilePath $pythonwPath -ArgumentList "$projectFolder\app.py" -WorkingDirectory $projectFolder -WindowStyle Hidden
