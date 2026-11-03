# 独立恢复与错误处理

来源：`WindowsDesktop.display/close`、`DisplayWatchdog`、`watchdog_main`、`Window.recover/exit_mode/closeEvent`。

## 跨模块顺序

进入：Qt `guard.arm()` → `WindowsDesktop.display(2)` → 关闭上一轮 watchdog（若有）→ 获取 Mouse 设备快照 → 新 `DisplayWatchdog(ids)` 等待 ready → 暂停设备并确认 → 关闭显示信号。

```python
# WindowsDesktop.display(2)：先建立独立恢复，再产生设备副作用。
self.mouse = MouseDevices()
self.watchdog = DisplayWatchdog(self.mouse.ids)
try:
    self.mouse.suspend()
    self.signal(2)
except Exception:
    self.display(-1)
    raise
```

正常恢复：Qt 关闭 guard → `display(-1)` 尝试恢复本轮鼠标，并在 finally 中恢复显示信号。watchdog 通常保留到下一轮或 `desktop.close()` 才关闭；不要把键盘唤醒理解为恢复子进程立即退出。

## 独立进程协议

每轮 `DisplayWatchdog` 创建系统临时目录 `yaoguang-watchdog-*`。协议文件如下：

| 文件 | 写入者 | 含义 |
| --- | --- | --- |
| `devices.json` | 主进程 | 本轮可暂停鼠标的 ID 列表 |
| `ready` | 子进程 | 已取得父进程句柄并读取设备快照，可开始暂停 |
| `restore` | 主进程 | 请求子进程恢复并退出 |

frozen 模式启动同一 EXE 的 `--watch-parent <parent_pid> <directory>`；源码模式启动 `yaoguang_watchdog.py`。子进程使用 `CREATE_NO_WINDOW`，stdout/stderr 丢弃，并设置 `PYINSTALLER_RESET_ENVIRONMENT=1`。Qt 入口必须在导入 PySide6 前识别该内部参数。

主进程最多等待 ready 15 秒，失败则 close 并报告“恢复保护未启动”。子进程每 250 ms 等待父进程句柄；父进程结束或发现 restore 后，先尝试恢复显示信号，再在 finally 中恢复快照鼠标，并关闭句柄、清理临时目录。`DisplayWatchdog.close()` 写 restore，最多等待 8 秒；超时报告错误，子进程未退出时不能直接删除恢复所需目录。

## 错误矩阵

| 触发 | 当前处理 |
| --- | --- |
| 设置读错误 | `load_config` 记录异常并使用默认值；文件不存在不报错 |
| 保存失败 | 保存按钮捕获 `OSError`，`report_error` 写日志并显示 warning |
| 手动进入 / tick 失败 | `recover` 分别尝试关闭输入保护、恢复显示/鼠标，回到 ready 后报告原错误 |
| 暂停失败 | `MouseDevices.suspend` 恢复 pending；原生层再走 display(-1)，上层仍进行 recover |
| 单个鼠标恢复失败 | 尽量尝试其他目标，再抛出错误；不吞掉错误并伪造成功 |
| 正常关闭 | 停止 Qt timer，释放 guard；waiting 时尝试恢复显示；main 的 finally 清理 desktop 和互斥量 |
| 主进程异常结束 | 独立子进程依据父进程句柄恢复；不依赖 GUI 的 finally 必然执行 |

Win32 失败通常抛出 `ctypes.WinError`；设备 CONFIGRET、线程/保护超时使用带中文说明的 `RuntimeError`。没有自定义业务异常层或 API 错误响应格式。`report_error()` 同时写异常日志和 `QMessageBox.warning`。

## 审查与验证

- 基准成功：先 ready 再暂停；唤醒后鼠标恢复；下次进入可以重建保护。
- 故障：无鼠标、部分暂停失败、ready 超时、恢复失败、进程异常结束，都必须走各自恢复通道。
- 审查每个新资源的取得/释放与每个副作用的回滚；不要把独立恢复改成 GUI 线程，不要先暂停后创建 watchdog。
- 现有代码会报告无法恢复的错误；不承诺任意硬件故障均能自动修复。设备恢复、主进程崩溃等真实检查需要 Windows 环境，历史证据不等于本轮重跑。
