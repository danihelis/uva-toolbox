#!/usr/bin/env python

import os
import sys
from pathlib import Path


def load(filename):
    if not os.path.isfile(filename):
        print('File not found:', filename)
        sys.exit(1)
    with open(filename, 'r') as stream:
        return stream.readlines()


def annotate(header, notice, filename, update):
    content = load(filename)
    start = 0, existing = None
    for index, line in enumerate(content):
        if index == start and line.startswith('#!'):
            start = index + 1
            continue
        if line == notice[0]:
            existing = line
            break
    if existing is not None:
        if not update:
            return
        del content[existing - len(header):existing + len(notice)]
    content[start:start] = header + notice
    with open(filename, 'w') as stream:
        stream.write(''.join(content))
    print(filename)


def annotate_files(header, notice, files, update):
    for file in files:
        annotate(header, notice, file, update)


def annotate_python(header, notice, path, update):
    header = ['# %s' % line for line in header]
    notice = ['# %s' % line for line in notice]
    annotate_files(header, notice, path.rglob('*.py'), update)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage:  %s  directory  [header]  [notice]' % sys.argv[0])
        sys.exit(2)
    path = Path(sys.argv[1])
    header = load(sys.argv[2] if len(sys.argv) >= 2 else 'copyright-header')
    notice = load(sys.argv[3] if len(sys.argv) >= 3 else 'copyright-notice')
    annotate_python(header, notice, path, False)
