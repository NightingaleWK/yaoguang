# 目录与职责

## 当前布局

```text
yaoguang_qt.py          Qt 入口、界面、设置、状态机、100 ms 定时器
yaoguang_native.py      Win32 显示、最近输入、互斥量、输入钩子线程
yaoguang_devices.py     Mouse 类设备枚举、暂停、恢复与回滚
yaoguang_watchdog.py    独立恢复进程及临时文件协议
scripts/build_windows.py
scripts/verify_package.py
requirements.txt       固定 Windows 构建依赖
YaoguangQt.exe         当前正式单文件交付
docs/                  优化清单、当前验收与 history/ 历史证据
.trellis/              规范、任务、工作日志及 Trellis 运行工具
```

## 修改放置规则

- UI、文字、交互和计时放在 `yaoguang_qt.Window`；配置读取以 `load_config` 为唯一兼容入口。
- 显示、单实例和钩子放在 `yaoguang_native`；设备枚举/暂停/恢复放在 `yaoguang_devices`。Qt 层调用 `desktop.display()`，不要内联设备操作。
- 独立恢复必须留在 `yaoguang_watchdog`，不能改成依附 GUI 存活的线程。
- 构建和静态包检查放在 `scripts/`；验收说明与证据放在 `docs/`。当前没有持久测试目录或 pytest/unittest 工程。
- 当前代码为小型平铺模块，使用 `snake_case` 函数/文件和 `PascalCase` 类。不要仅为套用框架新增 routes/services/models 分层。

`yaoguang_qt.py` 顶部先分流 `--watch-parent`，再设置 frozen Qt DLL 路径并导入 PySide6。保留这个顺序；DLL 目录句柄 `_qt_dll_directory` 要保持到进程结束。原生层在 `display(2)` 内延迟导入设备和 watchdog，watchdog 子进程再加载原生恢复接口。

## 本地文件与 Trellis

`settings.json`、`yaoguang.log` 位于 EXE 或源码目录，由 `.gitignore` 排除。`build/`、`dist/`、`.venv/`、`*.spec`、缓存也被忽略；当前构建脚本使用系统临时目录，不把这些目录当作交付物。

`.trellis/spec/` 是维护规范；任务记录在 `.trellis/tasks/`，完成后归档；工作日志由 `.trellis/scripts/add_session.py` 维护。`.gitattributes` 对 `workspace/*/journal-*.md` 使用 `merge=union`，不对会重建的个人 `index.md` 使用此规则。Trellis runtime、开发者标记和管理哈希按现有脚本管理，不手工伪造。
