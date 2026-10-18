# ra2ol-macos

**简体中文** | [English](README.en.md)

在 Apple 芯片 Mac 上，通过专用 Wine 环境运行 [ra2ol 红警战网](https://www.ra2ol.com/)和红色警戒 2。

这是从一台 MacBook Air M3 的实际配置整理出来的 **实验性项目**。包含可编译的 macOS 启动器、依赖准备脚本、Command/Control 映射、大窗口配置和排错记录。当前验证范围为 macOS 15.7.4、Wine Stable 11.0_1；其他系统和平台版本需要重新验证。

## 已实现

- 私有 Wine 和独立 Windows 环境，默认放在 `~/RA2OLMac`。
- 固定 Wine、GStreamer、战网安装器及 Rosetta 修复模块的 SHA256，校验失败即停止。
- 按范围从 CodeWeavers 官方 ZIP 读取单个开源 Wine 模块；不安装 CrossOver 应用。
- 编译支持 arm64 和 x86_64 的原生启动器，内置“强制结束战网和游戏”按钮。
- Command → Windows Ctrl，实体 Control → Windows Alt，Option → Windows Alt。
- 同步设置游戏画面分辨率和显示组件窗口大小，保留修改前备份。
- 中文字体复制与注册、只读环境检查、自动化配置与键盘组件测试。

**验证状态：**原来约一两分钟后退出的问题已修复并通过相同模式、相同地图超过 5 分钟实测；2304×1296 窗口已由使用者确认合适。随后另一次约 22 分钟对局在游戏引擎地址 `00505E41` 报错，仍未修复。实际游戏中的按键映射还需要最终操作反馈。

## 准备条件

1. Apple 芯片 Mac，已安装 Rosetta 2。Intel Mac 尚未实测。
2. Python 3.9 或以上。源码安装或重新编译还需要 Xcode Command Line Tools，可执行 `xcode-select --install`，按系统提示完成。
3. 网络连接和足够的磁盘空间。脚本会下载 Wine、GStreamer 和 Windows 战网安装器。
4. 自行提供有权使用的游戏和中文字体。当前字体方案需要宋体、微软雅黑、新細明體和黑体对应的六个文件，见[安装说明](docs/setup.md)。

## 下载预览版

在 [Releases](https://github.com/CarlCypress/ra2ol-macos/releases) 下载 `ra2ol-macos-<version>-universal.zip` 与 `SHA256SUMS.txt`。解压后阅读 `开始使用.md`，运行 `安装.command`。发布包内含预编译启动器，安装时无需 Xcode 编译工具；仍需要 Python、Rosetta、网络和自备字体。

当前版本为 `0.1.0-alpha.1`，完整游戏稳定性和下载后首次打开流程仍需扩大验证。App 尚无 Developer ID 签名或 Apple 公证，可能需要按 macOS「隐私与安全性」提示允许打开。

## 从源码开始

在仓库根目录执行。将字体路径替换为你自己的目录：

```sh
python3 scripts/ra2ol.py setup --fonts-dir "/path/to/your/fonts"
```

脚本会构建 `dist/红警战网.app`、准备默认环境 `~/RA2OLMac`。把生成的 App 移到“应用程序”，再打开它，由你完成战网安装向导与登录。默认 Windows 安装目录使用 `C:\RA2OL`。

战网准备好游戏文件后，**先退出对局**，再执行：

```sh
python3 scripts/ra2ol.py display --width 2304 --height 1296
```

这是适合 2560×1440 主屏的一组参数。其他屏幕请选择合适的宽高。下一次启动游戏生效。

`setup` 会拒绝覆盖已有的 `~/RA2OLMac`。不要为了运行它删除现有可玩的环境。

## 已有这套修复环境

只读检查，不更改配置：

```sh
python3 scripts/ra2ol.py doctor
```

只编译启动器，不替换现有 App 或游戏环境：

```sh
python3 scripts/ra2ol.py build
```

需要检查新环境时，可为所有命令指定独立根目录，`--base` 放在子命令前：

```sh
python3 scripts/ra2ol.py --base "$HOME/RA2OLMac-test" setup --fonts-dir "/path/to/your/fonts"
python3 scripts/ra2ol.py --base "$HOME/RA2OLMac-test" doctor
```

构建时的根目录会写入生成 App 的设置，移动这个 App 不会自动移动依赖目录。更改根目录后重新 `build`。

## 文档

- [安装与恢复](docs/setup.md)
- [窗口和按键设置](docs/settings.md)
- [闪退 卡死与 Fatal Error](docs/troubleshooting.md)
- [第三方组件与来源](THIRD_PARTY.md)
- [开发和验证](CONTRIBUTING.md)
- [版本与发布](docs/releasing.md)
- [更新记录](CHANGELOG.md)

## 仓库结构

```text
src/launcher/     macOS 启动器
src/keyboard/     Wine 按键组件
scripts/          环境管理、发布打包、提交检查
tests/            Python 配置与打包回归测试
tests/native/     原生按键测试
packaging/        发布包安装入口与入门说明
docs/             安装、设置、排错、版本发布说明
.github/          自动检查、Release 工作流、PR 模板
VERSION           统一版本号
dependencies.json 固定依赖版本、来源与校验值
```

## 项目边界

源码采用 MIT 许可证。第三方软件、游戏、字体各自遵循原有许可证。仓库只提交本项目源码、配置逻辑及文档；运行环境、账号配置、游戏文件、字体与崩溃转储均在本地生成或由用户提供。

本项目与 ra2ol、EA、WineHQ、CodeWeavers 均无隶属关系。这里记录的修复针对特定 Wine/Rosetta 故障，不能保证所有地图、模组和联机模式都不会出现游戏内部错误。
