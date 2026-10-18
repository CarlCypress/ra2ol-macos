#!/usr/bin/env python3
"""Prepare a private, pinned RA2OL Wine environment. Python 3.9+; no pip deps."""
import argparse
import configparser
from datetime import datetime
import hashlib
import io
import json
import os
from pathlib import Path
import platform
import plistlib
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request
import zipfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
LOCK = json.loads((ROOT / 'dependencies.json').read_text())
REL_WINE = Path('runtime/Wine Stable.app/Contents/Resources/wine')
REL_DLL = REL_WINE / 'lib/wine/x86_64-windows/wow64cpu.dll'
GAME_SECTIONS = ('ddraw', 'gamemd', 'gamemd-ares', 'gamemd-spawn')


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def verify(path, expected):
    if digest(path) != expected:
        raise ValueError('SHA256 校验失败，保留原文件，不继续安装: ' + str(path))


def run(args, **kwargs):
    print('+', args[0], flush=True)
    subprocess.run([str(x) for x in args], check=True, **kwargs)


def require_mac():
    if sys.platform != 'darwin':
        raise RuntimeError('此命令需要 macOS；纯配置测试可在其他系统运行。')


def wine_env(base):
    base = Path(base).resolve()
    wine = base / REL_WINE
    gst = base / 'runtime/GStreamer.framework/Versions/1.0'
    env = dict(os.environ)
    for key in ('DYLD_LIBRARY_PATH', 'DYLD_INSERT_LIBRARIES', 'WINEDLLPATH'):
        env.pop(key, None)
    env.update(WINEPREFIX=str(base / 'prefix'), LANG='zh_CN.GBK', LC_ALL='zh_CN.GBK',
               WINEDEBUG='-all', MVK_CONFIG_LOG_LEVEL='0', WINELOADER=str(wine / 'bin/wine'),
               DYLD_FALLBACK_LIBRARY_PATH=f'{wine}/lib:{gst}/lib:/usr/local/lib:/usr/lib',
               GST_PLUGIN_SYSTEM_PATH=str(gst / 'lib/gstreamer-1.0'),
               GST_PLUGIN_SCANNER=str(gst / 'libexec/gstreamer-1.0/gst-plugin-scanner'),
               GST_REGISTRY=str(base / 'gstreamer-registry.bin'))
    return env


def wine_run(base, *args):
    run([base / REL_WINE / 'bin/wine', *args], env=wine_env(base))


def fetch(name, cache):
    spec = LOCK[name]
    path = cache / spec['filename']
    if path.exists():
        verify(path, spec['sha256'])
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    partial = path.with_suffix(path.suffix + '.part')
    print('下载', name, spec.get('version', ''), flush=True)
    try:
        with urllib.request.urlopen(spec['url'], timeout=90) as response, partial.open('wb') as out:
            shutil.copyfileobj(response, out)
        verify(partial, spec['sha256'])
        partial.replace(path)
    finally:
        partial.unlink(missing_ok=True)
    return path


class RemoteZip(io.RawIOBase):
    """Read a fixed ZIP entry without downloading the proprietary app bundle."""
    def __init__(self, url):
        self.url, self.pos = url, 0
        with urllib.request.urlopen(urllib.request.Request(url, method='HEAD'), timeout=30) as r:
            self.size = int(r.headers['Content-Length'])

    def seekable(self): return True
    def readable(self): return True
    def tell(self): return self.pos

    def seek(self, offset, whence=0):
        value = offset if whence == 0 else self.pos + offset if whence == 1 else self.size + offset
        if value < 0:
            raise ValueError('negative ZIP seek')
        self.pos = value
        return value

    def read(self, count=-1):
        count = self.size - self.pos if count < 0 else min(count, self.size - self.pos)
        if count <= 0: return b''
        if count > 8 * 1024 * 1024: raise ValueError('unexpected oversized archive range')
        end = self.pos + count - 1
        request = urllib.request.Request(self.url, headers={'Range': f'bytes={self.pos}-{end}'})
        with urllib.request.urlopen(request, timeout=45) as response:
            expected = f'bytes {self.pos}-{end}/{self.size}'
            if response.status != 206 or response.headers.get('Content-Range') != expected:
                raise ValueError('源站不支持可靠的范围下载；停止提取')
            data = response.read(count + 1)
        if len(data) != count: raise ValueError('incomplete archive range')
        self.pos += count
        return data


