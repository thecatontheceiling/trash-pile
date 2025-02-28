@pushd %~dp0bin
@powershell -ExecutionPolicy Unrestricted -Command .\activate.ps1 %*
@popd
