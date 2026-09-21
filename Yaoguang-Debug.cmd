@echo off
setlocal
echo Starting Yaoguang in diagnostic mode...
where pwsh.exe >nul 2>nul
if errorlevel 1 (
  echo PowerShell 7 (pwsh.exe) is required.
  echo Download: https://github.com/PowerShell/PowerShell
  pause
  exit /b 1
)
pwsh.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0Yaoguang.ps1"
if errorlevel 1 (
  echo.
  echo Yaoguang failed. See yaoguang.log for details.
  pause
)
endlocal
