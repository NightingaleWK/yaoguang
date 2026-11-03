# 质量与验收

## 当前检查能力

仓库固定了 PySide6/PyInstaller 依赖，但没有持久测试套件、pytest/unittest 配置、lint/type-check 配置或 CI。不要报告不存在的检查已经通过，也不要直接照抄历史记录中的测试入口。

当前可信检查分为以下几类：

| 类型 | 能说明什么 | 不能替代什么 |
| --- | --- | --- |
| 源码语法与静态合同 | 文件可编译、状态与恢复路径符合实现 | Win32 调用与真实设备效果 |
| 临时隔离回归 | 纯逻辑、边界、失败路径的断言 | 系统显示信号、真实键鼠 |
| `verify_package.py` | 当前源码与 EXE、桌面副本、清单、禁止模块匹配 | 运行时功能验收 |
| Windows 真实验收 | 实际显示状态、物理键鼠、设备恢复、UI 循环 | 未覆盖硬件/会话场景 |

WSL 下可安全检查语法而不导入 Win32 或写入产品目录：

```bash
python3 -B - <<'PY'
from pathlib import Path
paths = sorted(Path('.').glob('yaoguang_*.py')) + sorted(Path('scripts').glob('*.py'))
for path in paths:
    compile(path.read_text(encoding='utf-8'), str(path), 'exec', dont_inherit=True)
print(f'Compiled {len(paths)} Python files')
PY
```

## 按改动选择检查

- 纯 Trellis/说明改动：校验本地文档链接、规范索引、引用符号、模板残留和任务上下文，确认产品及数据未改；无需重新熄屏或打包。
- 设置或计时改动：临时独立配置覆盖 BOM、新旧字段优先级、bool/int、范围、保存失败、重复循环、活动重置、取消和失败恢复。断言业务结果，避免只复述实现。
- 设备/恢复改动：先验证枚举筛选、逐设备失败回滚、只恢复本轮设备，再在 Windows 验证真实信号、键盘唤醒、鼠标不亮屏、正常退出与主进程异常结束恢复。
- 正式源码或构建改动：还要执行 [构建与包核验](delivery-and-cleanup.md)，交付与最终源码匹配的桌面单文件 EXE。

真实熄屏和设备暂停会改变当前交互状态，应结合任务授权与独立验收窗口安排。日常静态检查不得顺带调用 `display(2)`、`MouseDevices.suspend()` 或强杀用户在用的进程。

## 现有证据及其边界

- `docs/acceptance/2026-11-03-cleanup.json` 及当前验收记录记载清理后 16 项临时回归通过；临时用例已删除，不能宣称仓库现有 16 项可直接运行测试。
- `docs/history/acceptance/2026-11-03-auto-off.json` 记载 7 项真实 Qt 循环检查；`2026-11-03-keyboard-only-final.json` 记载 6 项仅键盘/异常恢复等原生检查。这些是历史结果，其测试模块和入口已移除。
- 当前发行包只有四个正式模块，不含 `--acceptance-test`、`--acceptance-crash-child`、`--idle-cycle-check`；内部 `--watch-parent` 必须保留。
- 新一轮验证要记录本轮命令、结果、源码/产物标识和未执行项。不要覆写旧证据，也不要将引用旧结果写成“本轮全部重测通过”。

## 完成审查

检查改变的行为和全部退出路径、用户配置是否保留、说明是否符合当前能力、证据是否对应最终源码。真实 Windows 检查尚未执行时，明确标记；不把 UI 文案、模拟输入或后台状态当成真实熄屏证据。
