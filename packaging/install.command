#!/bin/bash
set -eu
cd -- "$(dirname -- "$0")"
if ! python3 -c 'import sys; assert sys.version_info >= (3, 9)' 2>/dev/null; then
    echo '请先安装 Python 3.9 或以上版本，再重新运行。'
    read -r -p '按回车键关闭…' unused
    exit 1
fi
echo '请选择你有权使用的中文字体文件夹。所需文件见「开始使用.md」。'
if ! fonts_dir=$(/usr/bin/osascript -e 'POSIX path of (choose folder with prompt "选择包含宋体、微软雅黑、新細明體和黑体的字体文件夹")'); then
    exit 0
fi
if python3 scripts/ra2ol.py setup --fonts-dir "$fonts_dir"; then
    echo '请将 dist/红警战网.app 移入「应用程序」，然后打开以安装战网。'
    read -r -p '按回车键关闭…' unused
else
    echo '环境准备未完成，请保留上方错误信息并查看 docs/troubleshooting.md。'
    read -r -p '按回车键关闭…' unused
    exit 1
fi
