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

import getpass
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

    def as_kwargs(self):
        return {
            f'account_{ field }': getattr(self, field, None)
            for field in self.FIELDS
        }

    def set_password(self):
        assert self.user, 'user not defined'
        self.toolbox.console.alternate('Username:', self.user)
        try:
            self.password = getpass.getpass()
        except (EOFError, KeyboardInterrupt):
            self.toolbox.console.print('Operation aborted')
        self.save()
