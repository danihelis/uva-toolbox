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

from collections import namedtuple
import json
import math
import os
import urllib

from .submission import History


class Problem:
    DIFFICULTY = [
        'Very Easy', 'Easy', 'Easy-Medium', 'Medium', 'Medium-Hard',
        'Hard', 'Very Hard']

    def __init__(self, toolbox, data):
        self.toolbox = toolbox
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

    def print(self, short=False, star=False):
        if not short:
            self.toolbox.console.print('Volume %d' % self.volume,
                                       bold=True)
        self.toolbox.console.print('%6d' % self.number, bold=True, end=' ')
        verdict = self.history.verdict
        if short:
            if not self.history.accepted:
                self.toolbox.console.write(' %2s ' % (verdict[0] or ''),
                                           bold=True)
            else:
                self.toolbox.console.print(' %s ' % verdict[0], inv=True,
                                           end='')
            width = 49 - len(self.name)
            name = self.name[:49] + ' ' * width
            self.toolbox.console.alternate('', '*' if star else ' ',
                                           name, self.popularity,
                                           self.DIFFICULTY[self.level])
            return
        self.toolbox.console.write(self.name)
        if verdict[0]:
            self.toolbox.console.write(' ' * max(0, 69 - len(self.name)))
            self.toolbox.console.print(' %s ' % verdict[0], inv=True)
        else:
            self.toolbox.console.print()
        self.toolbox.console.alternate(
                'Time limit', '%.0fs' % (self.time_limit / 1000),
                ' Best time', '%0.3fs' % (self.best_time / 1000), end='')
        if self.history.accepted:
            accepted = self.submissions.ac + self.submissions.pe
            self.toolbox.console.alternate(
                    '  Your time ', '%.3fs' % (self.history.runtime / 1000),
                    '  Rank ', str(self.history.rank),
                    ' of %d (P≤' % accepted, '%.0f%%' % (
                            100.0 * self.history.rank / accepted),
                    ')', '', end='', sep='')
        self.toolbox.console.print()
        self.toolbox.console.alternate(
                'Distinct solutions ', str(self.dacu),
                ' (', self.popularity,
                ')  AC ', '%.1f%%' % (self.percentage('ac')
                                    + self.percentage('pe')),
                '  (PE ', '%.0f%%' % self.percentage('pe'),
                ')  WA ', '%.0f%%' % self.percentage('wa'),
                '  TL ', '%.0f%%' % self.percentage('tl'),
                '  ML ', '%.0f%%' % self.percentage('ml'),
                '  ER ', '%.0f%%' % self.percentage('er'), sep='')
        self.toolbox.console.alternate(
                'Expectation  AC ', '%.1f%%' % (100 * self.expected.ac),
                ' (', '%+.0f%%' % self.delta,
                ')  WA ', '%.0f%%' % (100 * self.expected.wa),
                '  TL ', '%.0f%%' % (100 * self.expected.tl),
                '  ML ', '%.0f%%' % (100 * self.expected.ml),
                '  Level ', self.DIFFICULTY[self.level], sep='')
        for chapter, star in sorted(self.chapters, key=lambda t: t[0].book):
            self.toolbox.console.print('*' if star else ' ', bold=True, end=' ')
            chapter.print_name(with_parent=True, width=78)
            self.toolbox.console.print()

    @property
    def filename(self):
        return os.path.join(self.toolbox.get('pdf-dir'), str(self.volume),
                                '%d.pdf' % self.number)

    def download(self):
        filename = self.filename
        if os.path.exists(filename):
            return None
        path, _ = os.path.split(filename)
        if not os.path.exists(path):
            os.makedirs(path)
        url = self.toolbox.get('uva-problem').format(self.volume, self.number)
        self.toolbox.console.alternate('Retrieving data from', url)
        try:
            urllib.request.urlretrieve(url, filename)
        except:
            raise Exception('cannot access URL', url)
        self.toolbox.console.print('Downloaded %dKB' % (
                    os.path.getsize(filename) / 1000))


class ProblemSet:

    def __init__(self, toolbox):
        self.toolbox = toolbox
        self.problems = {}
        self.list = {}
        self.volumes = {}
        self.last_problem = None
        filename = os.path.join(toolbox.get('data-dir'), 'problemset.json')
        if not os.path.isfile(filename):
            return
        with open(filename) as stream:
            data = json.load(stream)
        for obj in data:
            problem = Problem(self.toolbox, obj)
            self.problems[problem.id] = problem
            self.list[problem.number] = problem
            self.volumes.setdefault(problem.volume, []).append(problem)
        for book in toolbox.books:
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

    def get_problem(self, *args):
        number = self.toolbox.current_problem
        if args and args[0] == '-':
            assert self.last_problem, 'last problem not set yet'
            number = self.last_problem.number
        elif args:
            number = int(args[0])
        assert number, 'no problem currently selected'
        self.last_problem = self.list[number]
        return self.last_problem

    def list_volumes(self, volume=None):
        if not volume:
            volumes = sorted(self.volumes.keys())
            half = math.ceil(len(volumes) / 2)
            self.toolbox.console.print('List of volume sets', bold=True)
            for index in range(half):
                for vol_index in [index, index + half]:
                    if vol_index < len(volumes):
                        volume = volumes[vol_index]
                        label = ' %3d' % volume
                        total = len(self.volumes[volume])
                        done = sum(1 for p in self.volumes[volume]
                                   if p.history.accepted)
                        bold = False
                    else:
                        label = 'TOTAL'
                        total = len(self.problems)
                        done = sum(1 for p in self.problems.values()
                                   if p.history.accepted)
                        bold = True
                    self.toolbox.console.write('%-6s' % label, bold=True)
                    self.toolbox.console.bar(done, total, 26, bold=bold)
                    self.toolbox.console.write(' %3d%%' % round(
                                done * 100 / total), bold=bold)
                    if vol_index < half:
                        self.toolbox.console.write('    ')
                self.toolbox.console.print()
        else:
            title = 'Volume %d ' % volume
            self.toolbox.console.print(title, end='·' * (60 - len(title)))
            total = len(self.volumes[volume])
            done = sum(1 for p in self.volumes[volume] if p.history.accepted)
            self.toolbox.console.write(' %4d ' % total)
            self.toolbox.console.bar(done, total, 9, bold=True)
            self.toolbox.console.print(' %3d%%' % (done * 100 / total),
                                       bold=True)
            for problem in self.volumes[volume]:
                problem.print(short=True, star=problem.chapters)
