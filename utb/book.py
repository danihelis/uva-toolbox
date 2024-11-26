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

from .utils import to_roman, print_bar

class Chapter:

    def __init__(self, content, parent=None, index=0):
        self.parent = parent
        self.index = index
        self.problems = []
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

    @property
    def book(self):
        if self.parent:
            return self.parent.book
        return None

    def get_full_index(self):
        if not self.index or not self.parent:
            return ''
        parent_index = self.parent.get_full_index()
        return ('%s.' % parent_index if parent_index else '') + str(self.index)

    def print_name(self, console, with_parent=False, with_index=True, width=80,
                   bold=False):
        index = self.get_full_index()
        used = 0
        available = width - len(self.name)
        if with_index:
            available -= len(index) + 1
        if with_parent and self.parent:
            available -= 3 # separator
            used = self.parent.print_name(console, True, False, available, bold)
            console.print(' > ')
            used += 3
        if index and with_index:
            console.print(index, bold=bold, end=' ')
            used += len(index) + 1
        if used + len(self.name) <= width:
            console.print('%s' % self.name, bold=bold)
            used += len(self.name)
        else:
            console.print('%s…' % self.name[:max(0, width - 1 - used)], bold=bold)
            used += 1 + max(0, width - 1 - used)
        return used

    def print_content(self, console, indent=0, depth=0):
        console.print('  ' * indent)
        span = 60 - 2 * indent
        span -= self.print_name(console, with_parent=indent == 0,
                                bold=indent == 0, width=span)
        if span:
            console.print('', ('·' if depth == 1 else ' ') * (span - 1))
        done = sum(1 for p in self.problems if p.history.accepted)
        total = len(self.problems)
        console.print(' %4d ' % total)
        print_bar(console, done, total, 9, bold=depth == 1)
        console.print(' %3d%%' % (done * 100 / total), bold=True, end='\n')
        if depth > 0:
            for obj in self.content:
                if isinstance(obj, Chapter):
                    obj.print_content(console, indent + 1, depth - 1)
                else:
                    problem = self.get_problem(obj)
                    problem.print(console, short=True, star=obj < 0)

    def get_problem(self, number):
        for problem in self.problems:
            if problem.number == abs(number):
                return problem
        return None

    def set_problems(self, problemset):
        self.problems = []
        for obj in self.content:
            if isinstance(obj, Chapter):
                self.problems += obj.set_problems(problemset)
            else:
                problem = problemset.list[abs(obj)]
                problem.chapters.append((self, obj < 0))
                self.problems.append(problem)
        return self.problems


class Book(Chapter):

    def __init__(self, content, index):
        self.index = index
        super().__init__(['Book ' + to_roman(index)])
        for index, obj in enumerate(content):
            self.content.append(Chapter(obj, self, index + 1))

    def __str__(self):
        return self.name

    @property
    def book(self):
        return self.index

    def print_name(self, console, with_parent=False, with_index=True,
                   width=80, bold=False):
        console.write(self.name, bold=bold, end='')
        return len(self.name)

    def get_section(self, *args):
        index = '.'.join(args).split('.') if args else []
        section = self
        for i in index:
            try:
                section = section.content[int(i) - 1]
            except:
                raise Exception('invalid argument: %s' % '.'.join(args))
        return section
