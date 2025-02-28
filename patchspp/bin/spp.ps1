$ErrorActionPreference = [System.Management.Automation.ActionPreference]::Stop

Start-Process sc.exe -ArgumentList "start", "sppsvc" -WindowStyle Hidden

Start-Sleep -Milliseconds 250

$SPPPid = (Get-Process -Name sppsvc).Id

Push-Location $PSScriptRoot

.\PPLControl.exe unprotect $SPPPid | Out-Null
if($LastExitCode -ne 0) {
    Write-Host "Failed."
    Pop-Location
    exit 1
}

$ENV:_NT_SYMBOL_PATH = '.'
.\cdb.exe -snul -cf spp.txt -p $SPPPid | Out-Null
$ENV:_NT_SYMBOL_PATH = ''

.\PPLControl.exe protect $SPPPid PP Windows | Out-Null
if($LastExitCode -ne 0) {
    Write-Host "Failed."
    Pop-Location
    exit 1
}

.\pssuspend64.exe -r $SPPPid | Out-Null
.\pssuspend64.exe -r $SPPPid | Out-Null

Pop-Location

Write-Host "Done."
