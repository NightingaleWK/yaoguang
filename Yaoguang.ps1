param(
    [ValidateSet('off','on')]
    [string]$Action = 'off'
)

$ErrorActionPreference = 'Stop'

Add-Type @'
using System;
using System.Runtime.InteropServices;
public static class YaoguangDisplay {
    [DllImport("user32.dll", SetLastError=true)]
    public static extern IntPtr SendMessage(IntPtr hWnd, uint Msg, IntPtr wParam, IntPtr lParam);
    public static readonly IntPtr HWND_BROADCAST = new IntPtr(0xffff);
    public const uint WM_SYSCOMMAND = 0x0112;
    public const int SC_MONITORPOWER = 0xF170;
}
'@

function Find-OpenRgb {
    $candidates = @(
        (Get-Command openrgb.exe -ErrorAction SilentlyContinue).Source,
        "$env:ProgramFiles\OpenRGB\OpenRGB.exe",
        "${env:ProgramFiles(x86)}\OpenRGB\OpenRGB.exe",
        "$env:LOCALAPPDATA\Programs\OpenRGB\OpenRGB.exe"
    ) | Where-Object { $_ -and (Test-Path -LiteralPath $_) }
    return $candidates | Select-Object -First 1
}

function Set-Rgb([ValidateSet('off','on')][string]$State) {
    $openRgb = Find-OpenRgb
    if (-not $openRgb) {
        Write-Host '[RGB] OpenRGB not found; skipped device lighting.' -ForegroundColor Yellow
        return
    }

    # Device names vary by firmware. Add the exact names shown by OpenRGB here if needed.
    $devices = @('J104', 'Logitech G102', 'G102', 'G203')
    $mode = if ($State -eq 'off') { 'off' } else { 'static' }
    $changed = $false
    foreach ($device in $devices) {
        try {
            $p = Start-Process -FilePath $openRgb -ArgumentList @('--device', $device, '--mode', $mode) -WindowStyle Hidden -Wait -PassThru
            if ($p.ExitCode -eq 0) { $changed = $true }
        } catch { }
    }
    if ($changed) { Write-Host "[RGB] Requested OpenRGB state: $State." -ForegroundColor Green }
    else { Write-Host '[RGB] No matching device; check names in OpenRGB or use hardware hotkeys.' -ForegroundColor Yellow }
}

function Set-Monitors([ValidateSet('off','on')][string]$State) {
    $level = if ($State -eq 'off') { 2 } else { -1 }
    [void][YaoguangDisplay]::SendMessage(
        [YaoguangDisplay]::HWND_BROADCAST,
        [YaoguangDisplay]::WM_SYSCOMMAND,
        [IntPtr][YaoguangDisplay]::SC_MONITORPOWER,
        [IntPtr]$level)
    if ($State -eq 'off') { Write-Host '[Display] Signal off; PC keeps running and Windows is not locked.' -ForegroundColor Green }
    else { Write-Host '[Display] Signal restored.' -ForegroundColor Green }
}

if ($Action -eq 'off') {
    Set-Rgb off
    Start-Sleep -Milliseconds 250
    Set-Monitors off
} else {
    Set-Monitors on
    Set-Rgb on
}
