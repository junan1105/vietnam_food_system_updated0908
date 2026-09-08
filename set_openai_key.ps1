$secureKey = Read-Host "Paste your OpenAI API key (input is hidden)" -AsSecureString
$pointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureKey)
try {
    $plainKey = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($pointer)
    if ([string]::IsNullOrWhiteSpace($plainKey)) { throw "No API key was entered." }
    [Environment]::SetEnvironmentVariable("OPENAI_API_KEY", $plainKey, "User")
    Write-Host "API key saved. Run the website restart script next." -ForegroundColor Green
}
finally {
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($pointer)
}
Read-Host "Press Enter to close"
