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

import traceback

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
        if (color or bold or backcolor) and self.accept_color:
            print('\033[%s%s3%dm' % ('1;' if bold else '',
                                     ('4%d;' % backcolor) if backcolor else '',
                                     color if color is not None else self.WHITE),
                  end='')
            print(*args, sep=sep, end='')
            print('\033[0m', end=end)
        else:
            print(*args, sep=sep, end=end)

    def print(self, *args, bold=False, inv=False, end='', sep=' '):
        self.write(*args, bold=bold, color=self.BLACK if inv else None,
                   backcolor=self.WHITE if inv else None, end=end, sep=sep)

    def execute(self, line):
        argv = line.split()
        if not argv:
            return
        command = None
        try:
            command = self.toolbox.get_unique_command(argv[0])
            self.toolbox.commands[command](*argv[1:])
        except Exception as e:
            self.write('Error', bold=True, end=': ')
            if command:
                self.write(command, end=': ')
            self.write(str(e))
            if command and self.toolbox.config.get('debug', False):
                traceback.print_exc()

    def run(self):
        self.quit = False
        self.write(COPYRIGHT)
        bold = False
        for phrase in ['Type', 'h', 'or', 'help',
                       'for a list of available commands']:
            self.write(phrase, bold=bold, end=' ')
            bold = not bold
        self.write(end='\n\n')
        prompt = ' utb '
        while not self.quit:
            accent = '░▒▓'
            self.print(prompt + accent, inv=True, end=' ')
            try:
                line = input().strip()
                self.execute(line)
            except (EOFError, KeyboardInterrupt):
                self.write()
                self.quit = True
