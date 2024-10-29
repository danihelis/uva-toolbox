#!/usr/bin/env python

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
        # with open(filename, 'w') as stream:
        #     stream.write(header)
        #     stream.write(content)
        print(filename)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage:  %s  header  directory' % sys.argv[0])
        sys.exit(2)
    header = load_file(sys.argv[1])
    for file in Path(sys.argv[2]).rglob('*.py'):
        annotate(file, header)
