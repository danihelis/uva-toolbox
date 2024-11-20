from collections import namedtuple
import json
import math

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
