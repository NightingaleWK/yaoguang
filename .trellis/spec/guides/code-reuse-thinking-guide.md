# 代码复用思考指南

## 先查现有拥有者

```bash
rg -n 'enter_mode|display|signal|restore_devices|load_config|watchdog' yaoguang_*.py scripts
```

- [ ] 新行为能否沿用 `Window.enter_mode/exit_mode/recover`，而不是给自动分支复制一套保护流程？
- [ ] 设备恢复能否继续共用 `restore_devices()`，让正常退出和独立 watchdog 使用同一 ID 范围？
- [ ] 配置读取是否继续经过 `load_config()`，避免另起一套旧字段转换？
- [ ] 打包与验收是否继续使用现有 `scripts/` 入口，避免重复脚本与旧 EXE 混淆？

## 决定是否抽象

- [ ] 共享的是同一业务合同，还是恰巧相同的数字/字符串？只有必须一起变化的概念才适合集中。
- [ ] 抽取会不会把 Qt、设备层和独立恢复的生命周期耦合起来？保持现有职责边界。
- [ ] 小型平铺程序是否真的需要新目录/公共框架？不要为单次调用增加分层。
- [ ] 改动常量、状态或字段后，是否用 `rg` 找齐消费处和说明？

真实示例与边界见 [目录与职责](../desktop/directory-structure.md) 和 [状态机](../desktop/ui-and-state.md)。本项目是 Trellis 使用方，不维护 Trellis 上游模板，无需执行模板同步或编辑全局安装包。
