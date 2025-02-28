$SPPPid = (Get-Process -Name sppsvc).Id

Push-Location $PSScriptRoot

.\PPLControl.exe unprotect $SPPPid | Out-Null
if($LastExitCode -ne 0) {
    Write-Host "Failed."
    Pop-Location
    exit 1
}

$ENV:_NT_SYMBOL_PATH = '.'
.\cdb.exe -snul -cf activate.txt -p $SPPPid | Out-Null
$ENV:_NT_SYMBOL_PATH = ''

.\PPLControl.exe protect $SPPPid PP Windows | Out-Null
if($LastExitCode -ne 0) {
    Write-Host "Failed."
    Pop-Location
    exit 1
}

Pop-Location

Write-Host "Done."
