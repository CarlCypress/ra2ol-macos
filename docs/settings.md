# 窗口与按键

## 显示

本机已确认适合 2560×1440 横屏的窗口为 2304×1296。`display` 同时修改游戏内部 `RA2MD.ini` 和显示组件 `ddraw.ini`，并同步现有 `HT` 子目录内的副本。

```sh
python3 scripts/ra2ol.py display --width 2304 --height 1296
```

执行前先结束对局。原文件保存在 `RA2OLMac/diagnostics/display-时间戳/`。恢复时先退出游戏，再把所需备份文件复制回原位置。

游戏内部 `[Video]` 保持 `Windowed=no`、`Video.Windowed=False`，由 cnc-ddraw 类组件提供外部窗口。`ddraw.ini` 中的 `[ddraw]`、`[gamemd]`、`[gamemd-ares]` 和 `[gamemd-spawn]` 同时设置宽高、`windowed=true`、`fullscreen=false`、`border=true`、`devmode=true`。

`devmode=true` 不锁定鼠标，方便故障时切换到启动器。本脚本保留原渲染器和鼠标处理设置。游戏专用节可以覆盖通用节，因此不能只改文件顶部的宽高。

为保持当前验证范围，脚本接受宽 640–2560、高 480–1600。更大的内部游戏分辨率可能触发旧引擎限制，需要另行验证。

## 按键

| Mac 实体键 | Windows 游戏接收到的目标键 |
| --- | --- |
| Command | Ctrl |
| Control | Alt |
| Option | Alt |

Command 和 Option 使用 Wine 的 `Mac Driver` 注册表设置，左右键均设置。实体 Control 由 `ControlAsAlt.dylib` 在 Wine 窗口事件中转换，不安装全局键盘钩子，不改变 macOS 系统键盘设置。

新环境由 `setup` 设置注册表。需要重设时：

```sh
python3 scripts/ra2ol.py configure-keyboard
```

通过构建出来的 App 启动，才能加载 App 中的按键组件。直接运行其他 Wine 入口不保证相同映射。

原型已检查左右键、混合组合键、松键及 Wine 嵌套事件；但这不能替代真实游戏中的操作测试。报告问题时记录“哪个实体键、配合什么操作、期待结果、实际结果”。
