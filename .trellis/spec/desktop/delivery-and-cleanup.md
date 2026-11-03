# 构建交付与清理

来源：`requirements.txt`、`scripts/build_windows.py`、`scripts/verify_package.py` 和当前清理版验收记录。

## 构建合同

使用 Windows Python 3.12。依赖为 `PySide6==6.11.2`、`PyInstaller==6.22.3`；校验脚本还使用 PyInstaller 依赖带入的 `pefile`。不要用系统默认 Python 代替经核对的 3.12 来比较内嵌 code object。

在项目根目录，用确认指向该环境的 `python` 运行：

```powershell
python -m pip install -r requirements.txt
python scripts/build_windows.py --desktop
```

脚本拒绝非 Windows 平台；调用 PyInstaller 的 `--onefile --windowed --uac-admin --name YaoguangQt`。work/dist/spec 都在 `TemporaryDirectory` 中，完成后清理并复制最终 EXE 到仓库根目录。`--desktop` 再通过 Windows `GetFolderPath('Desktop')` 获取真实桌面，不能硬编码忽略 OneDrive 重定向。

保留 frozen 模式的 Qt DLL 查找与句柄生命周期，以及 watchdog 的独立进程环境重置。此前有 DLL 查找与 Python 版本调整的提交，改动运行环境时需重新验证启动与恢复。

## 包核验合同

```powershell
python scripts/verify_package.py --desktop C:\Users\djsyw\Desktop\YaoguangQt.exe --output "$env:TEMP\yaoguang-package-verification.json"
```

上例桌面是当前验收记录中的路径；执行时先重新确认真实桌面。输出选择新的任务或验收记录，避免覆盖旧证据。检查不启动 EXE，不会熄屏或暂停设备。

脚本逐项断言：

1. EXE 内的 `yaoguang_qt`、`yaoguang_native`、`yaoguang_devices`、`yaoguang_watchdog` 与最终源码编译结果一致；只递归规范化 `co_filename`，因此需要兼容的 Python 版本。
2. 仓库 EXE 与桌面副本 SHA-256 相同。
3. PE 清单包含 `requireAdministrator`。
4. 不包含脚本列出的验收模块、`unittest`、`tests` 及其子模块；这是明确禁止列表检查，不等于扫描所有可能的开发工具。

当前交付基线位于 `docs/acceptance/2026-11-03-build.json`。不要只凭文件名、时间戳、大小或 GUI 能打开就认为 EXE 与源码一致。

## 交付完成条件

改动业务实现时，交付包括最终源码、必要说明/验收结果、仓库 EXE 和经核对的桌面单文件 EXE。仅修改文档或 Trellis 时不重建业务未变化的 EXE，也不把本轮静态检查描述成真实硬件重新验收。

新增正式模块时同步审查 PyInstaller 导入、`verify_package.py` 的模块清单和交付说明。正式包不恢复历史验收命令、测试模块、旧 C#/PowerShell 入口或重复启动脚本。

## 清理边界

只清理由本轮创建、确认可再生的临时验证文件和构建缓存。保留源码、主开发环境、用户 `settings.json`、`yaoguang.log`、当前 EXE、实际桌面副本及全部真实验收/历史证据。不要把整个 `docs/history/` 当成废弃产物删除，也不要为清理而卸载已有环境。

Trellis 的归档与日志脚本默认可能自动提交 Git。未包含 Git 提交的任务使用受支持的 `--no-commit`；无 PR 分支的初始化任务归档可用 `--skip-branch-validation`，在任务中说明理由，不伪造分支、提交或验收结果。
