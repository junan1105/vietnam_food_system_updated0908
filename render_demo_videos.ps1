$ErrorActionPreference = 'Stop'

Add-Type -AssemblyName System.Runtime.WindowsRuntime

${genericAsTask} = [System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object {
    $_.Name -eq 'AsTask' -and $_.IsGenericMethodDefinition -and
    $_.GetGenericArguments().Count -eq 1 -and $_.GetParameters().Count -eq 1 -and
    $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1'
}

function Await-WinRt($operation, [Type]$resultType) {
    $task = $genericAsTask.MakeGenericMethod($resultType).Invoke($null, @($operation))
    $task.Wait()
    return $task.Result
}

function Await-WinRtAction($operation) {
    $task = [System.WindowsRuntimeSystemExtensions]::AsTask([Windows.Foundation.IAsyncAction]$operation)
    $task.Wait()
}

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$output = Join-Path $root 'video-output'

[void][Windows.Storage.StorageFile, Windows.Storage, ContentType=WindowsRuntime]
[void][Windows.Storage.StorageFolder, Windows.Storage, ContentType=WindowsRuntime]
[void][Windows.Media.Editing.MediaComposition, Windows.Media.Editing, ContentType=WindowsRuntime]
[void][Windows.Media.Editing.MediaClip, Windows.Media.Editing, ContentType=WindowsRuntime]
[void][Windows.Media.MediaProperties.MediaEncodingProfile, Windows.Media.MediaProperties, ContentType=WindowsRuntime]
[void][Windows.Media.MediaProperties.VideoEncodingQuality, Windows.Media.MediaProperties, ContentType=WindowsRuntime]
[void][Windows.Storage.CreationCollisionOption, Windows.Storage, ContentType=WindowsRuntime]
[void][Windows.Media.Editing.MediaTrimmingPreference, Windows.Media.Editing, ContentType=WindowsRuntime]

$folder = Await-WinRt ([Windows.Storage.StorageFolder]::GetFolderFromPathAsync($output)) ([Windows.Storage.StorageFolder])

foreach ($variant in @('landscape', 'portrait')) {
    $composition = New-Object Windows.Media.Editing.MediaComposition
    $frameFolder = Join-Path $output $variant
    Get-ChildItem -LiteralPath $frameFolder -Filter 'scene-*.png' | Sort-Object Name | ForEach-Object {
        $file = Await-WinRt ([Windows.Storage.StorageFile]::GetFileFromPathAsync($_.FullName)) ([Windows.Storage.StorageFile])
        $clip = Await-WinRt ([Windows.Media.Editing.MediaClip]::CreateFromImageFileAsync($file, [TimeSpan]::FromSeconds(10))) ([Windows.Media.Editing.MediaClip])
        $composition.Clips.Append($clip)
    }
    $targetName = if ($variant -eq 'landscape') { '安嘉點餐系統_3分鐘_橫式.mp4' } else { '安嘉點餐系統_3分鐘_直式.mp4' }
    $target = Await-WinRt ($folder.CreateFileAsync($targetName, [Windows.Storage.CreationCollisionOption]::ReplaceExisting)) ([Windows.Storage.StorageFile])
    $profile = [Windows.Media.MediaProperties.MediaEncodingProfile]::CreateMp4([Windows.Media.MediaProperties.VideoEncodingQuality]::HD720p)
    $render = $composition.RenderToFileAsync($target, [Windows.Media.Editing.MediaTrimmingPreference]::Precise, $profile)
    Await-WinRtAction $render
    Write-Host "Created: $($target.Path)"
}
