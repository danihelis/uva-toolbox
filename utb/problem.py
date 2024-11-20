from collections import namedtuple
import json
import math

from .submission import History
from .utils import to_roman

class Problem:
    DIFFICULTY = [
        'Very Easy', 'Easy', 'Easy-Medium', 'Medium', 'Medium-Hard',
        'Hard', 'Very Hard']

    def __init__(self, data):
        fields = {'id': 0, 'number': 1, 'name': 2, 'dacu': 3, 'best_time': 4,
                  'time_limit': 19, 'type': 20}
        self.__dict__.update({field: data[index]
                              for field, index in fields.items()})
        fields = {'tl': 14, 'ml': 15, 'wa': 16, 'pe': 17, 'ac': 18}
        submissions = {field: data[index] for field, index in fields.items()}
        submissions['er'] = sum(data[i] for i in range(10, 14))
        Submission = namedtuple('submission', submissions.keys())
        self.submissions = Submission(**submissions)
        self.total_subs = sum(self.submissions)
        self.chapters = []
        self.history = History()

    @property
    def volume(self):
        return self.number // 100

    @property
    def special(self):
        return self.type != 1

    def percentage(self, key):
        return getattr(self.submissions, key) * 100 / max(1, self.total_subs)

    @property
    def popularity(self):
        # return chr(ord('A') + self.popularity_level)
        return chr(ord('A') + 10 - min(10, int(math.log(max(1, self.dacu)))))

    def print(self, console, short=False, star=False):
        if not short:
            console.write('Volume', to_roman(self.volume), bold=True)
        console.print('%6d' % self.number, bold=True, end=' ')
        verdict = self.history.verdict
        if short:
            # TODO add personal submission status
            if not self.history.accepted:
                console.print(' %2s ' % (verdict[0] or ''), bold=True)
            else:
                console.print('▐', bold=True)
                console.print('%s' % verdict[0], inv=True)
                console.print('▌', bold=True)
            console.print('*' if star else ' ', bold=True, end=' ')
            width = 50 - len(self.name)
            console.print(self.name, end=' ' * width)
            console.print(self.popularity, end=' ', bold=True)
            console.write(self.DIFFICULTY[self.level])
            return
        console.print(self.name)
        if verdict[0]:
            width = 69 - len(self.name)
            console.print(' ' * width)
            console.print('▐', bold=True)
            console.print('%s' % verdict[0], inv=True)
            console.print('▌', bold=True)
        console.write()
        info = [('Time limit ', '%.0fs' % (self.time_limit / 1000)),
                ('  Best time ', '%0.3fs' % (self.best_time / 1000))]
        if self.history.accepted:
            accepted = self.submissions.ac + self.submissions.pe
            info += [('  Your time ', '%.3fs' % (self.history.runtime / 1000)),
                     ('  Rank ', str(self.history.rank)),
                     (' of %d (P≤' % accepted, '%.0f%%' % (
                            100.0 * self.history.rank / accepted)),
                     (')', '')]

        # TODO add personal marks
        for index, (label, value) in enumerate(info):
            console.print(label)
            console.print(value, bold=True)
        console.write()
        info = [('Distinct solutions ', str(self.dacu)),
                (' (', self.popularity),
                (')  AC ', '%.1f%%' % (self.percentage('ac')
                                     + self.percentage('pe'))),
                ('  (PE ', '%.0f%%' % self.percentage('pe')),
                (')  WA ', '%.0f%%' % self.percentage('wa')),
                ('  TL ', '%.0f%%' % self.percentage('tl')),
                ('  ML ', '%.0f%%' % self.percentage('ml')),
                ('  ER ', '%.0f%%' % self.percentage('er'))]
        for label, value in info:
            console.print(label)
            console.print(value, bold=True)
        console.write()
        info = [('Expectation  AC ', '%.1f%%' % (100 * self.expected.ac)),
                (' (', '%+.0f%%' % self.delta),
                (')  WA ', '%.0f%%' % (100 * self.expected.wa)),
                ('  TL ', '%.0f%%' % (100 * self.expected.tl)),
                ('  ML ', '%.0f%%' % (100 * self.expected.ml)),
                ('  Level ', self.DIFFICULTY[self.level])]
        for label, value in info:
            console.print(label)
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
        avg_ac, avg_wa, avg_tl, avg_ml = 0, 0, 0, 0
        for p in self.problems.values():
            p.non_errors = p.total_subs - p.submissions.er
            avg_ac += (p.submissions.ac + p.submissions.pe) / max(1, p.non_errors)
            avg_wa += p.submissions.wa / max(1, p.non_errors)
            avg_tl += p.submissions.tl / max(1, p.non_errors)
            avg_ml += p.submissions.tl / max(1, p.non_errors)
        avg_ac /= len(self.problems)
        avg_wa /= len(self.problems)
        avg_tl /= len(self.problems)
        avg_ml /= len(self.problems)
        counter = {}
        for p in self.problems.values():
            factor = 1 - p.submissions.er / max(1, p.total_subs)
            p.expected = namedtuple('Expected', ['ac', 'wa', 'tl', 'ml'])(
                    *(avg * factor for avg in [avg_ac, avg_wa, avg_tl, avg_ml]))
            p.delta = round(p.percentage('ac') + p.percentage('pe')
                            - 100 * p.expected.ac)
            if p.delta not in counter:
                counter[p.delta] = 0
            counter[p.delta] += 1
        bucket_size = len(self.problems) / len(Problem.DIFFICULTY)
        bucket_count, bucket = 0, 0
        level = {}
        for delta in sorted(counter, reverse=True):
            level[delta] = bucket
            bucket_count += counter[delta]
            if bucket_count > bucket_size:
                bucket_count -= bucket_size
                bucket += 1
        for p in self.problems.values():
            p.level = level[p.delta]
