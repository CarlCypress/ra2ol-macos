# 第三方组件与来源

本项目的 MIT 许可证仅覆盖本仓库原创代码与文档。第三方软件、游戏和字体保留各自权利与许可证。仓库不包含其二进制文件。

| 组件 | 来源和处理 |
| --- | --- |
| Wine Stable 11.0_1 | [Gcenx 的 WineHQ macOS 包](https://github.com/Gcenx/macOS_Wine_builds)，下载后解包为专用副本，保留包内许可证 |
| GStreamer 1.28.6 | [项目官方下载](https://gstreamer.freedesktop.org/download/)，展开官方 pkg 到私有 framework，保留其中的许可证与资料 |
| Windows 版战网 | [ra2ol 官网](https://www.ra2ol.com/)，下载 WinXP–11 通用安装器，用户自行完成安装和许可操作 |
| wow64cpu.dll | [CodeWeavers CrossOver 26.3.0 官方 ZIP](https://media.codeweavers.com/pub/crossover/cxmac/demo/crossover-26.3.0.zip)中的开源 Wine 模块，仅按范围读取一个 DLL，并核验固定 SHA256 |
| 游戏 | 用户自行取得并按平台要求配置，仓库不提供游戏资产 |
| 字体 | 用户提供有权使用的本机字体，仓库不附带字体 |

## Rosetta 修复依据

- [WineHQ 60034 讨论](https://list.winehq.org/hyperkitty/list/wine-bugs@list.winehq.org/thread/SKCHXYF7PVVEPIGYWREW4SSRJNCL5YXL/)
- [WineHQ 附件 81767 补丁](https://bugs.winehq.org/attachment.cgi?id=81767)
- [Wine LGPL 2.1 许可证](https://gitlab.winehq.org/wine/wine/-/blob/wine-11.0/COPYING.LIB)
- [CodeWeavers 源码说明](https://www.codeweavers.com/crossover/source)

脚本保存被替换的原 DLL 和模块来源记录。当前仓库只记录下载位置和校验值；如果今后打包分发第三方二进制，需要先落实对应版本的许可证、通知和源码提供义务，不能仅沿用本仓库 MIT 许可。
