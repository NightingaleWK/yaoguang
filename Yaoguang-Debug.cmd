@echo off
setlocal
echo Starting Yaoguang in diagnostic mode...
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0Yaoguang.ps1"
if errorlevel 1 (
  echo.
  echo Yaoguang failed. See yaoguang.log for details.
  pause
)
endlocal
