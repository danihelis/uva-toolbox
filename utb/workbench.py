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
import shutil

from .utils import trim


class Workbench:
    current_filename = '.current'

    def __init__(self, toolbox):
        self.toolbox = toolbox
        self.works = set()
        self.dir = toolbox.get('problem-dir')
        self.problem = None
        self.load()
        self._filename = os.path.join(self.dir, self.current_filename)
        try:
            current = toolbox.read_json(self._filename, default=None)
            self.select(self.toolbox.problemset.list[current])
        except (TypeError, ValueError, KeyError, AssertionError):
            pass

    def load(self):
        if not os.path.isdir(self.dir):
            os.makedirs(self.dir)
        for filename in os.listdir(self.dir):
            if os.path.isdir(os.path.join(self.dir, filename)):
                try:
                    problem = self.toolbox.problemset.list[int(filename)]
                    self.add(problem)
                except (ValueError, KeyError):
                    pass

    def add(self, problem):
        dir = os.path.join(self.dir, str(problem.number))
        if not os.path.isdir(dir):
            os.makedirs(dir)
            self.toolbox.console.alternate('Adding problem ', problem.number,
                                           ': %s' % problem.name, sep='')
        self.works.add(problem)

    def select(self, problem=None):
        if not problem and not self.works:
            self.toolbox.console.print('No problem is currently being solved')
        elif not problem:
            self.toolbox.console.print('Problems being currently solved',
                                       bold=True)
            for problem in self.works:
                problem.print(short=True, star=problem == self.problem)
        else:
            assert problem in self.works, ('problem is not being solved: '
                                           'add the problem first')
            if problem != self.problem:
                self.toolbox.write_json(self._filename, problem.number)
            self.problem = problem

    def get_filename(self, filename):
        return os.path.join(self.dir, str(self.problem.number), filename)

    def edit(self):
        assert self.problem, 'there is no problem selected'
        kwargs = self.toolbox.account.as_kwargs()
        kwargs.update(self.problem.as_kwargs())
        source = self.toolbox.get_language('source').format(**kwargs)
        filename = self.get_filename(source)
        if not os.path.isfile(filename):
            with open(filename, 'w') as stream:
                template = self.toolbox.get_language('template', '')
                stream.write(trim(template.format(**kwargs)))
        self.toolbox.process.open('editor', filename)

    def remove(self, problem, force=False):
        assert problem in self.works, 'problem is not being solved'
        if not force:
            self.toolbox.console.alternate('Removing problem ', problem.number,
                                           ': %s' % problem.name, sep='')
            self.toolbox.console.alternate('Type', 'remove', 'to confirm:',
                                           end=' ')
            try:
                confirm = input()
                assert confirm == 'remove'
            except (AssertionError, KeyboardInterrupt):
                self.toolbox.console.print('Operation aborted')
                return
        dir = os.path.join(self.dir, str(problem.number))
        shutil.rmtree(dir)
        self.works.remove(problem)
        if problem == self.problem:
            self.problem = None
        self.toolbox.console.print('Problem removed')
