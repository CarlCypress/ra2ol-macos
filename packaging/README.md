# 红警战网 macOS 预览版

这是实验性版本。已在 MacBook Air M3、macOS 15.7.4 验证部分功能；Intel Mac 尚未实测。约 22 分钟对局出现过游戏内部错误 `00505E41`，仍未修复，详见 `docs/troubleshooting.md`。

## 首次安装

1. 准备 Rosetta 2、Python 3.9 或以上版本、网络连接和有权使用的中文字体。
2. 字体文件夹需要包含 `Simsun.ttc`、`msyh.ttc`、`msyhbd.ttc`、`msyhl.ttc`、`mingliu.ttc`、`SimHei.ttf`。详见 `docs/setup.md`。
3. 将整个解压后的文件夹放到可写目录，双击 `安装.command`，选择字体文件夹，等待依赖下载与初始化。
4. 将生成的 `dist/红警战网.app` 移入「应用程序」并打开。由你完成战网安装许可、安装向导与登录，默认选择 `C:\RA2OL`。

也可以从终端进入解压目录运行：

```sh
python3 scripts/ra2ol.py setup --fonts-dir "/path/to/your/fonts"
```

此包带预编译的通用启动器和按键组件，安装时无需编译。Wine、GStreamer 与修复模块在安装时从锁文件指定来源获取；游戏和字体由你提供。

## 已有运行环境

如果已有可玩的 `~/RA2OLMac`，不要重复安装或删除原环境。可以先只读检查：

```sh
python3 scripts/ra2ol.py doctor
```

本包根目录的 `红警战网.app` 默认使用当前用户的 `~/RA2OLMac`，可用于已有默认环境。自定义运行目录请参考 `docs/setup.md`。

## macOS 首次打开

App 只有本地临时签名，尚未使用 Developer ID 签名或 Apple 公证。下载后可能受到 Gatekeeper 拦截。确认来源和校验值后，按 macOS「系统设置 → 隐私与安全性」中的提示允许打开；若仍被拦截，请保留错误文本报告问题。此版本的安装命令和 App 仍需在另一台 Mac 验证下载后的首次运行。

## 校验下载

将 ZIP 和 `SHA256SUMS.txt` 放在同一目录，运行：

```sh
shasum -a 256 -c SHA256SUMS.txt
```

文件名含 universal 表示启动器包含 arm64 和 x86_64 两种架构，不代表 Intel Mac 已通过完整对局验证。
