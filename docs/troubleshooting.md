# 故障排查

## 先检查环境

```sh
python3 scripts/ra2ol.py doctor
```

此命令只读检查运行路径、依赖、固定修复模块和窗口设置。它不读取平台 `Config.ini`，也不会上传日志。

## 一两分钟后退出或卡住

原型曾在 `wow64cpu+0x1139` 以错误模式执行指令并尝试读取 `0x4ECD`。症状和 [WineHQ 60034 后续讨论](https://list.winehq.org/hyperkitty/list/wine-bugs@list.winehq.org/thread/SKCHXYF7PVVEPIGYWREW4SSRJNCL5YXL/)中 Rosetta 模式切换故障吻合。

当前私有 Wine 中加入带修复的 `wow64cpu.dll`。离线重写代码复现程序在原环境失败，修复环境中 8 个独立进程、共 800 次操作通过；实际同模式同地图超过 5 分钟正常。来源和 SHA256 见锁文件、第三方说明。

这项结果仅覆盖该转换层问题，不代表所有内部错误均已解决。不要用原版 Wine 直接覆盖私有运行环境。

## 运行较长时间后的 00505E41

另一次原型对局在运行约 22 分钟后发生 `C0000005 at 00505E41`，读取 `0xDF8`。这个地址在游戏引擎内，与上述 Wine 错误位置不同。

[Phobos 官方错误数据库](https://github.com/Phobos-developers/Phobos/blob/develop/gamemd.edb)把它关联到不能正常建造基地的 AI 阵营取得建造厂后进入基地规划流程。例如心控基地车释放给中立方，或中立工程师占领建造厂。数据库注明地址只是原因提示，需要结合当局状态核对。

**此问题尚未修复，具体触发事件尚未确认。** Windows 上也可能出现类似游戏错误。现有证据不足以把它归因于文件迁移、窗口或按键设置。对战中不要擅自替换引擎或规则文件，以免版本与房间要求不一致。

暂时可避免让心控基地车在原玩家出局后释放到中立方；若相同地图反复触发，保留模式、地图、阵营与错误快照供平台或地图作者定位。

## 应用没有响应

切回原生启动器点击“强制结束战网和游戏”。也可以在核对 `--base` 后使用：

```sh
python3 scripts/ra2ol.py stop
```

它只向指定独立前缀的私有 wineserver 请求结束，会中断该环境的对局。不要使用全局 `killall wine` 等方式结束不相关的 Wine 软件。

## 中文字体加载失败

确认字体目录中六个文件完整、字体注册发生在同一个前缀，并通过专用 App 启动。仅文件改名不能修复字体族匹配。重新登记后退出战网并重新启动：

```sh
python3 scripts/ra2ol.py fonts --source "/path/to/your/fonts"
```

## 提交问题时保留什么

- macOS、芯片型号、Wine 和平台版本。
- 模式、地图、阵营、运行时长、出错前操作。
- `gui-launch-fixed-时间戳.log` 中相关段落。
- 游戏目录的 `syringe.log`、`debug/snapshot-时间戳/except.txt`。

完整转储可能很大且含内存信息，先提供文本摘要。不要把账号配置、整个 prefix 或游戏资产提交进仓库。问题表单只需提交你检查过的必要信息。
