# 设置与本地数据

来源：`yaoguang_qt.py:ROOT`、`load_config`、`Window.save`。当前只使用本地 JSON，没有数据库、迁移框架、网络同步或注册表设置。

## 文件与字段合同

`ROOT` 在 frozen 程序中取 `Path(sys.executable).parent`，源码模式取当前源文件目录。目录必须可写；不能把用户设置写入 PyInstaller 的临时解包目录 `sys._MEIPASS`。

| 字段 | 保存格式 | 读取行为 |
| --- | --- | --- |
| `autoOffEnabled` | bool，默认 `true` | 按下列旧字段优先级读取；非 bool 保持默认 |
| `idleSeconds` | int，默认 `60` | 兼容 `IdleSeconds`；非 bool 的 int 限制为 10–86400，其他类型保持默认 |

开关查找优先级：`autoOffEnabled` → `AutoOffEnabled` → `autoLockEnabled` → `AutoLockEnabled`。新键存在时，即使类型非法也不会继续采用旧键；校验后保留默认值。旧 `autoLockEnabled` 只作为迁移别名，行为仍是再次熄屏。

`load_config(path)` 使用 `utf-8-sig`，兼容带 BOM 的旧文件。文件缺失直接用默认值；读取/JSON/对象形状错误由现有 `OSError`、`ValueError`、`AttributeError` 分支记录日志并回到默认值。不要将任意字符串强制转换为 bool 或把 `true` 当作秒数。

## 保存模式

当前 `Window.save()` 仅写两个规范字段，未知字段不会保留；从控件读取值后先写同目录 `settings.json.tmp`，再替换正式文件，成功后更新内存配置：

```python
temporary = self.settings_path.with_suffix(".json.tmp")
temporary.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
temporary.replace(self.settings_path)
self.config = config
```

保存失败应通过现有 UI 错误通道报告。不要先截断正式配置，再尝试写入；也不要在验收中覆盖用户已保存的开关或 10 秒等个人设置。

## 修改字段时检查

用临时目录/独立配置检查：文件不存在、BOM、旧字段、新旧冲突、非法对象/JSON、bool/int 区别、10 与 86400 边界、范围外限制、保存往返与写入失败。增加字段时同步 `load_config`、控件初始化、`save`、消费逻辑、README 和包核验。

`settings.json`、`yaoguang.log` 以及 `*.tmp`、旧锁文件名等在 `.gitignore` 中排除。忽略列表里的 `yaoguang.lock` 不代表当前单实例实现使用文件锁；当前使用 Windows 命名互斥量。