def fetch_wow64cpu(cache):
    spec = LOCK['wow64cpu']
    path = cache / 'wow64cpu.dll'
    if path.exists():
        verify(path, spec['sha256'])
        return path
    with zipfile.ZipFile(RemoteZip(spec['url'])) as archive:
        entry = archive.getinfo(spec['member'])
        if entry.file_size > 1024 * 1024: raise ValueError('unexpected module size')
        data = archive.read(entry)
    if hashlib.sha256(data).hexdigest() != spec['sha256']:
        raise ValueError('修复模块 SHA256 校验失败，停止安装')
    cache.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return path


def build(output, base):
    require_mac()
    output.mkdir(parents=True, exist_ok=True)
    app = output / '红警战网.app'
    binary, resources = app / 'Contents/MacOS', app / 'Contents/Resources'
    binary.mkdir(parents=True, exist_ok=True)
    resources.mkdir(parents=True, exist_ok=True)
    flags = ['xcrun', 'clang', '-arch', 'arm64', '-arch', 'x86_64', '-fobjc-arc', '-framework', 'Cocoa']
    run([*flags, '-dynamiclib', ROOT / 'src/keyboard/ControlAsAlt.m', '-o', resources / 'ControlAsAlt.dylib'])
    run([*flags, ROOT / 'src/launcher/Launcher.m', '-o', binary / 'RA2OL'])
    info = dict(CFBundleName='红警战网', CFBundleDisplayName='红警战网',
                CFBundleIdentifier='io.github.ra2ol-macos.launcher', CFBundleVersion='0.1.0',
                CFBundlePackageType='APPL', CFBundleExecutable='RA2OL', NSHighResolutionCapable=True)
    (app / 'Contents/Info.plist').write_bytes(plistlib.dumps(info))
    (resources / 'settings.plist').write_bytes(plistlib.dumps({'baseDirectory': str(base)}))
    run(['/usr/bin/codesign', '--force', '--sign', '-', resources / 'ControlAsAlt.dylib'])
    run(['/usr/bin/codesign', '--force', '--sign', '-', app])
    run([*flags, ROOT / 'tests/native/check-key-mapping.m', '-o', output / 'check-key-mapping'])
    print('已构建:', app)
    return app


