#requires -Version 5.1
# Downloads/verification only; Python and OpenSSL must already be trusted.
$ErrorActionPreference='Stop'
& python (Join-Path $PSScriptRoot 'download.py') @args
if($LASTEXITCODE -ne 0){throw 'MUiT download or verification failed; no downloaded program was started'}
