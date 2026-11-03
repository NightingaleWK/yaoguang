# 日志

来源：`yaoguang_qt.py:main/load_config` 与 `Window`。当前使用标准库 `logging`，不是 JSON 结构日志服务。

## 当前配置与事件

```python
logging.basicConfig(
    filename=ROOT / "yaoguang.log", level=logging.INFO,
    format="%(asctime)s %(message)s",
)
```

记录 GUI 启动/退出、进入 waiting、键盘唤醒、无操作再次进入、恢复显示等生命周期事件。读取设置失败、清理失败等用 `logging.exception`；面向用户的异常由 `report_error` 使用 `logging.error(..., exc_info=True)` 并弹出提示。

调试时从这些状态事件还原一次完整循环。新增日志要说明哪个动作失败、是否进入恢复；不在 100 ms tick 中无条件打印，不记录键盘键值、键入内容或连续鼠标事件。

## 现有限制

当前日志格式不含等级、模块、进程 ID，未设置轮转、大小上限、版本信息或远程上传。独立 watchdog 的 stdout/stderr 丢弃，也未配置自己的文件日志；主进程会报告保护准备/关闭失败，但没有完整子进程诊断日志。不要在排障说明中依赖这些尚未实现的信息。

`yaoguang.log` 在 EXE/源码目录，属于用户本地数据，由 Git 忽略。清理构建产物时保留它。日志轮转与更完整诊断属于 `docs/优化清单.md` 中的后续建议。
