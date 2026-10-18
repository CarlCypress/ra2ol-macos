#!/usr/bin/env python3
"""Build a portable macOS launcher distribution with SHA256 checksums."""
import argparse
import hashlib
from pathlib import Path
import plistlib
import re
import shutil
import tempfile

import ra2ol


def package(output):
    ra2ol.require_mac()
    version = ra2ol.VERSION
    if not re.fullmatch(r'\d+\.\d+\.\d+(?:-(?:alpha|beta|rc)\.\d+)?', version):
        raise ValueError('VERSION 必须为 0.1.0 或 0.1.0-alpha.1 等版本号')
    output = output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    name = f'ra2ol-macos-{version}-universal'
    archive = output / (name + '.zip')
    checksums = output / 'SHA256SUMS.txt'
    if archive.exists() or checksums.exists():
        raise FileExistsError('发布产物已存在，请选择新的输出目录，避免覆盖已发布校验值')
    with tempfile.TemporaryDirectory(prefix='ra2ol-package-') as temp:
        work = Path(temp)
        app = ra2ol.build(work / 'build', Path.home() / 'RA2OLMac')
        ra2ol.run(['/usr/bin/codesign', '--verify', '--strict', app])
        for binary in [app / 'Contents/MacOS/RA2OL', app / 'Contents/Resources/ControlAsAlt.dylib']:
            ra2ol.run(['/usr/bin/lipo', binary, '-verify_arch', 'arm64', 'x86_64'])
        ra2ol.run([work / 'build/check-key-mapping', app / 'Contents/Resources/ControlAsAlt.dylib'])
        settings = plistlib.loads((app / 'Contents/Resources/settings.plist').read_bytes())
        if settings != {'baseDirectory': '~/RA2OLMac'}:
            raise ValueError('发布启动器包含非便携运行目录')
        stage = work / name
        stage.mkdir()
        ra2ol.run(['/usr/bin/ditto', app, stage / app.name])
        for filename in ['VERSION', 'dependencies.json', 'LICENSE', 'THIRD_PARTY.md', 'CHANGELOG.md']:
            shutil.copy2(ra2ol.ROOT / filename, stage / filename)
        (stage / 'scripts').mkdir()
        shutil.copy2(ra2ol.ROOT / 'scripts/ra2ol.py', stage / 'scripts/ra2ol.py')
        shutil.copytree(ra2ol.ROOT / 'docs', stage / 'docs')
        shutil.copy2(ra2ol.ROOT / 'packaging/README.md', stage / '开始使用.md')
        installer = stage / '安装.command'
        shutil.copy2(ra2ol.ROOT / 'packaging/install.command', installer)
        installer.chmod(0o755)
        ra2ol.run(['/usr/bin/ditto', '--norsrc', '--noextattr', '-c', '-k', '--keepParent', stage, archive])
    checksum = hashlib.sha256(archive.read_bytes()).hexdigest()
    checksums.write_text(f'{checksum}  {archive.name}\n')
    print('发布包:', archive)
    print('校验文件:', checksums)
    return archive


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ra2ol.ROOT / 'dist/release')
    args = parser.parse_args()
    package(args.output)
