# Yaoguang 下班关灯

双击 `下班关灯.cmd` 后：

- 关闭两个显示器的显示信号；主机继续运行，后台任务继续运行。
- 不调用锁屏接口，Windows 会保持当前解锁状态。
- 如果安装了 [OpenRGB](https://openrgb.org/)，尝试关闭 J104 和 Logitech G102/G203 的灯效。

双击 `恢复屏幕和灯效.cmd` 可以恢复显示器信号，并请求 OpenRGB 恢复静态灯效。

## 使用前

1. 可选安装 OpenRGB，并在 OpenRGB 中确认它能看到键盘和鼠标。设备名称因固件不同可能显示为 `J104`、`Logitech G102` 或其他名称。
2. 如果 OpenRGB 看不到设备，脚本仍会正常关闭显示器；外设灯效需要使用设备上的灯效快捷键，或把 OpenRGB 的实际设备名称补到 `Yaoguang.ps1` 的 `$devices` 数组中。
3. 第一次运行如果被 Windows 策略拦截，可右键 `下班关灯.cmd` 选择“以管理员身份运行”。通常关闭显示器不需要管理员权限。

## 验证

运行：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\Yaoguang.ps1 -Action off
powershell -NoProfile -ExecutionPolicy Bypass -File .\Yaoguang.ps1 -Action on
```

脚本没有调用 `LockWorkStation`、关机、睡眠或休眠接口。

