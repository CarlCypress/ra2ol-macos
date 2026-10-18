# ra2ol-macos

**English** | [简体中文](README.zh-CN.md)

Run the [ra2ol multiplayer platform](https://www.ra2ol.com/) and Red Alert 2 on an Apple silicon Mac using a dedicated Wine environment.

This is an **experimental project** based on a working setup on a MacBook Air M3. It includes a native macOS launcher, dependency setup scripts, Command/Control key mapping, window configuration, and troubleshooting notes. The current validation covers macOS 15.7.4 and Wine Stable 11.0_1; other system and platform versions need separate testing.

## Features

- Private Wine runtime and an isolated Windows environment, stored in `~/RA2OLMac` by default.
- Pinned SHA256 checksums for Wine, GStreamer, the platform installer, and the Rosetta fix module. Setup stops if verification fails.
- HTTP range requests to retrieve a single open-source Wine module from the official CodeWeavers ZIP, without installing the CrossOver application.
- A universal native launcher containing arm64 and x86_64 binaries, with a button to force quit the platform and game.
- Command → Windows Ctrl, physical Control → Windows Alt, and Option → Windows Alt.
- Coordinated game resolution and display-component window settings, with backups before changes.
- Chinese font installation and registration, read-only environment diagnostics, and automated configuration and keyboard-component tests.

**Validation status:** The original exit after roughly one or two minutes was fixed, and a session using the same mode and map ran for more than five minutes. The user confirmed that the 2304×1296 window size was suitable. A later session failed after approximately 22 minutes at game-engine address `00505E41`; this remains unresolved. The key mapping still needs final confirmation during actual gameplay.

## Requirements

1. An Apple silicon Mac with Rosetta 2 installed. Intel Macs have not been tested.
2. Python 3.9 or later. Installing from source or rebuilding also requires Xcode Command Line Tools; run `xcode-select --install` and follow the system prompts.
3. Internet access and sufficient disk space. Setup downloads Wine, GStreamer, and the Windows platform installer.
4. Your own game files and Chinese fonts that you are authorized to use. The current font configuration requires six files for SimSun, Microsoft YaHei, MingLiU, and SimHei; see the [setup guide](docs/setup.md), currently in Chinese.

## Download the preview

Download `ra2ol-macos-<version>-universal.zip` and `SHA256SUMS.txt` from [Releases](https://github.com/CarlCypress/ra2ol-macos/releases). Extract the ZIP, read `开始使用.md` (Getting started), and run `安装.command` (Install). The release bundle includes a precompiled launcher, so installation does not require Xcode build tools. Python, Rosetta, internet access, and your own fonts are still required.

The current version is `0.1.0-alpha.1`. Game stability and the first launch after downloading still need broader testing. The App does not yet have a Developer ID signature or Apple notarization; macOS may require you to allow it in System Settings → Privacy & Security.

This language switch changes the repository README. The launcher, installer messages, bundled getting-started guide, and detailed documentation are currently in Simplified Chinese.

## Install from source

Run this from the repository root, replacing the font path with your own:

```sh
python3 scripts/ra2ol.py setup --fonts-dir "/path/to/your/fonts"
```

Setup builds `dist/红警战网.app` and prepares the default environment at `~/RA2OLMac`. Move the generated App to Applications and open it, then complete the platform installation wizard and sign in yourself. Use the default Windows installation directory `C:\RA2OL`.

After the platform has prepared the game files, **exit any active game session** before running:

```sh
python3 scripts/ra2ol.py display --width 2304 --height 1296
```

These dimensions suit the tested 2560×1440 main display. Choose suitable dimensions for other displays. Changes take effect in the next game session.

`setup` refuses to overwrite an existing `~/RA2OLMac`. Keep your working environment rather than deleting it to rerun setup.

## Use an existing environment

Inspect the environment without changing its configuration:

```sh
python3 scripts/ra2ol.py doctor
```

Build the launcher without replacing your installed App or game environment:

```sh
python3 scripts/ra2ol.py build
```

To test a separate environment, specify its root directory with `--base` before the subcommand:

```sh
python3 scripts/ra2ol.py --base "$HOME/RA2OLMac-test" setup --fonts-dir "/path/to/your/fonts"
python3 scripts/ra2ol.py --base "$HOME/RA2OLMac-test" doctor
```

The generated App stores its environment location. The default `~/RA2OLMac` expands to the current user's home directory; a custom location remains explicit. Moving the App does not move its dependencies. Run `build` again with the new `--base` after changing the environment location.

## Documentation

The detailed guides below are currently in Simplified Chinese.

- [Installation and recovery](docs/setup.md)
- [Window and keyboard settings](docs/settings.md)
- [Crashes, hangs, and Fatal Error](docs/troubleshooting.md)
- [Third-party components and sources](THIRD_PARTY.md)
- [Development and validation](CONTRIBUTING.md)
- [Versioning and releases](docs/releasing.md)
- [Changelog](CHANGELOG.md)

## Repository layout

```text
src/launcher/     Native macOS launcher
src/keyboard/     Wine keyboard component
scripts/          Environment management, release packaging, commit checks
tests/            Python configuration and packaging regression tests
tests/native/     Native keyboard tests
packaging/        Release installation entry point and getting-started guide
docs/             Setup, settings, troubleshooting, and release guides
.github/          Automated checks, release workflow, and PR template
VERSION           Single source of truth for the project version
dependencies.json Pinned dependency versions, sources, and checksums
```

## Scope and licensing

The project source code is licensed under MIT. Third-party software, games, and fonts remain subject to their respective licenses. The repository contains project source, configuration logic, and documentation. Runtime environments, account settings, game files, fonts, and crash dumps are generated locally or supplied by the user.

This project is not affiliated with ra2ol, EA, WineHQ, or CodeWeavers. The documented fix addresses a specific Wine/Rosetta failure; game-engine errors may still occur in other maps, mods, and multiplayer modes.
