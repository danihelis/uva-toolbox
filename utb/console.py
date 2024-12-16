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
        self.accept_color = self.toolbox.get('accept-color', False)

    def write(self, arg, color=None, bold=False, background=None):
        if (color or bold or background) and self.accept_color:
            print('\033[%s%s3%dm' % (
                        '1;' if bold else '',
                        ('4%d;' % background) if background else '',
                        color if color is not None else self.WHITE),
                  arg, '\033[0m', sep='', end='', flush=True)
        else:
            print(arg, sep='', end='', flush=True)

    def print(self, *args, bold=False, inv=False, end='\n', sep=' '):
        content = (sep.join(args) if len(args) > 1 else
                   args[0] if args else '')
        self.write(content, bold=bold, color=self.BLACK if inv else None,
                   background=self.WHITE if inv else None)
        self.write(end)

    def alternate(self, *args, end='\n', sep=' ', inv=False, start_bold=False):
        mod = 0 if start_bold else 1
        for index, arg in enumerate(args):
            last = sep if index < len(args) - 1 else end
            self.print(arg, bold=index % 2 == mod, end=last, inv=inv)

    def bar(self, value, maximum, size, bold=False):
        fractions = zip('▉▊▋▌▍▎▏', list(range(7, 0, -1)))
        bar = ''
        factor = maximum / size
        for i in range(size):
            symbol = None
            if value >= (i + 1) * factor:
                symbol = '█'
            elif value > i * factor:
                delta = (value - i * factor) / factor
                for symbol, f in fractions:
                    if delta >= f / 8:
                        break
                else: # no break
                    symbol = None
            if symbol:
                self.write(symbol, bold=bold)
            else:
                self.write('⁚')

    def execute(self, line):
        argv = line.split()
        if not argv:
            return
        command = None
        try:
            command = self.toolbox.get_unique_command(argv[0])
            self.toolbox.commands[command](*argv[1:])
        except Exception as e:
            self.print('Error', bold=True, end=': ')
            if command:
                self.print(command, end=': ')
            self.print(str(e))
            if command and self.toolbox.get('debug', False):
                traceback.print_exc()
        self.print()

    def run(self):
        self.quit = False
        self.print(COPYRIGHT)
        bold = False
        self.alternate('Type', 'h', 'or', 'help',
                       'for a list of available commands')
        prompt = ' utb '
        while not self.quit:
            accent = '░▒▓'
            self.print(prompt + accent, inv=True, end=' ')
            try:
                line = input().strip()
                self.execute(line)
            except (EOFError, KeyboardInterrupt):
                self.print()
                self.quit = True
