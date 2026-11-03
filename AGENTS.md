<!-- TRELLIS:START -->
# Trellis Instructions

These instructions are for AI assistants working in this project.

This project is managed by Trellis. The working knowledge you need lives under `.trellis/`:

- `.trellis/workflow.md` — development phases, when to create tasks, skill routing
- `.trellis/spec/` — package- and layer-scoped coding guidelines (read before writing code in a given layer)
- `.trellis/workspace/` — per-developer journals and session traces
- `.trellis/tasks/` — active and archived tasks (PRDs, research, jsonl context)

If a Trellis command is available on your platform (e.g. `/trellis:finish-work`, `/trellis:continue`), prefer it over manual steps. Not every platform exposes every command.

If you're using Codex or another agent-capable tool, additional project-scoped helpers may live in:
- `.agents/skills/` — reusable Trellis skills
- `.codex/agents/` — optional custom subagents

Managed by Trellis. Edits outside this block are preserved; edits inside may be overwritten by a future `trellis update`.

<!-- TRELLIS:END -->

## Yaoguang 项目入口

这是 Python + Qt 的 Windows 本地下班熄屏工具，当前交付 `YaoguangQt.exe`。

- 先读 `.trellis/spec/index.md` 和 `.trellis/spec/desktop/index.md`，按任务涉及的主题读取具体规范。
- 修改进入、唤醒、再次熄屏或退出路径时，同时核对 Qt 状态机、Mouse 设备保护和独立恢复进程。
- 当前使用说明见 `README.md`，当前验收见 `docs/验收记录-2026-11-03.md`；`docs/history/` 中的旧测试入口和旧产物标识只用于历史追溯。
- 正式源码修改须交付并核对与最终源码一致的桌面单文件 EXE；纯文档修改无需重建。保留用户配置、日志、开发环境及真实验收证据，按 `.trellis/spec/desktop/delivery-and-cleanup.md` 执行。
