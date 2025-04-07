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

import json
import math
import os
import time
from collections import namedtuple


class Submission:
    VERDICT_CODES = {
        10: ('SE', 'Submission error'),
        15: ('CJ', 'Cannot be judged'),
        20: ('IQ', 'In queue'),
        30: ('CE', 'Compile error'),
        35: ('RF', 'Restricted function'),
        40: ('RE', 'Runtime error'),
        45: ('OL', 'Output limit'),
        50: ('TL', 'Time limit'),
        60: ('ML', 'Memory limit'),
        70: ('WA', 'Wrong answer'),
        80: ('PE', 'Presentation error'),
        90: ('AC', 'Accepted'),
    }
    LANGUAGE_CODES = {
        1: 'C',
        2: 'Java',
        3: 'C99',
        4: 'Pascal',
        5: 'C++',
        6: 'Python',
    }

    def __init__(self,
                 problem_id,
                 timestamp,
                 verdict_id,
                 runtime=None,
                 rank=None,
                 language_code=None):
        self.problem_id = problem_id
        self.timestamp = timestamp
        self.verdict_id = verdict_id
        self.timestamp = timestamp
        self.runtime = runtime
        self.rank = rank
        self.language_code = language_code

    @property
    def language(self):
        return self.LANGUAGE_CODES.get(self.language_code, '?')

    @property
    def verdict(self):
        return self.VERDICT_CODES[self.verdict_id]

    @property
    def accepted(self):
        return self.verdict_id in [80, 90]

    @property
    def time_ago(self):
        value = max(0, int(time.time() - self.timestamp))
        window = [('s', 1), ('m', 60), ('h', 60), ('d', 24), ('y', 365),
                  (None, -1)]
        for i in range(1, len(window)):
            nextval = value // window[i][1]
            if nextval < 1 or not window[i][0]:
                return str(value) + window[i - 1][0]
            value = nextval
        return '???'


class History:

    def __init__(self):
        self.submissions = []

    def add(self, submission):
        self.submissions.append(submission)

    @property
    def verdict(self):
        if self.submissions:
            best = max(s.verdict_id for s in self.submissions)
            return Submission.VERDICT_CODES[best]
        return (None, None)

    @property
    def accepted(self):
        return any(s.accepted for s in self.submissions)

    def get_accepted_submissions(self):
        return [s for s in self.submissions if s.accepted]

    @property
    def runtime(self):
        accepted = self.get_accepted_submissions()
        return min(s.runtime for s in accepted) if accepted else None

    @property
    def rank(self):
        accepted = self.get_accepted_submissions()
        return min(s.rank for s in accepted) if accepted else None


class UserHistory:

    def __init__(self, toolbox):
        self.toolbox = toolbox
        self.filename = os.path.join(toolbox.get('data-dir'),
                                     'submissions.json')
        data = toolbox.read_json(self.filename, {})
        if data and data['uname'] != toolbox.account.user:
            data = {}
        self.populate(data)

    @property
    def count(self):
        return len(self.submissions)

    def reset(self):
        self.data = {}
        for p in self.toolbox.problemset.problems.values():
            p.history = History()

    def populate(self, data):
        self.reset()
        self.data = data
        self.submissions = []
        for entry in data.get('subs', []):
            pid = entry[1]
            submission = Submission(entry[1], entry[4], entry[2], entry[3],
                                    entry[6], entry[5])
            self.submissions.append(submission)
            self.toolbox.problemset.problems[pid].history.add(submission)
        self.submissions.sort(key=lambda s: s.timestamp, reverse=True)

    def update(self):
        if self.toolbox.account:
            self.populate(self.toolbox.uhunt.get_submissions())
        self.save()

    def save(self):
        self.toolbox.write_json(self.filename, self.data)

    def last_submissions(self, entries=10):
        self.update()
        self.toolbox.console.print('%4s' % 'Time',
                                   '%-30s' % 'Problem',
                                   '%7s' % 'Run',
                                   '%7s' % 'Best',
                                   '%4s' % 'Lang',
                                   'Verdict',
                                   bold=True,
                                   sep='  ')
        for sub in self.submissions[:entries]:
            problem = self.toolbox.problemset.problems[sub.problem_id]
            title = '%5s %s' % (problem.number, problem.name)
            if len(title) > 30:
                title = title[:29] + '…'
            verd = sub.verdict[1]
            self.toolbox.console.print('%4s' % sub.time_ago,
                                       '%-30s' % title,
                                       '%6.3fs' % (sub.runtime / 1000),
                                       '%6.3fs' % (problem.best_time / 1000),
                                       '%-4s' % sub.language[:4],
                                       verd,
                                       sep='  ',
                                       bold=False)
