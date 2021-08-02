@echo off

if "%1" == "" GOTO MISSING_FILE
cmd /k powershell -exec bypass ".\demo.ps1" "%1"
exit /b

:MISSING_FILE
echo [-] Usage demo [filename]