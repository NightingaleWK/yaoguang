# Yaoguang 下班模式

运行要求：Windows PowerShell 7（`pwsh.exe`），启动器会以 STA 模式运行 WinForms 界面。如果电脑未安装，启动器会提示下载地址。

双击 `Yaoguang-GUI.cmd`（或 `下班关灯.cmd`）打开图形界面：

- 关闭两个显示器的显示信号；主机继续运行，后台任务继续运行。
- 点击“进入下班模式”时不会立即锁屏，Windows 会保持当前解锁状态。
- 可以配置无操作自动锁屏时间，默认 60 秒。
- 显示器关闭后，移动鼠标或按键盘会唤醒显示器；之后持续无操作达到设定时间，程序调用 Windows 正常锁屏。

`恢复屏幕和灯效.cmd` 也会打开同一个界面，再点击“恢复显示器”。工具不会修改键盘和鼠标灯效。

程序运行日志保存在同目录的 `yaoguang.log`。如果双击后窗口仍然闪退，可双击 `Yaoguang-Debug.cmd`，它会保留错误窗口并提示日志位置。

## 使用前

1. 在 GUI 中勾选自动锁屏并设置秒数，点击“保存设置”。最小值为 10 秒。
2. 第一次运行如果被 Windows 策略拦截，可右键 `.cmd` 文件选择“以管理员身份运行”。通常关闭显示器和锁屏不需要管理员权限。

## 验证

运行：

```powershell
pwsh -NoProfile -ExecutionPolicy Bypass -File .\Yaoguang.ps1
```

脚本不会关机、睡眠、休眠或控制键鼠灯效；自动锁屏开启时会调用 Windows 的 `LockWorkStation`。
