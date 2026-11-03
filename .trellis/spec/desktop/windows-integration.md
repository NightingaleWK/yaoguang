# Windows 显示与输入

来源：`yaoguang_native.py`、`yaoguang_devices.py`；独立恢复协议见 [恢复与错误](recovery-and-errors.md)。这些模块运行依赖 Win32，不能在 WSL 中导入并据此宣称功能通过。

## 显示与最近输入

- `WindowsDesktop` 创建私有隐藏 `STATIC` 窗口，使用 `SendMessageTimeoutW` 发送 `WM_SYSCOMMAND/SC_MONITORPOWER`：`2` 熄屏，`-1` 恢复；不依赖向所有应用广播。
- `signal(-1)` 先用 `SetThreadExecutionState(0x00000002)` 做一次显示空闲复位，不设置持续保亮标志。
- `display(2)` 负责整条保护流程；`signal(2)` 只是底层显示操作，Qt 不应跳过设备保护直接调用它。
- `GetLastInputInfo` 的 `dwTime` 通过 `last_input()` 返回；上层只用它检测变化，不将它直接减去 `time.monotonic()`。

## 输入钩子合同

`KeyboardWakeGuard` 在独立 daemon 线程创建消息队列、安装低级鼠标与键盘钩子并运行消息泵。`arm()` 等待最多 3 秒确认启动；`close()` 取消 armed，投递退出消息并等待线程结束，未退出时报告错误。

持有 `_mouse_proc`、`_keyboard_proc` 的 ctypes callback 引用；不能只传临时回调对象。`LRESULT/LPARAM` 使用 `c_ssize_t`，`WPARAM` 使用 `c_size_t`，设备结构中的 reserved、键盘 extra info 也必须保持指针宽度；新增绑定照现有 `argtypes/restype` 规则明确签名。

armed 期间丢弃鼠标事件。首个键盘 key-down 设置唤醒事件并解除 armed，该键的后续重复/key-up 继续被消费，避免唤醒按键落入前台应用。事件由 Qt tick 消费，不记录按键内容。

**仅钩子吞事件不能保证 Windows 不亮屏。** 失败证据见 `docs/history/acceptance/2026-11-03-os-only-wake.json`；不能把“仍处于 waiting”当作物理熄屏证明。

## Mouse 类设备合同

`WindowsMouseApi.enumerate()` 只枚举当前存在的 Mouse 类设备（GUID `4d36e96f-e325-11ce-bfc1-08002be10318`）。`MouseDevices` 只选择已启动且 problem=0 的设备；不操作 Keyboard 类、通用 HID 集合、USB 父设备或用户预先禁用的鼠标。

暂停使用 `CM_Disable_DevNode(devinst, 1)`，不设置 `CM_DISABLE_PERSIST`。每次尝试前把 ID 加入 `pending`，全部调用后重新枚举，确认所有目标 problem=22；无可用鼠标或未全部暂停时进入失败恢复，不能继续报成功。

恢复由 `restore_devices(names, api=None)` 拥有：重新枚举 Mouse 类，只对本轮 ID 且当前 problem=22 的设备调用 enable。恢复尝试覆盖所有目标后再抛出首个错误；最多轮询 30 次、每次 0.1 秒。当前缺失的设备被视为无需继续等待；这不构成热插拔已验收的证据。`MouseDevices.restore()` 仅在恢复成功后清空 `pending`，便于失败后重试。

## 单实例

`acquire_instance()` 使用会话命名互斥量 `Local\Yaoguang.KeyboardWake`。已存在时关闭新句柄并返回 `None`，UI 提示已有实例；主实例最终释放句柄。范围是同一 Windows 会话，不承诺跨会话互斥，也不使用磁盘锁文件。

## 验收与禁止项

涉及设备变更时检查：正常设备筛选、逐设备暂停失败回滚、暂停状态复核、只恢复本轮设备、首次唤醒键、线程退出和重复进入。真实验证须观察 Windows 显示状态及物理键鼠，不能用模拟回调替代。

不得重新采用黑色遮罩、全局 `BlockInput`、主动锁屏或未验证的 DDC/CI 方案替代当前流程。远程桌面、新接入鼠标和不同输入桌面仍在验收边界之外，新增支持需单独任务。
