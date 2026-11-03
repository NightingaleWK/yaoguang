# 界面与状态机

来源：`yaoguang_qt.py` 的 `Window`。当前是 `QWidget` + `QTimer`，固定 540 × 410 逻辑像素，Fusion 风格、Microsoft YaHei UI 字体；不是浏览器界面。

## 状态合同

| 状态 | 进入条件 | 后续行为 |
| --- | --- | --- |
| `ready` | 启动、明确退出、关闭自动循环、错误恢复 | 正常运行；启动时不会因为开启自动选项就自行倒计时 |
| `waiting` | `enter_mode()` 启用保护并执行 `desktop.display(2)` | 仅等待键盘唤醒；当前鼠标设备被临时暂停 |
| `counting` | `waiting` 中收到唤醒且自动选项开启 | 恢复鼠标/显示后计时；活动重置；到期再次调用 `enter_mode()` |

`toggle()` 在 `ready` 时先保存设置再进入；其他状态调用 `exit_mode()`。关闭自动选项在 `counting` 的下次 tick 结束倒计时；在 `waiting` 中取消勾选不会自动恢复显示，后续唤醒回到 `ready`。恢复显示器、退出模式和关闭窗口负责结束当前循环。

## 必须共用的进入与恢复路径

手动进入与计时到期均调用同一个 `enter_mode()`：

```python
self.guard.arm()
self.state = "waiting"
self.setFocus(Qt.FocusReason.OtherFocusReason)
self.refresh()
self.desktop.display(2)
```

这是 `Window.enter_mode` 的现有顺序，不能在自动分支仅发送熄屏指令、漏掉鼠标保护。界面变成 `waiting` 不能证明显示信号已关闭；`desktop.display()` 失败由调用边界进入 `recover()`。

每 100 ms 的 `tick()` 通过 `guard.take_wake()` 读取线程事件，再关闭钩子、恢复显示和鼠标，按自动选项进入 `counting` 或 `ready`。钩子线程不直接操作 Qt 控件。

## 时间与设置

`desktop.last_input()` 的 Win32 时间值仅比较是否变化。`activity_at` 与 `elapsed` 都用 `time.monotonic()`，不要混用系统启动计时、墙钟或 epoch。倒计时读取当前控件 `self.seconds.value()` 和 `self.auto.isChecked()`；保存由保存按钮或手动进入触发，并非每次修改控件就落盘。

设为 10 秒意味着无操作计时达到 10 秒后开始进入流程；watchdog 准备和设备暂停有额外耗时。历史真实循环记录为约 12.83 秒关闭信号，不保证物理显示器恰好第 10 秒熄灭。

## 修改时的验收点

- 首次启动保持 `ready`；手动进入 → 按键恢复 → 倒计时 → 再次进入可以重复。
- 新键鼠活动重置倒计时；取消自动选项、明确退出与错误恢复的状态正确。
- 文案使用“再次熄屏”“仅按键盘唤醒”；禁止重新引入 `LockWorkStation` 主动锁屏或黑色遮罩。
- 新增状态时同步审查 `toggle`、`tick`、`refresh`、`recover`、`closeEvent`，不能只增加显示文案。
