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
            url = self.api + '/'.join([endpoint] + list(params))
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
        '%-18s' % 'Verdict',
                                   'User',
                                   bold=True, sep='  ')
        for entry in data[:entries]:
            obj = entry['msg']
            problem = self.toolbox.problemset.problems[obj['pid']]
            user = obj['name']
            if len(user) > 13:
                user = user[:12] + '…'
            title = '%5s %s' % (problem.number, problem.name)
            if len(title) > 30:
                title = title[:29] + '…'
            sub = Submission(problem.id, obj['sbt'], obj['ver'],
                             runtime=obj['run'], rank=obj['rank'])
            self.toolbox.console.print(
                    '%4s' % sub.time_ago,
                    '%-30s' % title,
                    '%6.3fs' % (sub.runtime / 1000),
                    '%-18s' % sub.verdict[1][:18],
                    user,
                    sep='  ', bold=False)

    def get_user(self, username):
        userid = self.get('uname2uid/' + username)
        assert userid, 'username not found: %s' % username
        obj = self.get('subs-user-last/%d/0' % userid)
        return (userid, obj['name'])
