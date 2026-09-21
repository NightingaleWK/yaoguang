# Yaoguang 下班关灯

双击 `下班关灯.cmd` 后：

- 关闭两个显示器的显示信号；主机继续运行，后台任务继续运行。
- 不调用锁屏接口，Windows 会保持当前解锁状态。

双击 `恢复屏幕和灯效.cmd` 可以恢复显示器信号。该工具不会修改键盘和鼠标灯效。

## 使用前

1. 第一次运行如果被 Windows 策略拦截，可右键 `下班关灯.cmd` 选择“以管理员身份运行”。通常关闭显示器不需要管理员权限。

## 验证

运行：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\Yaoguang.ps1 -Action off
powershell -NoProfile -ExecutionPolicy Bypass -File .\Yaoguang.ps1 -Action on
```

脚本没有调用 `LockWorkStation`、关机、睡眠、休眠或任何键鼠灯效控制接口。