def setup(args):
    require_mac()
    base, cache = args.base, args.cache
    if base.exists():
        raise FileExistsError('目标目录已存在，拒绝覆盖: ' + str(base))
    if not args.fonts_dir:
        raise ValueError('请用 --fonts-dir 指定你有权使用的中文字体目录，参见 docs/setup.md')
    # Check fonts and toolchain before any downloads or target-directory writes.
    font_files(args.fonts_dir)
    run(['xcrun', '--find', 'clang'])
    wine_archive = fetch('wine', cache)
    gst_archive = fetch('gstreamer', cache)
    installer = fetch('installer', cache)
    module = fetch_wow64cpu(cache)
    app = build(args.output, base)
    base.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.ra2ol-prepare-', dir=base.parent) as temp:
        stage = Path(temp)
        runtime = stage / 'ready/runtime'
        runtime.mkdir(parents=True)
        unpack = stage / 'wine'; unpack.mkdir()
        # These fixed archives have already passed the pinned SHA256 checks.
        run(['/usr/bin/tar', '-xf', wine_archive, '-C', unpack])
        source = list(unpack.rglob('Wine Stable.app'))
        if len(source) != 1: raise ValueError('Wine 目录结构与固定版本不符')
        run(['/usr/bin/ditto', source[0], runtime / 'Wine Stable.app'])
        package = stage / 'gst'
        run(['/usr/sbin/pkgutil', '--expand-full', gst_archive, package])
        count = 0
        for info in package.rglob('PackageInfo'):
            location = ET.parse(info).getroot().get('install-location', '')
            prefix = '/Library/Frameworks/GStreamer.framework'
            if not location.startswith(prefix + '/') and location != prefix:
                raise ValueError('GStreamer 出现非预期安装路径: ' + location)
            relative = Path(location[len(prefix):].lstrip('/'))
            if '..' in relative.parts: raise ValueError('unsafe framework path')
            payload = info.parent / 'Payload'
            if not payload.is_dir(): raise ValueError('missing expanded GStreamer payload')
            target = runtime / 'GStreamer.framework' / relative
            run(['/usr/bin/ditto', payload, target]); count += 1
        if not count: raise ValueError('GStreamer 安装包内没有组件')
        ready = stage / 'ready'
        diagnostics = ready / 'diagnostics/rosetta-fix'; diagnostics.mkdir(parents=True)
        shutil.copy2(ready / REL_DLL, diagnostics / 'wow64cpu-original.dll')
        shutil.copy2(module, ready / REL_DLL)
        (diagnostics / 'provenance.json').write_text(json.dumps(LOCK['wow64cpu'], indent=2))
        (ready / 'installers').mkdir()
        shutil.copy2(installer, ready / 'installers/ra2ol-legacy-setup.exe')
        (ready / '.ra2ol-macos').write_text('0.1.0\n')
        # Another process might create the destination while downloads are running.
        if base.exists(): raise FileExistsError('目标目录刚刚被创建，拒绝覆盖')
        ready.rename(base)
    initialize(base)
    install_fonts(base, args.fonts_dir)
    print('环境已准备。将此 App 移到应用程序后打开，安装向导由你完成:', app)


def initialize(base):
    require_mac()
    if not (base / '.ra2ol-macos').is_file():
        raise ValueError('initialize 仅用于本项目新建的环境；已有环境请使用独立 configure 命令')
    verify(base / REL_DLL, LOCK['wow64cpu']['sha256'])
    wine_run(base, 'wineboot', '-u')
    # wineboot can return before wineserver flushes the first registry files.
    deadline = time.monotonic() + 45
    while not (base / 'prefix/system.reg').is_file():
        if time.monotonic() >= deadline:
            raise RuntimeError('Wine 首次初始化尚未完成；保留环境，稍后运行 initialize。')
        time.sleep(0.25)
    configure_keyboard(base)


def import_reg(base, text, name):
    destination = base / 'diagnostics' / name
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding='utf-16')
    windows_path = 'Z:' + str(destination.resolve()).replace('/', '\\')
    wine_run(base, 'regedit', '/S', windows_path)


def configure_keyboard(base):
    if not (base / 'prefix/system.reg').exists(): raise ValueError('Wine 环境尚未初始化')
    text = 'Windows Registry Editor Version 5.00\r\n\r\n'
    text += '[HKEY_CURRENT_USER\\Software\\Wine\\Mac Driver]\r\n'
    text += ''.join(f'"{key}"="Y"\r\n' for key in
                    ['LeftCommandIsCtrl', 'RightCommandIsCtrl', 'LeftOptionIsAlt', 'RightOptionIsAlt'])
    import_reg(base, text, 'keyboard.reg')
    print('已设置 Command→Ctrl、Option→Alt；实体 Control→Alt 由 App 内组件处理。')


FONT_NAMES = {
    'simsun.ttc': ('Simsun.ttc', 'SimSun & NSimSun (TrueType)'),
    'msyh.ttc': ('msyh.ttc', 'Microsoft YaHei & Microsoft YaHei UI (TrueType)'),
    'msyhbd.ttc': ('msyhbd.ttc', 'Microsoft YaHei Bold & Microsoft YaHei UI Bold (TrueType)'),
    'msyhl.ttc': ('msyhl.ttc', 'Microsoft YaHei Light & Microsoft YaHei UI Light (TrueType)'),
    'mingliu.ttc': ('mingliu.ttc', 'MingLiU & PMingLiU (TrueType)'),
    'simhei.ttf': ('SimHei.ttf', 'SimHei (TrueType)'),
}


