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

import datetime
import os
import shutil

from .utils import trim


class Workbench:
    current_filename = '.current'

    def __init__(self, toolbox):
        self.toolbox = toolbox
        self.works = set()
        self.base_dir = toolbox.get('problem-dir')
        self._filename = os.path.join(self.base_dir, self.current_filename)
        toolbox.makedir(self._filename)
        self.problem = None
        self.load()
        try:
            current = toolbox.read_json(self._filename, default=None)
            self.select(self.toolbox.problemset.list[current])
        except (TypeError, ValueError, KeyError, AssertionError):
            pass

    def load(self):
        for filename in os.listdir(self.base_dir):
            if os.path.isdir(os.path.join(self.base_dir, filename)):
                try:
                    problem = self.toolbox.problemset.list[int(filename)]
                    self.add(problem)
                except (ValueError, KeyError):
                    pass

    def add(self, problem):
        dir = self.dir(problem)
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

    def dir(self, problem=None):
        if not problem:
            problem = self.problem
        return os.path.join(self.base_dir, str(problem.number))

    def get_filename(self, filename, problem=None):
        return os.path.join(self.dir(problem), filename)

    @property
    def source(self):
        kwargs = self.toolbox.account.as_kwargs()
        kwargs.update(self.problem.as_kwargs())
        return self.toolbox.get_language('source').format(**kwargs)

    @property
    def source_path(self):
        return self.get_filename(self.source)

    def check_source_file(self, exception=True):
        if not os.path.isfile(self.source_path):
            if exception:
                raise Exception(f'source not found: { self.source }')
            return False
        return True

    @property
    def exe(self):
        exe = self.toolbox.get_language('exe')
        if not exe:
            return None
        kwargs = self.toolbox.account.as_kwargs()
        kwargs.update(self.problem.as_kwargs())
        return exe.format(**kwargs)

    @property
    def exe_path(self):
        exe = self.exe
        return self.get_filename(exe) if exe else None

    def get_testcases(self):
        testcases = {}
        for input in os.listdir(self.dir()):
            if input.endswith('.in'):
                testcase = input[:-3]
                answer = self.get_filename(f'{ testcase }.ans')
                testcases[testcase] = os.path.isfile(answer)
        return testcases

    def edit(self):
        assert self.problem, 'there is no problem selected'
        if not self.check_source_file(exception=False):
            with open(self.source_path, 'w') as stream:
                template = self.toolbox.get_language('template', '')
                kwargs = self.toolbox.account.as_kwargs()
                kwargs.update(self.problem.as_kwargs())
                stream.write(trim(template.format(**kwargs)))
        self.toolbox.process.open('editor', self.source_path)

    def edit_test(self, test=None):
        assert self.problem, 'there is no problem selected'
        if not test:
            testcases = self.get_testcases()
            test = 'a'
            while test in testcases:
                test = chr(ord(test) + 1)
        input = self.get_filename(f'{ test }.in')
        answer = self.get_filename(f'{ test }.ans')
        self.toolbox.process.open('editor', '"%s" "%s"' % (input, answer))

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
        shutil.rmtree(self.dir(problem))
        self.works.remove(problem)
        if problem == self.problem:
            self.problem = None
        self.toolbox.console.print('Problem removed')

    def compile(self):
        if self.exe is None:
            self.toolbox.console.print('There is no need to compile')
            return
        self.check_source_file()
        if os.path.isfile(self.exe_path):
            os.remove(self.exe_path)
        result = self.toolbox.process.run(
                'compile', source=self.source, exe=self.exe, language=True,
                dir=self.dir())
        return result == 0

    def test(self, *suite):
        self.check_source_file()
        if self.exe is not None:
            source_date = os.path.getctime(self.source_path)
            exe_date = (os.path.getctime(self.exe_path)
                        if os.path.isfile(self.exe_path) else 0)
            if exe_date < source_date:
                if not self.compile():
                    return
        testcases = self.get_testcases()
        for test in suite:
            if test not in testcases:
                raise Exception(f'test case not found: { test }')
        if not testcases:
            self.toolbox.console.print('There are no test cases to run')
            return True
        self.toolbox.console.print('Running tests with a time limit of %d ms'
                                   % self.problem.time_limit)
        timeout = self.problem.time_limit / 1000
        success = True
        for test in suite if suite else sorted(testcases.keys()):
            kwargs = {'exe': self.exe,
                      'time': '.time',
                      'input': f'{ test }.in',
                      'output': f'{ test }.out',
                      'answer': f'{ test }.ans',
                      'error': f'{ test }.err'}
            kwargs['run'] = self.toolbox.get_language('run').format(**kwargs)
            self.toolbox.console.alternate('Test ', test, '...', sep='', end='')
            code = self.toolbox.process.run(
                    'time', echo=False, dir=self.dir(), timeout=timeout,
                    **kwargs)
            timefile = self.get_filename(kwargs['time'])
            if os.path.isfile(timefile):
                with open(timefile) as stream:
                    time = stream.readline()[:-1]
                if time.startswith('0'):
                    self.toolbox.console.print('  ', time, end='')
                os.remove(timefile)
            if code == -1:
                success = False
                self.toolbox.console.print('  Timeout', bold=True, end='')
            elif code != 0:
                success = False
                self.toolbox.console.print('  Error', bold=True, end='')
            else:
                if not testcases[test]:
                    self.toolbox.console.alternate('  ', 'Okay', end='')
                else:
                    result = self.toolbox.process.run(
                            'diff', echo=False, dir=self.dir(), **kwargs)
                    success = success and result == 0
                    self.toolbox.console.alternate(
                            '  ', 'Wrong answer' if result else 'Accepted',
                            end='')
                if os.path.getsize(self.get_filename(kwargs['error'])):
                    success = False
                    self.toolbox.console.print('  (stderr output)', end='')
            self.toolbox.console.print()
        return success

    def files(self):
        assert self.problem, 'there is no problem selected'
        files = []
        source = self.source
        for file in sorted(os.listdir(self.dir())):
            if not file.startswith('.'):
                path = self.get_filename(file)
                bold = (file == source or file.endswith('.in')
                        or file.endswith('.ans'))
                date = datetime.datetime.fromtimestamp(os.path.getctime(path))
                self.toolbox.console.print(date.strftime('%b %d %Y %H:%M:%S'),
                                           end='  ')
                self.toolbox.console.print(file, bold=bold)
