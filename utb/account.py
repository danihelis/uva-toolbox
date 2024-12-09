import json
import os

class Account:
    FIELDS = ['id', 'user', 'password', 'name']

    def __init__(self, toolbox):
        self.toolbox = toolbox
        self.filename = os.path.join(toolbox.get('data-dir'), 'account.json')
        data = {}
        if os.path.isfile(self.filename):
            data = json.load(open(filename))
        self.update(data)

    def update(self, data):
        for field in self.FIELDS:
            setattr(self, field, data.get(field, None))

    def save(self):
        data = {f: getattr(self, f) for f in self.FIELDS}
        with open(self.filename, 'w') as stream:
            stream.write(json.dumps(data))
