# 跨模块与生命周期思考指南

## 改动前

- [ ] 画清实际路径：Qt 操作/计时 → guard → desktop → watchdog ready → Mouse 暂停 → 显示关闭；恢复时哪些步骤可能失败？
- [ ] 手动进入和自动再次熄屏是否仍共用 `Window.enter_mode()`？
- [ ] 新增副作用前是否已具备独立恢复？设备快照、pending 和恢复 ID 范围是否一致？
- [ ] 设置字段是否只有 `load_config()` 一个兼容入口，保存和消费逻辑是否同步？
- [ ] 时间是否全部在各自正确的时钟域内，Win32 最近输入值是否仅用来检测变化？
- [ ] 新导入是否改变 watchdog 的早期分流或 Qt DLL 初始化顺序？

详细合同：[状态机](../desktop/ui-and-state.md)、[设置](../desktop/settings-and-data.md)、[Windows 集成](../desktop/windows-integration.md)、[独立恢复](../desktop/recovery-and-errors.md)。

## 改动后

- [ ] 成功、部分失败、取消、正常关闭和主进程异常结束的资源归属是否清楚？
- [ ] 钩子线程是否仅发事件，由 Qt 主线程更新控件？
- [ ] 测试证明的是业务结果、包匹配，还是真实显示/设备状态？是否在记录中分清？
- [ ] 新模块是否进入构建并加入源码匹配检查？最终桌面 EXE 是否与源码相符？
- [ ] README、规范与本轮验收是否采用相同语义，旧历史证据是否仍标为历史？

检查级别见 [质量与验收](../desktop/quality-guidelines.md)，产物与清理见 [交付规范](../desktop/delivery-and-cleanup.md)。
