
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
        self.works.add(problem)

    def select(self, problem=None):
        if not problem:
            self.toolbox.console.print('Problems being currently solved',
                                       bold=True)
            for problem in self.works:
                problem.print(short=True, star=problem == self.problem)
            if not self.works:
                self.toolbox.console.print('Empty list')
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
