# 开发与验证

## 提交规范

使用 [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/)：`type(scope): description`。标题不超过 100 个字符，scope 可省略，描述使用具体动词，正文解释原因和验证结果。每次提交围绕一个可独立理解的变更。

| 前缀 | 用途 | 示例 |
| --- | --- | --- |
| `feat` | 新功能 | `feat(release): package portable macOS preview` |
| `fix` | 修复行为 | `fix(launcher): expand runtime path for current user` |
| `refactor` | 保持行为的结构调整 | `refactor: separate launcher and keyboard sources` |
| `docs` | 文档 | `docs: explain preview installation` |
| `test` | 测试 | `test(release): check portable app settings` |
| `build` | 构建工具 | `build: centralize application version` |
| `ci` | 自动化流程 | `ci: validate commits and build release drafts` |
| `chore` | 仓库维护、版本 | `chore(release): prepare v0.1.0-alpha.1` |

也接受 `perf` 和 `revert`。不兼容变更在冒号前加 `!`，并在正文解释 `BREAKING CHANGE:`。

启用本地提交检查：

```sh
git config core.hooksPath .githooks
```

CI 会检查分支历史中的提交标题。PR 标题采用同样格式；合并时使用 squash 并核对最终提交信息。历史整理前保留可恢复备份，共享分支改写须先与协作者协调，使用带预期旧提交的 `--force-with-lease`。

## 本地检查

```sh
python3 -m unittest discover -s tests -v
python3 scripts/check_commits.py --range HEAD
python3 scripts/ra2ol.py build
dist/check-key-mapping dist/红警战网.app/Contents/Resources/ControlAsAlt.dylib
codesign --verify --strict dist/红警战网.app
python3 scripts/package_release.py
```

测试覆盖配置继承、专用节覆盖、备份、缺失配置不写入、现有目录保护、下载校验、单模块提取和环境变量隔离。原生测试覆盖左右修饰键、组合和嵌套事件。

macOS 可分别用 `arch -arm64`、`arch -x86_64` 运行构建出的按键测试；后者在 Apple 芯片上需要 Rosetta 2。CI 会运行 Python 测试和 macOS 原生编译/测试。自动化不启动真实对局，也不证明所有模式稳定。

## 验收记录

当前原型来自一台 MacBook Air M3、16 GB、macOS 15.7.4，主屏 2560×1440。

| 项目 | 状态 |
| --- | --- |
| 中文战网界面 | 原型已确认正常 |
| 原 Wine 转换层闪退 | 复现对照及超过 5 分钟相同模式地图对局通过 |
| 2304×1296 窗口 | 使用者已确认合适 |
| 原生按键事件转换 | 自动检查通过；实际游戏操作等待最终确认 |
| 游戏内部错误 00505E41 | 已记录，未修复 |
| 仓库脚本全新环境准备 | 独立临时目录的解包、修复、Wine 初始化、字体注册与键盘设置通过；安装向导后的真实对局尚待验证 |

首次环境准备测试使用了锁文件校验通过的本地官方安装包缓存；修复 DLL 的远程 ZIP 范围下载也已单独通过校验。该测试没有代替用户完成平台安装许可或登录。

## 提交范围

源码、文档、测试、依赖锁文件可以提交。`dist/`、`cache/`、运行前缀、账号配置、字体、游戏、DLL 和个人路径不提交。原型电脑的完整 Word 手册含本机路径，仓库采用重新整理的通用 Markdown 文档。

更换依赖前先解释触发问题、版本与校验来源，再在独立新目录验证。当前按预览版发布，正式版前还需扩大 Mac 型号、显示器、地图及模式的实测范围。发布步骤和打包内容见 [版本与发布](docs/releasing.md)。
