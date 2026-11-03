# Windows 桌面程序开发规范

适用范围：四个 `yaoguang_*.py` 正式模块、`scripts/` 构建校验脚本及相关交付说明。架构与当前证据见 [项目入口](../index.md)。

## Guidelines Index

| 文档 | 查阅时机 |
| --- | --- |
| [目录与职责](directory-structure.md) | 定位代码、添加文件、整理产物 |
| [界面与状态机](ui-and-state.md) | 修改 Qt、倒计时或唤醒流程 |
| [设置与本地数据](settings-and-data.md) | 修改字段、默认值、读写与迁移 |
| [Windows 显示与输入](windows-integration.md) | 修改 Win32 绑定、键鼠与设备操作 |
| [独立恢复与错误处理](recovery-and-errors.md) | 修改生命周期、异常或跨进程协议 |
| [日志](logging-guidelines.md) | 添加诊断事件或排查故障 |
| [质量与验收](quality-guidelines.md) | 选择检查方法、评估完成状态 |
| [构建交付与清理](delivery-and-cleanup.md) | 修改构建、交付桌面 EXE、清理文件 |

## Pre-Development Checklist

1. 读取任务 `prd.md`，以及存在的 `design.md`、`implement.md`。
2. 先读目录与职责，再按上表读取实际涉及的规范及对应源码。
3. 涉及进入、恢复或计时的改动，同时读界面与状态机、Windows 集成、独立恢复；不要只看一个模块。
4. 修改字段前查阅设置规范；修改发行程序前查阅交付规范。
5. 跨模块改动先过 [跨层指南](../guides/cross-layer-thinking-guide.md)；新建函数前过 [复用指南](../guides/code-reuse-thinking-guide.md)。

## Quality Check

1. 按 [质量与验收](quality-guidelines.md) 选择与实际改动匹配的检查；记录执行命令与结果，注明历史证据和未执行项。
2. 改动设置时检查旧字段、BOM、类型、边界值及保存失败；改动循环时检查重复进入、活动重置、取消和恢复。
3. 改动设备/原生层时检查本轮设备快照、失败回滚、首次唤醒按键、异常退出和单实例。真实硬件效果不能由 UI 状态或模拟事件代替。
4. 业务源码改动须按 [交付规范](delivery-and-cleanup.md) 重建并核对桌面单文件 EXE；纯文档改动无需重建。
5. 确认个人设置、日志、历史证据和最终产物保留，测试入口不进入正式发行包。
