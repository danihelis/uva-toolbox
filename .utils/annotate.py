#!/usr/bin/env python

# utb: UVa Online Judge toolbox
# Copyright (C) 2024  Daniel Donadon
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
import sys
from pathlib import Path


def load_file(filename):
    if not os.path.isfile(filename):
        print('File not found:', filename)
        sys.exit(1)
    with open(filename, 'r') as stream:
        return stream.read()


def annotate(filename, header):
    content = load_file(filename)
    if header not in content:
        with open(filename, 'w') as stream:
            stream.write(header)
            stream.write(content)
        print(filename)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage:  %s  header  directory' % sys.argv[0])
        sys.exit(2)
    header = load_file(sys.argv[1])
    for file in Path(sys.argv[2]).rglob('*.py'):
        annotate(file, header)
