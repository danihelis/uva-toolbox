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
import time

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

    def __init__(self, problem_id, timestamp, verdict_id, runtime=None,
                 rank=None):
        self.problem_id = problem_id
        self.timestamp = timestamp
        self.verdict_id = verdict_id
        self.timestamp = timestamp
        self.runtime = runtime
        self.rank = rank

    @property
    def verdict(self):
        return self.VERDICT_CODES[self.verdict_id]

    @property
    def accepted(self):
        return self.verdict_id in [80, 90]

    @property
    def time_ago(self):
        value = max(0, int(time.time() - self.timestamp))
        window = [('s', 1), ('m', 60), ('h', 60),
                  ('d', 24), ('y', 365), (None, -1)]
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

    @classmethod
    def update_all(cls, problemset, data):
        for p in problemset.problems.values():
            p.history = cls()
        for entry in data['subs']:
            pid = entry[1]
            submission = Submission(entry[1], entry[4], entry[2], entry[3],
                                    entry[6])
            problemset.problems[pid].history.add(submission)
