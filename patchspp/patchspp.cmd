@pushd %~dp0bin
@powershell -ExecutionPolicy Unrestricted -Command .\spp.ps1 %*
@popd
