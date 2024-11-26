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

    def queue(self, console, entries=10):
        data = self.get('poll/0')
        data = sorted(filter(lambda e: e['msg']['ver'] > 0, data),
                      key=lambda e: -e['msg']['sbt'])
        console.write('%4s' % 'Time',
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
            console.write('%4s' % sub.time_ago,
                          '%-30s' % title,
                          '%6.3fs' % (sub.runtime / 1000),
                          '%-18s' % sub.verdict[1][:18],
                          user,
                          sep='  ', bold=False)
