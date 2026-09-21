param()
$ErrorActionPreference = 'Stop'
$logPath = Join-Path (Split-Path -Parent $MyInvocation.MyCommand.Path) 'yaoguang.log'
try { Start-Transcript -Path $logPath -Append -Force | Out-Null } catch { }
Add-Type @'
using System;
using System.Runtime.InteropServices;
public static class YaoguangNative {
 [DllImport("user32.dll")] public static extern IntPtr SendMessage(IntPtr hWnd,uint msg,IntPtr wParam,IntPtr lParam);
 [DllImport("user32.dll")] public static extern bool GetLastInputInfo(ref LASTINPUTINFO info);
 [DllImport("user32.dll")] public static extern bool LockWorkStation();
 [StructLayout(LayoutKind.Sequential)] public struct LASTINPUTINFO { public uint cbSize; public uint dwTime; }
 public static readonly IntPtr HWND_BROADCAST=new IntPtr(0xffff); public const uint WM_SYSCOMMAND=0x0112; public const int SC_MONITORPOWER=0xF170;
 public static uint LastInputTick(){ LASTINPUTINFO i=new LASTINPUTINFO(); i.cbSize=(uint)Marshal.SizeOf(i); return GetLastInputInfo(ref i)?i.dwTime:0; }
}
'@
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
[Windows.Forms.Application]::EnableVisualStyles()
$configPath=Join-Path (Split-Path -Parent $MyInvocation.MyCommand.Path) 'settings.json'
$settings=@{autoLockEnabled=$true;idleSeconds=60}
if(Test-Path $configPath){try{$s=Get-Content $configPath -Raw|ConvertFrom-Json;if($null-ne $s.autoLockEnabled){$settings.autoLockEnabled=[bool]$s.autoLockEnabled};if($s.idleSeconds-ge 10-and $s.idleSeconds-le 86400){$settings.idleSeconds=[int]$s.idleSeconds}}catch{}}
$form=New-Object Windows.Forms.Form;$form.Text='Yaoguang 下班模式';$form.ClientSize=New-Object Drawing.Size(430,330);$form.StartPosition='CenterScreen';$form.FormBorderStyle='FixedDialog';$form.MaximizeBox=$false
function Add-Label($text,$x,$y,$size=10){$l=New-Object Windows.Forms.Label;$l.Text=$text;$l.Location=New-Object Drawing.Point($x,$y);$l.Font=New-Object Drawing.Font('Microsoft YaHei UI',$size);$l.AutoSize=$true;$form.Controls.Add($l);return $l}
$title=Add-Label 'Yaoguang 下班模式' 24 18 16;$title.Font=New-Object Drawing.Font('Microsoft YaHei UI',16,[Drawing.FontStyle]::Bold)
$status=Add-Label '当前状态：正常运行' 26 62 11;$status.Font=New-Object Drawing.Font('Microsoft YaHei UI',11,[Drawing.FontStyle]::Bold)
$autoLock=New-Object Windows.Forms.CheckBox;$autoLock.Text='启用无操作自动锁屏';$autoLock.Checked=$settings.autoLockEnabled;$autoLock.Location=New-Object Drawing.Point(28,105);$autoLock.AutoSize=$true;$form.Controls.Add($autoLock)
[void](Add-Label '无操作时间（秒）：' 28 140);$seconds=New-Object Windows.Forms.NumericUpDown;$seconds.Minimum=10;$seconds.Maximum=86400;$seconds.Value=$settings.idleSeconds;$seconds.Location=New-Object Drawing.Point(160,136);$seconds.Width=90;$form.Controls.Add($seconds)
$hint=Add-Label '关闭显示器后，移动鼠标或按键盘会唤醒屏幕。' 28 174 9;$hint.ForeColor=[Drawing.Color]::DimGray
$mainButton=New-Object Windows.Forms.Button;$mainButton.Text='进入下班模式';$mainButton.Location=New-Object Drawing.Point(28,212);$mainButton.Size=New-Object Drawing.Size(170,42);$mainButton.Font=New-Object Drawing.Font('Microsoft YaHei UI',10,[Drawing.FontStyle]::Bold);$form.Controls.Add($mainButton)
$restoreButton=New-Object Windows.Forms.Button;$restoreButton.Text='恢复显示器';$restoreButton.Location=New-Object Drawing.Point(210,212);$restoreButton.Size=New-Object Drawing.Size(170,42);$form.Controls.Add($restoreButton)
$saveButton=New-Object Windows.Forms.Button;$saveButton.Text='保存设置';$saveButton.Location=New-Object Drawing.Point(28,268);$saveButton.Size=New-Object Drawing.Size(110,30);$form.Controls.Add($saveButton)
$state='Ready';$baselineInput=[uint32]0;$lastWakeInput=[uint32]0;$locked=$false
function Set-Monitors([int]$level){[void][YaoguangNative]::SendMessage([YaoguangNative]::HWND_BROADCAST,[YaoguangNative]::WM_SYSCOMMAND,[IntPtr][YaoguangNative]::SC_MONITORPOWER,[IntPtr]$level)}
function Save-Settings{@{autoLockEnabled=[bool]$autoLock.Checked;idleSeconds=[int]$seconds.Value}|ConvertTo-Json|Set-Content $configPath -Encoding UTF8}
function Refresh-Ui{if($state-eq'Ready'){$status.Text='当前状态：正常运行';$mainButton.Text='进入下班模式'}elseif($state-eq'Waiting'){$status.Text='当前状态：显示器已关闭，等待输入';$mainButton.Text='退出下班模式'}elseif($state-eq'Counting'){$e=[uint32](([Environment]::TickCount)-$lastWakeInput);$left=[Math]::Max(0,[int]$seconds.Value-[int]($e/1000));$status.Text="当前状态：已唤醒，$left 秒后自动锁屏";$mainButton.Text='退出下班模式'}elseif($state-eq'Locked'){$status.Text='当前状态：已锁屏';$mainButton.Text='退出下班模式'}}
$timer=New-Object Windows.Forms.Timer;$timer.Interval=250;$timer.Add_Tick({if($state-eq'Waiting'){$now=[YaoguangNative]::LastInputTick();if($now-ne 0-and $now-ne $baselineInput){$lastWakeInput=$now;$state=if($autoLock.Checked){'Counting'}else{'Ready'};Refresh-Ui}}elseif($state-eq'Counting'){$now=[YaoguangNative]::LastInputTick();if($now-ne $lastWakeInput){$lastWakeInput=$now;Refresh-Ui;return};$e=[uint32](([Environment]::TickCount)-$lastWakeInput);if($e-ge([int]$seconds.Value*1000)){if([YaoguangNative]::LockWorkStation()){$state='Locked';$locked=$true;Refresh-Ui}}else{Refresh-Ui}}})
$saveButton.Add_Click({Save-Settings;[Windows.Forms.MessageBox]::Show('设置已保存。','Yaoguang')})
$mainButton.Add_Click({if($state-eq'Ready'){Save-Settings;$baselineInput=[YaoguangNative]::LastInputTick();Set-Monitors 2;$state='Waiting';$timer.Start();Refresh-Ui}else{Set-Monitors -1;$timer.Stop();$state='Ready';Refresh-Ui}})
$restoreButton.Add_Click({Set-Monitors -1;$timer.Stop();$state='Ready';Refresh-Ui})
$form.Add_FormClosing({if($state-ne'Ready'-and-not$locked){Set-Monitors -1};$timer.Stop();try{Stop-Transcript|Out-Null}catch{}})
Refresh-Ui;[void]$form.ShowDialog()
