from collections import namedtuple
import json

from .utils import to_roman

class Problem:

    def __init__(self, data):
        fields = {'id': 0, 'number': 1, 'name': 2, 'dacu': 3, 'best_time': 4,
                  'time_limit': 19, 'type': 20}
        self.__dict__.update({field: data[index]
                              for field, index in fields.items()})
        fields = {'tl': 14, 'wa': 16, 'pe': 17, 'ac': 18}
        submissions = {field: data[index] for field, index in fields.items()}
        submissions['er'] = sum(data[i] for i in list(range(10, 14)) + [15])
        Submission = namedtuple('submission', submissions.keys())
        self.submissions = Submission(**submissions)
        self.total_subs = sum(self.submissions)
        self.chapters = []

    @property
    def volume(self):
        return self.number // 100

    @property
    def special(self):
        return self.type != 1

    def print(self, console, short=False, star=False):
        if not short:
            console.write('Volume', to_roman(self.volume), bold=True)
        console.print('%6d' % self.number, bold=True, end=' ')
        if short:
            if not True:
                console.print(' ' * 3)
            else:
                console.print('▐', bold=True)
                console.print('%s' % 'A', inv=True)
                console.print('▌', bold=True)
            console.print('*' if star else ' ', bold=True, end=' ')
        console.print(self.name)
        if short:
            console.write()
            return
        console.write()
        info = [('Time limit', '%.0fs' % (self.time_limit / 1000)),
                ('Best time', '%0.3fs' % (self.best_time / 1000))]
        # TODO add personal marks
        for index, (label, value) in enumerate(info):
            if index:
                console.print('  ')
            console.print(label, end=' ')
            console.print(value, bold=True)
        console.write()
        info = [('Distinct solutions', str(self.dacu))] + [
                (key.upper(), '%.1f%%' % (
                        100 * getattr(self.submissions, key) / self.total_subs))
                for key in ('ac', 'pe', 'wa', 'tl', 'er')]
        for index, (label, value) in enumerate(info):
            if index:
                console.print('  ')
            console.print(label, end=' ')
            console.print(value, bold=True)
        console.write()
        for chapter, star in sorted(self.chapters, key=lambda t: t[0].book):
            console.print('*' if star else ' ', bold=True, end=' ')
            chapter.print_name(console, with_parent=True, width=78)
            console.write()

class ProblemSet:

    def __init__(self, data, books=[]):
        self.problems = {}
        self.list = {}
        self.volumes = {}
        for obj in data:
            problem = Problem(obj)
            self.problems[problem.id] = problem
            self.list[problem.number] = problem
            self.volumes.setdefault(problem.volume, []).append(problem)
        for book in books:
            book.set_problems(self)
