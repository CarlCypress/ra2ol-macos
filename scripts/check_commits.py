#!/usr/bin/env python3
"""Check commit subjects or a commit-message file against project conventions."""
import argparse
from pathlib import Path
import re
import subprocess

SUBJECT = re.compile(r'^(feat|fix|docs|refactor|test|build|ci|chore|perf|revert)(\([a-z0-9][a-z0-9/_-]*\))?!?: \S.*$')


def valid(subject):
    return len(subject) <= 100 and bool(SUBJECT.fullmatch(subject))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument('--message-file', type=Path)
    source.add_argument('--range', dest='revision')
    args = parser.parse_args()
    if args.message_file:
        lines = args.message_file.read_text().splitlines()
        subjects = [lines[0] if lines else '']
    else:
        subjects = subprocess.check_output(['git', 'log', '--format=%s', args.revision], text=True).splitlines()
    bad = [subject for subject in subjects if not valid(subject)]
    for subject in bad:
        print('提交标题不符合规范:', subject)
    if bad:
        print('格式: type(scope): description；不超过 100 个字符。详见 CONTRIBUTING.md。')
    return bool(bad)


if __name__ == '__main__':
    raise SystemExit(main())
