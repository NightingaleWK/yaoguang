# Yaoguang 下班模式

Windows 本地下班熄屏工具。双击仓库根目录的 `YaoguangQt.exe`，允许管理员授权后使用；无需安装 Python。

## 使用

1. 按需要设置无操作时间，点击“保存设置”。
2. 点击“进入下班模式”：程序临时暂停鼠标设备输入，并真正关闭显示信号；主机和后台任务继续运行。
3. 按键盘唤醒显示器，鼠标自动恢复。第一次唤醒按键会被消耗，避免误操作。
4. 开启“唤醒后，无操作自动进入下班模式”时，到达设定的无操作时间会重新进入同样的熄屏流程，仍需按键盘唤醒。新的键鼠操作会重置计时。
5. 点击“退出下班模式”“恢复显示器”或关闭窗口，结束当前循环。

程序不会主动锁屏，不使用黑色遮罩。熄屏期间，当前已暂停鼠标的移动、点击和滚轮无法唤醒显示器。默认无操作时间为 60 秒，可设置 10 秒至 24 小时；旧版已保存的秒数和开关设置可继续读取。

暂停鼠标需要管理员权限。程序只操作 Mouse 类设备；键盘在下班期间应保持连接。独立恢复进程负责在主程序异常退出时恢复本轮暂停的鼠标和显示器。同一 Windows 会话只运行一个实例。

## 本地数据

`settings.json` 与 `yaoguang.log` 保存在 EXE 所在目录，目录需要可写。这些文件只保留在本地，不提交到 Git。恢复鼠标时可能伴随设备重新连接提示音。

程序不控制键盘、鼠标灯效。远程桌面、运行中新接入鼠标、热插拔与外部输入桌面切换尚未完成专项验证。

## 项目结构

```text
yaoguang_qt.py          图形界面、设置与无操作再次熄屏
yaoguang_native.py      Windows 显示控制、输入保护、单实例
yaoguang_devices.py     鼠标设备临时暂停与恢复
yaoguang_watchdog.py    主程序异常退出后的独立恢复
scripts/               正式构建与产物校验工具
docs/                  优化清单、验收记录和历史证据
requirements.txt       固定的 Windows 构建依赖
YaoguangQt.exe         当前单文件交付程序
```

发行程序只包含正式功能代码。内部 `--watch-parent` 参数用于启动独立恢复进程，由主程序管理。

## 构建

使用 Windows Python 3.12：

```powershell
python -m pip install -r requirements.txt
python scripts/build_windows.py --desktop
```

构建使用系统临时目录，结束后自动清理；输出项目根目录的 `YaoguangQt.exe`。`--desktop` 额外复制到 Windows 的实际桌面目录，省略此参数则只生成项目内的 EXE。

可核对桌面副本、内嵌正式源码、管理员清单及发行包内容：

```powershell
python scripts/verify_package.py --desktop C:\Users\YOUR_NAME\Desktop\YaoguangQt.exe --output docs/acceptance/2026-11-03-build.json
```

桌面使用重定向或 OneDrive 时，将上述路径替换为实际 EXE 路径。构建与校验脚本不会关闭显示器或暂停鼠标。

[优化清单](docs/优化清单.md) · [当前验收记录](docs/验收记录-2026-11-03.md)
