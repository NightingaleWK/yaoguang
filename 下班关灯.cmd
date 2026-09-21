@echo off
setlocal
where pwsh.exe >nul 2>nul
if errorlevel 1 (
  echo PowerShell 7 (pwsh.exe) is required.
  echo Download: https://github.com/PowerShell/PowerShell
  pause
  exit /b 1
)
start "Yaoguang" pwsh.exe -STA -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0Yaoguang.ps1"
endlocal
