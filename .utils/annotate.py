#!/usr/bin/env python

# utb: UVa Online Judge toolbox
# Copyright (C) 2024-2025  Daniel Donadon
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os
import re
import sys
from pathlib import Path


def load(filename):
    if not os.path.isfile(filename):
        print('File not found:', filename)
        sys.exit(1)
    with open(filename, 'r') as stream:
        return stream.readlines()


def annotate(header, notice, filename):
    content = load(filename)
    start, existing = 0, None
    for index, line in enumerate(content):
        if index == start and line.startswith('#!'):
            start = index + 1
            continue
        if line == notice[0]:
            existing = index
            break
    if existing is not None:
        start = existing - len(header)
        del content[start:existing + len(notice)]
    content[start:start] = header + notice
    with open(filename, 'w') as stream:
        stream.write(''.join(content))
    print(filename)


def annotate_files(header, notice, files):
    for file in files:
        annotate(header, notice, file)


def clean(line):
    return re.sub(r'\s+\n$', '\n', line)


def annotate_python(header, notice, path):
    header.append('\n')
    header = [clean(f'# { line }') for line in header]
    notice = [clean(f'# { line }') for line in notice]
    annotate_files(header, notice, path.rglob('*.py'))


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage:  %s  directory  [header]  [notice]' % sys.argv[0])
        sys.exit(2)
    path = Path(sys.argv[1])
    header = load(sys.argv[2] if len(sys.argv) > 2 else 'copyright-header')
    notice = load(sys.argv[3] if len(sys.argv) > 3 else 'copyright-notice')
    annotate_python(header, notice, path)
