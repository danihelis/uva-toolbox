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
        self.total_submissions = sum(self.submissions)
        self.chapters = []

    @property
    def volume(self):
        return self.number // 100

    @property
    def special(self):
        return self.type != 1

    def print(self, console, short=False, indent=0, star=False):
        console.print('%6d' % self.number, bold=True)
        console.print('!' if self.special else ' ', end=' ')
        if True:
            console.print('▐', bold=True)
            console.print('%s' % 'AC', inv=True)
            console.print('▌', bold=True, end=' ')
        if star:
            console.print('*', bold=True, end=' ')
        console.write(self.name)
        return

        if not short:
            console.write('Volume', to_roman(self.volume))
            volume = 'Volume ' + roman_number(self.info['number'] // 100)
            if output == sys.stdout:
                print(c('B', volume))
            else:
                print(volume, file=output)
        maxsize = 64 - indent
        title = self.info['title']
        if len(title) >= maxsize:
            title = title[:maxsize - 3] + '... '
            ldots = ''
        else:
            ldots = (' ' if len(title) % 2 != 0 else '') + \
                     ' .' * ((maxsize - len(title)) // 2) + ' '
        status, color = Problem.STATUS[self.info['status']]
        special = self.info['type'] != 1
        number = '%5d' % self.info['number']
        if output == sys.stdout:
            status = c(color, status)
            number = c('W', number)
            ldots = c('b', ldots)
        print(' ' * indent, number, '! ' if special else '  ', title, ldots,
                '%02d' % self.info['level'], '  ', status, sep='', file=output)
        if not short:
            print('Time limit:', c('W', '%0.3fs' % \
                    (self.info['limit'] / 1000)), end='  ')
            print('Best time:', c('W', '%0.3fs' % \
                    (self.info['best'] / 1000)), end='  ')
            if 'time' in self.info:
                print('Your time:', c('W', '%0.3fs' % \
                        (self.info['time'] / 1000)), end='  ')
                print('Rank:', c('W', self.info['rank']), end='')
            print()
            print('Distinct solutions:', c('W', self.info['dacu']), end='  ')
            entries = [('AC', 'G', 'AC'), ('PE', 'Y', 'PE'),
                       ('WA', 'R', 'WA'), ('TL', 'P', 'TL'),
                       ('E', 'W', 'errors')]
            for label, color, key in entries:
                print(label + ':', c(color, '%0.1f%%' % \
                    (self.info[key] / self.info['subs'] * 100)), end='  ')
            print()
            if not self.info['halim']:
                print("The problem is not part of Halim's exercises",
                      file=output)
            else:
                for chapter in self.info['halim']:
                    tokens = chapter.split()
                    extra = str()
                    if '.' in tokens[0]:
                        name = c('B', tokens[0]) + ' ' + ' '.join(tokens[1:])
                    else:
                        name = c('B', chapter)
                        extra = c('W', ' *') if self.info['starred'] else ''
                    print(' ' * indent, name, extra, sep='', file=output)
                    indent += 2


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
