# Trellis 现状回填执行清单

- [x] 核对 Git 状态、默认任务、规范模板及开发者身份。
- [x] 通读正式模块、构建/校验脚本、当前与历史验收记录。
- [x] 对照当前源码和 EXE 哈希，确认现有交付基线仍匹配。
- [x] 填写真实桌面应用规范，移除无关后端模板，改写思考指南。
- [x] 补充 AGENTS 入口与任务上下文，校验索引、链接和源码符号。
- [x] 检查当前 EXE、桌面副本及内嵌源码；单独记录本轮结果。
- [x] 区分历史已验收、当前可复核和未专项验证项。
- [x] 确认产品文件、个人配置、EXE 和历史证据未被修改。
- [x] 归档 `00-bootstrap-guidelines`，记录工作日志，确认无活动任务。

## 检查方式

1. `python3 .trellis/scripts/get_context.py --mode packages`：发现 `desktop`。
2. `python3 .trellis/scripts/task.py validate 00-bootstrap-guidelines`：上下文有效。
3. 临时静态检查：本地 Markdown 链接、目录索引、模板残留、源码语法和文档所引符号。检查不导入 Win32 模块，不创建持久测试入口。
4. 使用与构建相同的 Windows Python 3.12 运行 `scripts/verify_package.py`，输出到本任务内的 `package-verification.json`；不覆盖历史构建证据。如果运行环境不可用，明确记录限制。
5. `task.py archive 00-bootstrap-guidelines --no-commit --skip-branch-validation`：此初始化文档任务无独立 PR 分支，保留脚本记录的 main 与未设置的 base_branch，不伪造分支。
6. `add_session.py --no-commit`：记录本轮工作未提交；检查归档状态、上下文和最终文件差异。

本轮不执行真实熄屏或鼠标暂停，不重建业务未改动的 EXE。Windows 功能验证沿用已存在且与源码基线对应的证据。
