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
import random
import yaml

from .book import Book
from .console import Console
from .problem import ProblemSet
from .submission import History

# Commands:
#
# n ext = choose next problem to solve
# o pen = download PDF and open it
# se lect = list open problems or select one
# ad d = put problem into workbench
# ed it = edit test case
# co mpile = ...
# t est = ...
# m ake = "compile & test"
# su bmit = ...
# q ueue = see submission queue
# ch eck = list of last submissions
# ac cept = mark as accepted, removing from workbench
# re move = remove problem from workbench
#
# up date = ...
#
# uh unt = open uHunt web
# ud ebug = open uDebug web
# sh ell = open shell terminal
#
# ! b ook = list of uHunt books
# ! l ist = show problems
# ! i nfo = info for problem
# v olume = show volumes
# ra nk = rank on UVA
#
# ex it = ...


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
        self.load_submissions()
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
        self.problemset = None
        if os.path.isfile(filename):
            data = json.load(open(filename))
            self.problemset = ProblemSet(data, self.books)

    def load_submissions(self):
        filename = os.path.join(self.config.get('data-dir', '.data'),
                                'submissions.json')
        if self.problemset and os.path.isfile(filename):
            data = json.load(open(filename))
            History.update_all(self.problemset, data)

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

    def command_exit(self, *args):
        """
        Exit the interactive shell.
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
        self.current_book.get_section(*args).print_content(
                self.console, depth=2)

    def command_book(self, *args):
        """
        Select which book will be used. To list all books available,
        type the command without argument. To select a book, type its
        number. To see which book is currently selected, type `?`.
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

    def command_next(self, *args):
        """
        Choose randomly the next problem to solve. The next problem is
        selected from the easiest problems listed in the current book.
        To choose a problem from a specific list, type its index as
        argument. To choose a problem from the entire problemset, type
        `-` as argument.
        """
        choices, level, pop = None, None, None
        problems = (self.problemset.list.values() if args and args[0] == '-'
                    else self.current_book.get_section(*args).problems)
        for p in problems:
            if not p.history.accepted and (level is None or (p.level < level or
                     (p.level == level and p.popularity <= pop))):
                if level is None or p.level < level or p.popularity < pop:
                    choices = []
                    level = p.level
                    pop = p.popularity
                choices.append(p)
        assert choices, 'there is no problem available'
        problem = random.choice(choices)
        self.command_info(problem.number)
