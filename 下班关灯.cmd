@echo off
setlocal
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0Yaoguang.ps1" -Action off
if errorlevel 1 pause
endlocal

