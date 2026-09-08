$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$output = Join-Path $root 'video-output'
$ffmpeg = (Get-Command ffmpeg.exe -ErrorAction SilentlyContinue).Source

if (-not $ffmpeg) {
    $fallback = 'C:\ffmpeg\bin\ffmpeg.exe'
    if (Test-Path -LiteralPath $fallback) { $ffmpeg = $fallback }
}
if (-not $ffmpeg) {
    Write-Host '找不到 ffmpeg.exe。請先將 FFmpeg 解壓縮到 C:\ffmpeg，讓檔案位於 C:\ffmpeg\bin\ffmpeg.exe。' -ForegroundColor Yellow
    Write-Host '完成後，再按兩下本檔案即可輸出兩支 MP4。' -ForegroundColor Yellow
    Read-Host '按 Enter 結束'
    exit 1
}

function Render-Video([string]$variant, [string]$fileName) {
    $frames = Join-Path $output $variant
    $target = Join-Path $output $fileName
    & $ffmpeg -y -framerate '1/10' -start_number 1 -i (Join-Path $frames 'scene-%02d.png') -c:v libx264 -pix_fmt yuv420p -r 30 -movflags +faststart $target
    if ($LASTEXITCODE -ne 0) { throw "影片輸出失敗：$fileName" }
    Write-Host "已完成：$target" -ForegroundColor Green
}

Render-Video 'landscape' '安嘉點餐系統_3分鐘_橫式.mp4'
Render-Video 'portrait' '安嘉點餐系統_3分鐘_直式.mp4'
Read-Host '兩支影片已完成。按 Enter 結束'
