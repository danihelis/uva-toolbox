import json
import os

from .submission import History

class Account:
    FIELDS = ['id', 'user', 'password', 'name']

    def __init__(self, toolbox):
        self.toolbox = toolbox
        self.filename = os.path.join(toolbox.get('data-dir'), 'account.json')
        data = {}
        if os.path.isfile(self.filename):
            data = json.load(open(self.filename))
        self.update(data)

    def update(self, data):
        for field in self.FIELDS:
            setattr(self, field, data.get(field, None))

    def save(self):
        path, _ = os.path.split(self.filename)
        if not os.path.exists(path):
            os.makedirs(path)
        data = {f: getattr(self, f) for f in self.FIELDS}
        with open(self.filename, 'w') as stream:
            stream.write(json.dumps(data))

    def set(self, user):
        if user != self.user:
            self.id, self.name = self.toolbox.uhunt.get_user(user)
            self.user = user
            self.password = None
            self.save()
