# Yaoguang 项目规范

Yaoguang 是 Windows 本地“下班熄屏”工具：临时暂停本轮鼠标设备，关闭显示信号，按键盘恢复；唤醒后可按无操作时间再次进入同样的流程。主机继续运行，程序不主动锁屏。当前交付是 `YaoguangQt.exe` 单文件程序。

## 规范入口

| 入口 | 内容 |
| --- | --- |
| [Desktop](desktop/index.md) | Python / Qt / Win32 正式实现、维护规则与交付检查 |
| [思考指南](guides/index.md) | 跨模块改动与代码复用检查 |

这是单仓库、单个桌面程序。`desktop/` 取代初始化时未填写的 `backend/`；本项目没有 Web 前后端、HTTP API、数据库、ORM 或服务端部署。规范和项目说明使用中文，代码符号保留原名。

## 当前基线与证据

- 正式运行模块：`yaoguang_qt.py`、`yaoguang_native.py`、`yaoguang_devices.py`、`yaoguang_watchdog.py`。
- 构建环境：Windows Python 3.12；依赖固定在 `requirements.txt`（PySide6 6.11.2、PyInstaller 6.22.3）。WSL 可做静态检查，不能替代 Windows 功能验收。
- 使用说明以 [README](../../README.md) 为入口；当前交付以 [清理版验收记录](../../docs/验收记录-2026-11-03.md)、[包核验](../../docs/acceptance/2026-11-03-build.json) 和 [清理记录](../../docs/acceptance/2026-11-03-cleanup.json) 为准。
- 真实熄屏和键盘唤醒历史证据位于 [自动熄屏记录](../../docs/history/验收记录-2026-11-03-自动熄屏修正.md)；其中旧测试命令和旧 EXE 哈希不能用于描述当前发行包。
- Trellis 初始化回填的执行与验证结果保存在 `.trellis/tasks/archive/2026-11/00-bootstrap-guidelines/`。

## 能力边界

当前已交付：仅键盘唤醒、唤醒后无操作再次熄屏、旧设置兼容、同一 Windows 会话单实例、独立进程异常恢复。当前验收包含用户现场双屏确认；不代表所有显示器与输入环境均已覆盖。

尚未完成专项验证：远程桌面、运行中新增鼠标、热插拔、外部输入桌面切换及不同连接方式。[优化清单](../../docs/优化清单.md) 中的托盘、快捷键、日志轮转、版本显示、定时下班和开机启动仍属于后续建议。此处不代替后续需求任务。
