# 版本与发布

## 版本来源

`VERSION` 是唯一版本来源。预览版使用 `0.1.0-alpha.1`，对应 Git 标签 `v0.1.0-alpha.1`。App 的数字版本使用 `0.1.0`，完整版本保存在 `RA2OLReleaseVersion`。

## 发布内容

发布 `ra2ol-macos-<version>-universal.zip` 与 `SHA256SUMS.txt`。ZIP 仅包含本项目编译产物、安装工具、依赖锁文件、许可和使用说明。第三方运行组件安装时获取，游戏、字体、账号、prefix、缓存和诊断转储不进入发行包。

当前提供预览版 ZIP。完整 PKG/DMG 安装器、Developer ID 签名和 Apple 公证尚未实现。

## 本地构建

```sh
python3 -m unittest discover -s tests -v
python3 scripts/package_release.py
cd dist/release
shasum -a 256 -c SHA256SUMS.txt
```

打包命令会编译 App、检查两种架构与签名、运行原生按键测试、验证默认目录可跨账号展开，然后仅复制明确列出的发布文件。安装包与源码构建共用版本和依赖锁文件。重新打包时使用新的 `--output` 目录，避免覆盖已发布的校验值。

## GitHub 发布流程

1. 更新 `VERSION`、`CHANGELOG.md` 与 `docs/releases/v<version>.md`，提交检查通过后同步到主分支。
2. 创建带说明的标签并推送：

   ```sh
   git tag -a v0.1.0-alpha.1 -m "chore(release): v0.1.0-alpha.1"
   git push origin v0.1.0-alpha.1
   ```

3. `Release` 工作流验证标签和版本一致、测试与打包后，上传附件并创建 GitHub Release 草稿。带 `alpha` / `beta` / `rc` 的版本标记为预发布。
4. 下载附件核对校验值和首次运行表现，核对说明里的验证边界，然后发布草稿。

可手动运行工作流并输入已有标签重试。若已存在同名 Release，流程会停止；先检查已有附件，避免覆盖已发布文件。

版本标签只指向完成验证的提交。正式发布后通过新版本修复，不移动已发布标签。
