$ErrorActionPreference = 'Stop'

$root = $PSScriptRoot
$output = Join-Path $root 'video-output'
$ffmpeg = 'C:\ffmpeg\bin\ffmpeg.exe'

if (-not (Test-Path -LiteralPath $ffmpeg)) {
    Write-Host 'FFmpeg was not found at C:\ffmpeg\bin\ffmpeg.exe.' -ForegroundColor Yellow
    Read-Host 'Press Enter to exit'
    exit 1
}

function Render-Video([string]$variant, [string]$fileName) {
    $frames = Join-Path $output $variant
    $target = Join-Path $output $fileName
    & $ffmpeg -y -framerate '1/10' -start_number 1 -i (Join-Path $frames 'scene-%02d.png') -c:v libx264 -pix_fmt yuv420p -r 30 -movflags +faststart $target
    if ($LASTEXITCODE -ne 0) { throw "Video render failed: $fileName" }
    Write-Host "Created: $target" -ForegroundColor Green
}

Render-Video 'landscape' 'an-gia-ordering-3min-landscape.mp4'
Render-Video 'portrait' 'an-gia-ordering-3min-portrait.mp4'
Read-Host 'Both MP4 videos are ready. Press Enter to exit'
