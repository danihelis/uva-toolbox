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

from collections import OrderedDict
import inspect
import json
import os
import yaml

from .book import Book
from .console import Console
from .problem import ProblemSet


class Toolbox:

    def __init__(self, config):
        if not os.path.isfile(config):
            raise Exception('Configuration file not found: %s' % str(config))
        with open(config) as stream:
            try:
                self.config = yaml.safe_load(stream)
            except yaml.YAMLError:
                raise
        self.console = Console(self)
        self.load_books()
        self.load_problems()
        self.load_commands()

    def load_books(self):
        self.books = []
        for index in range(self.config.get('number-books', 4)):
            filename = os.path.join(self.config.get('data-dir', '.data'),
                                    'book-%d.json' % (index + 1))
            if os.path.isfile(filename):
                with open(filename) as stream:
                    data = json.loads(stream.read())
                    self.books.append(Book(data, index + 1))
        self.current_book = self.books[-1]

    def load_problems(self):
        filename = os.path.join(self.config.get('data-dir', '.data'),
                                'problemset.json')
        data = json.load(open(filename))
        if os.path.isfile(filename):
            self.problemset = ProblemSet(data, self.books)
        else:
            self.problemset = None

    def load_commands(self):
        members = inspect.getmembers(self, lambda obj: inspect.ismethod(obj))
        prefix = 'command_'
        self.commands = {name[len(prefix):]: method for name, method in members
                         if name.startswith('command_')}

    def get_unique_command(self, prefix):
        commands = [k for k in self.commands if k.startswith(prefix)]
        if not commands:
            raise Exception('command not found: %s' % prefix)
        if len(commands) > 1:
            raise Exception('ambiguous command: %s' % ', '.join(commands))
        return commands[0]

    def run(self):
        self.console.run()

    def command_quit(self, *args):
        """
        Quit the interactive shell.
        """
        self.console.quit = True

    def command_help(self, *args):
        """
        See the help entry for a command. To see a list of all available
        commands, type the command without argument.
        """
        if args:
            command = self.get_unique_command(args[0])
            doc = self.commands[command].__doc__
            doc = '\n'.join(line.strip() for line in doc.split('\n')[1:-1])
            self.console.write(command, bold=True)
            self.console.write(doc)
        else:
            self.console.write('List of available commands')
            for name in sorted(self.commands.keys()):
                self.console.write('%-10s' % name, bold=True, end='')
                doc = self.commands[name].__doc__.split('.')[0]
                self.console.write(doc.strip().lower())

    def command_list(self, *args):
        """
        List all chapters of the current book. To see the divisions of a
        chapter, type the chapter or the section entry, separating each
        number by space or dot. Example:
            >>> list 2.3.1
        """
        data = self.current_book
        if len(args) == 1:
            args = args[0].split('.')
        for arg in args:
            try:
                data = data.content[int(arg) - 1]
            except:
                raise Exception('invalid argument: %s' % '.'.join(args))
        data.print_content(self.console, depth=2)

    def command_book(self, *args):
        """
        Select which book will be used. To list all books available,
        type the command without argument. To select a book, type its
        number. To see which book is currently selected, type `?`.
        Example:
            >>> book 3
        """
        if not args:
            for book in self.books:
                book.print_content(self.console, depth=1)
            return
        if args[0] == '?':
            self.console.write(self.current_book.name, 'is currently selected')
            return
        try:
            self.current_book = self.books[int(args[0]) - 1]
            self.console.write(self.current_book.name, 'selected')
        except:
            raise Exception('invalid argument: %s' % args[0])

    def command_info(self, *args):
        """
        Show information about a problem. To show information about the
        current selected problem, type the comment without argument.
        To show information about a specific problem, type its number.
        To show information about the last problem listed, type `-`.
        """
        if args:
            number = 100 if args[0] == '-' else int(args[0])
        else:
            number = 100
        problem = self.problemset.list[number]
        problem.print(self.console)