def font_files(source):
    files = {p.name.lower(): p for p in source.iterdir() if p.is_file()}
    missing = FONT_NAMES.keys() - files.keys()
    if missing: raise ValueError('缺少当前字体方案所需文件: ' + ', '.join(sorted(missing)))
    return files


def install_fonts(base, source):
    require_mac()
    if not (base / 'prefix/system.reg').exists(): raise ValueError('Wine 环境尚未初始化')
    files = font_files(source)
    target = base / 'prefix/drive_c/windows/Fonts'
    target.mkdir(parents=True, exist_ok=True)
    for key, (name, family) in FONT_NAMES.items(): shutil.copy2(files[key], target / name)
    text = 'Windows Registry Editor Version 5.00\r\n\r\n'
    for key in [r'HKEY_LOCAL_MACHINE\Software\Microsoft\Windows NT\CurrentVersion\Fonts',
                r'HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion\Fonts']:
        text += f'[{key}]\r\n'
        text += ''.join(f'"{family}"="{name}"\r\n' for name, family in FONT_NAMES.values())
        text += '\r\n'
    text += '[HKEY_LOCAL_MACHINE\\Software\\Microsoft\\Windows NT\\CurrentVersion\\FontSubstitutes]\r\n'
    text += '"MS Shell Dlg"="SimSun"\r\n"MS Shell Dlg 2"="Tahoma"\r\n'
    import_reg(base, text, 'fonts.reg')
    wine_run(base, 'wineboot', '-u')
    print('中文字体已复制并登记；请退出后重新打开战网。')


def update_ini(text, updates):
    """Preserve comments and unrelated settings; replace duplicate target keys."""
    updates = {s.lower(): {k.lower(): str(v) for k, v in data.items()} for s, data in updates.items()}
    output, section, seen, found = [], None, set(), set()
    def finish():
        if section in updates:
            output.extend(f'{key}={value}' for key, value in updates[section].items() if key not in seen)
    for line in text.splitlines():
        header = re.match(r'^\s*\[([^]]+)\]', line)
        if header:
            finish(); section = header[1].lower(); seen = set(); found.add(section)
            output.append(line); continue
        item = re.match(r'^\s*([^;#=]+?)\s*=', line)
        key = item[1].strip().lower() if item else None
        if section in updates and key in updates[section]:
            if key not in seen: output.append(f'{key}={updates[section][key]}')
            seen.add(key)
        else: output.append(line)
    finish()
    for section in updates.keys() - found:
        output.extend(['', f'[{section}]', *(f'{k}={v}' for k, v in updates[section].items())])
    return '\r\n'.join(output) + '\r\n'


def configure_display(base, game, width, height):
    if not 640 <= width <= 2560 or not 480 <= height <= 1600:
        raise ValueError('此版本仅接受 640–2560 宽、480–1600 高；参见已知限制。')
    if not game.is_dir() or not (game / 'RA2MD.ini').is_file():
        raise ValueError('未发现游戏配置；请先通过战网准备游戏，或指定 --game-dir。')
    backup = base / 'diagnostics' / datetime.now().strftime('display-%Y%m%d-%H%M%S-%f')
    config = dict(width=width, height=height, fullscreen='false', windowed='true', border='true',
                  devmode='true', posX=-32000, posY=-32000)
    changes = []
    for folder in [game, game / 'HT']:
        for filename, settings in [('ddraw.ini', {s: config for s in GAME_SECTIONS}),
                                   ('RA2MD.ini', {'Video': dict(ScreenWidth=width, ScreenHeight=height,
                                                             Windowed='no', **{'Video.Windowed': 'False'})})]:
            path = folder / filename
            if not path.exists(): continue
            raw = path.read_bytes()
            encoding = 'utf-8'
            try: text = raw.decode(encoding)
            except UnicodeDecodeError: encoding = 'gb18030'; text = raw.decode(encoding)
            changes.append((path, raw, update_ini(text, settings).encode(encoding)))
    if not any(path.name == 'ddraw.ini' for path, _, _ in changes):
        raise ValueError('缺少 ddraw.ini；未修改配置，请先确认游戏显示组件。')
    backup.mkdir(parents=True)
    for path, raw, new in changes:
        saved = backup / path.relative_to(game); saved.parent.mkdir(parents=True, exist_ok=True); saved.write_bytes(raw)
        temporary = path.with_name(path.name + '.ra2ol-new'); temporary.write_bytes(new); temporary.replace(path)
    print(f'已设置 {width}×{height} 带边框窗口，下次对局生效。备份: {backup}')


