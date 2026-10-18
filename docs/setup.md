# 安装与恢复

## 运行链路

原生启动器 → 私有 Wine → Windows 战网 → 游戏。Rosetta 2 在 Apple 芯片上转换 Intel 代码，GStreamer 提供多媒体支持。通过独立 `WINEPREFIX` 隔离注册表、游戏和字体。

固定版本见 `dependencies.json`。更新任何依赖时，应重新验证启动、字体、按键、窗口和长时间对局；不要只更新版本号并跳过校验。

## 字体准备

目前脚本支持这组六个文件，文件名匹配不区分大小写：

```text
Simsun.ttc
msyh.ttc
msyhbd.ttc
msyhl.ttc
mingliu.ttc
SimHei.ttf
```

在原型电脑上，字体取自已安装 Microsoft Word 的 `Contents/Resources/DFonts`。如果你拥有同样可用的字体，可将该目录作为 `--fonts-dir`；仓库不提供这些字体。没有这组字体时，需要先设计并测试其他字体方案，不能把任意字体改成这些文件名。

## setup 做了什么

1. 检查目标目录尚不存在、字体齐全且本机有编译工具。
2. 下载固定安装包，或复用 `cache/` 内校验匹配的文件。
3. 单独提取并校验带 Rosetta 修复的 `wow64cpu.dll`。
4. 编译原生 App 与按键动态库。
5. 在临时目录解包 Wine 和 GStreamer，创建私有运行环境；不运行全局 pkg 安装程序。
6. 保存原 Wine 模块和来源记录后，放入经过校验的修复模块。
7. 创建独立 Windows 环境，设置 Wine 的 Command/Option 映射，复制和登记字体。
8. 输出 App，由用户完成战网安装与登录。

大约数百 MB 的下载和更多磁盘空间由实际软件包决定。安装包缓存在仓库的 `cache/`，运行文件在根目录 `~/RA2OLMac`，均已加入 Git 忽略规则。

若软件包内容与固定校验值不同，脚本会停止。先核对官网下载和上游变更，审查新版本后再调整锁文件；不要忽略校验错误。

## 安装平台与游戏

首次打开 App 会启动官网下载的 WinXP–11 通用安装器。安装目录选 `C:\RA2OL`，自行完成许可和账号操作。游戏按平台要求配置；脚本不会分发红警游戏资产。

当前默认游戏目录为 `prefix/drive_c/Ra2Game412`。若平台后续版本使用其他目录，可指定：

```sh
python3 scripts/ra2ol.py display --game-dir "/absolute/path/to/game" --width 2304 --height 1296
```

## 中断后恢复

下载或解包失败且目标目录尚未生成时，可以直接重试 `setup`。目标已经生成而初始化失败时，保留它，按需运行：

```sh
python3 scripts/ra2ol.py initialize
python3 scripts/ra2ol.py fonts --source "/path/to/your/fonts"
```

`initialize` 只接受带有本项目 `.ra2ol-macos` 标记的新环境，不自动改造来源不明的已有环境。

## 备份和迁移

完全退出战网和游戏后，备份生成的 App 与完整 `RA2OLMac` 文件夹。App 内保存的是环境路径，恢复到其他位置后需要使用新 `--base` 重新构建。前缀内可能包含平台账号配置，备份用于个人恢复，不提交到 GitHub。

默认运行位置与 Downloads 无关。确认旧快捷方式没有用途后可以移除；真实运行目录需要保留。
