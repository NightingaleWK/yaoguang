# 代码与现状依据

核对日期：2026-11-03。仓库 `main`，源码基线 `2becb1544e3a3f13d5dd50d5462bf36ab5dfe294`。

| 主题 | 当前拥有者与依据 | 要固化的事实 |
| --- | --- | --- |
| 产品入口 | `README.md`、`yaoguang_qt.py:main` | Windows 本地 Qt 工具；单文件 EXE，无 Web 服务或数据库 |
| UI 与计时 | `Window.enter_mode/tick/exit_mode` | ready/waiting/counting；唤醒后才启动无操作循环；手动与自动共用进入流程 |
| 设置 | `load_config`、`Window.save` | BOM/旧字段兼容；10–86400 秒；临时文件替换；数据位于源码或 EXE 目录 |
| 原生显示 | `WindowsDesktop.signal/display/last_input` | 私有隐藏窗口、SC_MONITORPOWER；最近输入值只用于判断变化；计时使用 monotonic |
| 输入保护 | `KeyboardWakeGuard` | 独立线程与消息泵；吞掉首次唤醒键；钩子单独不能阻止系统亮屏 |
| 鼠标范围 | `MouseDevices`、`restore_devices` | 只枚举正常启动的 Mouse 类设备；暂停后检查 problem=22；只恢复本轮快照 |
| 异常恢复 | `DisplayWatchdog`、`watchdog_main` | 先准备独立恢复再暂停；devices.json/ready/restore 协议；父进程句柄及退出恢复 |
| 打包 | `scripts/build_windows.py`、`requirements.txt` | Windows Python 3.12，PySide6 6.11.2，PyInstaller 6.22.3；单文件、GUI、管理员清单 |
| 包核验 | `scripts/verify_package.py` | 四个正式模块的规范化 code object、桌面副本哈希、管理员清单及禁止测试模块 |
| 当前交付 | `docs/验收记录-2026-11-03.md`、`docs/acceptance/2026-11-03-build.json` | 最终清理版 EXE；当前源码及产物哈希已再次匹配历史报告 |
| 历史行为证据 | `docs/history/acceptance/2026-11-03-auto-off.json`、`2026-11-03-keyboard-only-final.json` | 自动再次熄屏、真实显示信号、仅键盘唤醒、异常恢复、单实例等历史通过 |
| 后续边界 | `README.md`、`docs/优化清单.md` | 托盘、快捷键、日志轮转、定时/开机启动为建议；远程桌面、热插拔等未完成专项验收 |

## 需避免的历史误读

- 早期记录中的主动锁屏已经被自动再次熄屏取代。
- 历史复现命令中的 `tests/`、`--idle-cycle-check` 等已经从正式发行版移除；不能直接作为当前测试入口。
- 历史六模块验收版与当前四模块清理版的 EXE 哈希不同。当前产物以 `docs/acceptance/2026-11-03-build.json` 为准。
- `docs/优化清单.md` 的旧失败记录路径仍写作 `acceptance/2026-11-03-os-only-wake.json`，实际文件已归档到 `docs/history/acceptance/2026-11-03-os-only-wake.json`；本轮不改写历史材料。
- 本轮未重跑 16 项临时回归或真实硬件循环，只复核当前代码、静态合同及包内容。