def doctor(base):
    print('系统:', platform.system(), platform.machine(), platform.mac_ver()[0])
    print('环境目录:', base)
    for name, path in [('Wine', base / REL_WINE / 'bin/wine'),
                       ('GStreamer', base / 'runtime/GStreamer.framework/Versions/1.0/lib'),
                       ('Windows 环境', base / 'prefix/system.reg'),
                       ('平台', base / 'prefix/drive_c/RA2OL/HTPlatform.exe')]:
        print(name + ':', '存在' if path.exists() else '未找到')
    module = base / REL_DLL
    print('Rosetta 修复:', '校验通过' if module.exists() and digest(module) == LOCK['wow64cpu']['sha256'] else '未匹配固定修复版本')
    game = base / 'prefix/drive_c/Ra2Game412'
    log = game / 'syringe.log'
    if log.exists():
        text = log.read_text(errors='replace')
        if 'at 0x00505E41' in text:
            print('最近日志包含游戏引擎错误 00505E41；具体触发条件待确认，见 docs/troubleshooting.md')
    ini = game / 'ddraw.ini'
    if ini.exists():
        c = configparser.RawConfigParser(strict=False); c.read(ini)
        for section in GAME_SECTIONS:
            if c.has_section(section):
                print(section, {k: c.get(section, k, fallback='未设置') for k in ['width', 'height', 'windowed']})


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', type=lambda p: Path(p).expanduser().resolve(), default=Path.home() / 'RA2OLMac')
    commands = parser.add_subparsers(dest='command', required=True)
    for name in ['build', 'setup']:
        p = commands.add_parser(name)
        p.add_argument('--output', type=Path, default=ROOT / 'dist')
        if name == 'setup':
            p.add_argument('--cache', type=lambda s: Path(s).expanduser(), default=ROOT / 'cache')
            p.add_argument('--fonts-dir', type=lambda s: Path(s).expanduser())
    commands.add_parser('doctor')
    commands.add_parser('initialize')
    commands.add_parser('configure-keyboard')
    commands.add_parser('stop')
    fonts = commands.add_parser('fonts'); fonts.add_argument('--source', type=lambda s: Path(s).expanduser(), required=True)
    display = commands.add_parser('display')
    display.add_argument('--width', type=int, default=2304)
    display.add_argument('--height', type=int, default=1296)
    display.add_argument('--game-dir', type=lambda s: Path(s).expanduser())
    args = parser.parse_args(argv)
    try:
        if args.command == 'build': build(args.output.resolve(), args.base)
        elif args.command == 'setup': setup(args)
        elif args.command == 'doctor': doctor(args.base)
        elif args.command == 'initialize': initialize(args.base)
        elif args.command == 'configure-keyboard': require_mac(); configure_keyboard(args.base)
        elif args.command == 'fonts': install_fonts(args.base, args.source)
        elif args.command == 'display': configure_display(args.base, args.game_dir or args.base / 'prefix/drive_c/Ra2Game412', args.width, args.height)
        elif args.command == 'stop':
            require_mac()
            if not (args.base / 'prefix/system.reg').exists(): raise ValueError('目标环境不存在')
            run([args.base / REL_WINE / 'bin/wineserver', '-k'], env=wine_env(args.base))
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError, zipfile.BadZipFile) as exc:
        print('错误:', exc, file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
