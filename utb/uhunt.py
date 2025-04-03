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
import urllib.request as request

from .submission import Submission

class UHunt:
# problem     = p/num/{pid}
# problem-set = p
# submissions = subs-user/{uid}
# last        = subs-user-last/{uid}/{count}
# rank        = ranklist/{uid}/{above}/{below}
# name2id     = uname2uid/{name}
# halim       = cpbook/{edition}

    def __init__(self, toolbox):
        self.toolbox = toolbox
        self.api = toolbox.get('uhunt-api')

    def get(self, endpoint, *params):
        try:
            url = self.api + '/'.join([endpoint] + list(map(str, params)))
            response = request.urlopen(url)
            return json.loads(response.read().decode('utf-8'))
        except:
            raise Exception('cannot access URL', url)

    def queue(self, entries=10):
        data = self.get('poll/0')
        data = sorted(filter(lambda e: e['msg']['ver'] > 0, data),
                      key=lambda e: -e['msg']['sbt'])
        self.toolbox.console.print('%4s' % 'Time',
                                   '%-30s' % 'Problem',
                                   '%7s' % 'Run',
                                   '%-12s' % 'Verdict',
                                   '%4s' % 'Lang',
                                   'User',
                                   bold=True, sep='  ')
        for entry in data[:entries]:
            obj = entry['msg']
            problem = self.toolbox.problemset.problems[obj['pid']]
            user = obj['uname']
            sub = Submission(problem.id, obj['sbt'], obj['ver'],
                             runtime=obj['run'], rank=obj['rank'],
                             language_code=obj['lan'])
            if len(user) > 13:
                user = user[:12] + '…'
            title = '%5s %s' % (problem.number, problem.name)
            if len(title) > 30:
                title = title[:29] + '…'
            verd = sub.verdict[1]
            if len(verd) > 12:
                verd = verd[:11] + '…'
            self.toolbox.console.print(
                    '%4s' % sub.time_ago,
                    '%-30s' % title,
                    '%6.3fs' % (sub.runtime / 1000),
                    '%-12s' % verd,
                    '%-4s' % sub.language[:4],
                    user,
                    sep='  ', bold=obj['uid'] == self.toolbox.account.id)

    def get_user(self, username):
        userid = self.get('uname2uid', username)
        assert userid, 'username not found: %s' % username
        obj = self.get('subs-user-last/%d/0' % userid)
        return (userid, obj['name'])

    def get_submissions(self, userid=None):
        userid = userid or self.toolbox.account.id
        assert userid, 'user account not defined'
        return self.get('subs-user', userid)

    def ranklist(self, username=None, entries=10):
        if username:
            userid = self.get('uname2uid', username)
            assert userid, 'username not found: %s' % username
        else:
            userid = self.toolbox.account.id
            assert userid, 'account user not defined'
        data = self.get('ranklist', userid, entries, 10)
        activities = ' '.join('%3s' % f
                              for f in ('2d', '7d', '1m', '3m', '1y'))
        self.toolbox.console.print('%6s' % 'Rank',
                                   '%4s' % 'AC',
                                   '%6s' % 'Subs',
                                   activities,
                                   'User',
                                   sep='  ', bold=True)
        for entry in data:
            name = '%s (%s)' % (entry['username'], entry['name'])
            if len(name) > 37:
                name = name[:36] + '…'
            activities = ' '.join('%3d' % min(999, value)
                                  for value in entry['activity'])
            self.toolbox.console.print(
                    '%6s' % entry['rank'],
                    '%4s' % entry['ac'],
                    '%6s' % entry['nos'],
                    activities,
                    name,
                    sep='  ', bold=entry['userid'] == userid)
