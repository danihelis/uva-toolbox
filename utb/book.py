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

from .utils import to_roman

class Chapter:

    def __init__(self, content, parent=None, index=0):
        self.parent = parent
        self.index = index
        if isinstance(content, (list, tuple)):
            self.name = content[0]
            self.content = content[1:]
        else:
            assert 'title' in content and 'arr' in content
            self.name = content['title']
            self.content = []
            for index, obj in enumerate(content['arr']):
                self.content.append(Chapter(obj, self, index + 1))

    def __str__(self):
        return '%s %s' % (self.get_full_index(), self.name)

    def get_full_index(self):
        if not self.index or not self.parent:
            return ''
        parent_index = self.parent.get_full_index()
        return ('%s.' % parent_index if parent_index else '') + str(self.index)

    def print_name(self, console, with_parent=False, width=80, bold=False):
        index = self.get_full_index()
        available = width - len(index)
        if with_parent and self.parent:
            available -= 3 # separator
            available -= self.parent.print_name(
                    console, True, available - len(self.name) - 1, bold)
            console.write(' > ', end='')
        if index:
            console.write(index, bold=bold, end='')
        if available > len(self.name):
            console.write(' %s' % self.name, bold=bold, end='')
            available -= len(self.name)
        elif available > 2:
            console.write(' %s…' % self.name[:available - 2], bold=bold, end='')
            available = 0
        return width - available

    def print_content(self, console, indent=0, depth=0):
        console.write('  ' * indent, end='')
        self.print_name(console, with_parent=indent == 0, bold=indent == 0,
                        width=60)
        console.write()
        if depth > 0:
            for obj in self.content:
                if isinstance(obj, Chapter):
                    obj.print_content(console, indent + 1, depth - 1)
                else:
                    console.write(obj)

    def get_problems(self):
        problems = []
        for obj in self.content:
            if isinstance(obj, Chapter):
                problems += obj.get_problems()
            else:
                problems.append(obj)
        return problems


class Book(Chapter):

    def __init__(self, content, index):
        super().__init__(['Book ' + to_roman(index)])
        for index, obj in enumerate(content):
            self.content.append(Chapter(obj, self, index + 1))

    def __str__(self):
        return self.name

    def print_name(self, console, with_parent=False, width=80, bold=False):
        console.write(self.name, bold=bold, end='')
        return len(self.name)
