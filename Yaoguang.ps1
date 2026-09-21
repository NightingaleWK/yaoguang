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
    Set-Monitors off
} else {
    Set-Monitors on
}
