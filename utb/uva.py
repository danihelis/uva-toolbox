
import mechanize
import os

class UVa:
    url = 'https://uva.onlinejudge.org/index.php?option=com_onlinejudge&Itemid=25'
    code = {'c': '1',
            'java': '2',
            'c99': '3',
            'pascal': '4',
            'cpp': '5',
            'python': '6'}

    def __init__(self, toolbox):
        self.toolbox = toolbox
        self.browser = None

    def get_code(self):
        code = self.code[self.toolbox.get('language')]
        if code == '1' and self.toolbox.get('force-cpp-on-ansi-c'):
            code = code['cpp']
        return code

    def login(self):
        assert hasattr(self.toolbox.account, 'user'), 'user account not defined'
        if not self.toolbox.account.password:
            self.toolbox.account.set_password()
            assert self.toolbox.account.password, 'password not defined'

        self.toolbox.console.alternate(
                'Logging in', 'uva.onlinejudge.org', 'as user',
                self.toolbox.account.user, end='...\n')
        self.browser = mechanize.Browser()
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
            self.account.password = None
            self.account.save()
            raise Exception('cannot login: invalid password')

    def submit(self, force=False):
        if not force:
            assert self.toolbox.workbench.test(), 'cannot submit with errors'
            self.toolbox.console.print()
        if self.browser is None:
            self.login()

        self.toolbox.console.alternate(
                'Submitting solution', self.toolbox.workbench.source,
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
