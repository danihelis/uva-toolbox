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

import os
import ssl

import mechanize


class UVa:
    url = 'https://uva.onlinejudge.org/index.php?option=com_onlinejudge&Itemid=25'
    code = {
        'c': '1',
        'java': '2',
        'c99': '3',
        'pascal': '4',
        'cpp': '5',
        'python': '6'
    }

    def __init__(self, toolbox):
        self.toolbox = toolbox
        self.browser = None

    def get_code(self):
        code = self.code[self.toolbox.get('language')]
        if code == '1' and self.toolbox.get('force-cpp-on-ansi-c'):
            code = self.code['cpp']
        return code

    def login(self):
        assert hasattr(self.toolbox.account, 'user'), 'user account not defined'
        if not self.toolbox.account.password:
            self.toolbox.account.set_password()
            assert self.toolbox.account.password, 'password not defined'

        self.toolbox.console.alternate('Logging in',
                                       'uva.onlinejudge.org',
                                       'as user',
                                       self.toolbox.account.user,
                                       end='...\n')
        self.browser = mechanize.Browser()
        if self.toolbox.get('bypass-ssl-certificate'):
            self.browser.set_ca_data(context=ssl._create_unverified_context())
        self.browser.set_handle_robots(False)
        self.browser.open(self.url)
        try:
            self.browser.select_form(action=lambda x: 'login' in x)
        except mechanize.FormNotFoundError:
            raise Exception('cannot login due to changes in UVa website')
        self.browser.select_form(nr=0)
        self.browser['username'] = self.toolbox.account.user
        self.browser['passwd'] = self.toolbox.account.password
        self.browser['remember'] = ['yes']
        response = self.browser.submit()
        try:
            self.browser.select_form(action=lambda x: 'login' in x)
        except mechanize.FormNotFoundError:
            pass  # form does not exist in a successful login
        else:
            self.toolbox.account.password = None
            self.toolbox.account.save()
            self.browser = None
            raise Exception('cannot login: invalid password')

    def submit(self, force=False):
        if not force:
            assert self.toolbox.workbench.test(), 'cannot submit with errors'
            self.toolbox.console.print()
        if self.browser is None:
            self.login()

        self.toolbox.console.alternate('Submitting solution',
                                       self.toolbox.workbench.source,
                                       end='...\n')
        self.browser.open(self.url)
        try:
            self.browser.select_form(action=lambda x: 'submission' in x)
        except mechanize.FormNotFoundError:
            raise Exception('cannot submit due to changes in UVa website')
        self.browser['localid'] = str(self.toolbox.workbench.problem.number)
        self.browser['language'] = [self.get_code()]
        self.browser.add_file(open(self.toolbox.workbench.source_path),
                              'text/plain', self.toolbox.workbench.source)
        resp = self.browser.submit()
        self.toolbox.console.print('Submitted with success', bold=True)
