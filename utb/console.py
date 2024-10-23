import os, sys, json

COPYRIGHT = """utb (UVa Online Judge toolbox)
Copyright (C) 2024  Daniel Donadon
This is free software; see the source for copying conditions.  There is NO
warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
"""


class Console:
    BLACK, RED, GREEN, YELLOW, BLUE, PURPLE, CYAN, WHITE = list(range(8))

    def __init__(self, toolbox):
        self.toolbox = toolbox
        self.accept_color = self.toolbox.config.get('accept-color', False)

    def write(self, *args, color=None, bold=False, backcolor=None, end='\n',
              sep=' '):
        if (color or bold) and self.accept_color:
            print('\033[%s%s3%dm' % (
                    '1;' if bold else '',
                    ('4%d;' % color) if backcolor else '',
                    color or self.WHITE,
                    ), end='')
            print(*args, sep=sep, end='')
            print('\033[0m', end=end)
        else:
            print(*args, sep=sep, end=end)

    def run(self):
        self.write(COPYRIGHT)
        self.write('Look, does it accept color?', bold=True)
        self.write(self.toolbox.config)
        return

        if not self.data.account.id:
            print(c('R', 'The account file is empty.  ' \
                         'Please define an account.'))
            self.data.account.retrieve(self.data.uhunt)

        while not self.quit:
            self.data.check_integrity()
            prompt = ' %s ' % self.data.account.user
            current = self.data.workbench.get_current()
            if current:
                title = current.get('title')
                limit = 30
                if len(title) > limit:
                    title = title[:limit - 3] + '...'
                #prompt = '[%d: %s]' % (current.get('number'), title)
                prompt += '| %d | %s ' % (current.get('number'), title)
            print(c('n', prompt, 'w') + '▶', end=' ')
            try:
                command = input().strip()
            except (EOFError, KeyboardInterrupt):
                print()
                break
            if len(command) == 0:
                continue
            try:
                tokens = command.split()
                command = tokens[0]
                parameters = tokens[1:]
                command, function = self.get_operation(command)
                function(*parameters)
            except Error as error:
                print(c('R', 'Error:'), c('W', command + ':'), error)
        self.data.workbench.save_state()
        self.data.uhunt.save_correction()
        print('Bye!')
