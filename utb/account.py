import json
import os

class Account:
    FIELDS = ['id', 'user', 'password', 'name']

    def __init__(self, toolbox):
        self.toolbox = toolbox
        self.filename = os.path.join(toolbox.get('data-dir'), 'account.json')
        data = toolbox.read_json(self.filename, default={})
        self.update(data)

    def update(self, data):
        for field in self.FIELDS:
            setattr(self, field, data.get(field, None))

    def save(self):
        data = {f: getattr(self, f) for f in self.FIELDS}
        self.toolbox.write_json(self.filename, data)

    def set(self, user, update_history=True):
        if user != self.user:
            self.toolbox.console.print('Retrieving account information...')
            self.id, self.name = self.toolbox.uhunt.get_user(user)
            self.user = user
            self.password = None
            self.save()
            if update_history:
                self.toolbox.console.print('Retrieving submission data...')
                self.toolbox.history.update()
            else:
                self.toolbox.history.reset()
