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

from collections import OrderedDict
import inspect
import json
import os
import random
import yaml

from .account import Account
from .book import Book
from .console import Console
from .problem import ProblemSet
from .process import Process
from .settings import DEFAULT_SETTINGS
from .submission import UserHistory
from .uhunt import UHunt
from .utils import trim
from .uva import UVa
from .workbench import Workbench

# Commands:
#
# !  n ext = choose next problem to solve
# !  d ownload = download statement
# !  o pen = download PDF and open it
# !  se lect = list open problems or select one
# !  ad d = put problem into workbench
# !  ed it = edit test case
# !  co mpile = ...
# !  t est = ...
# su bmit = ...
# !  q ueue = see submission queue
# ch eck = list of last submissions
# ac cept = mark as accepted, removing from workbench
# => ar chive = ''
# !  re move = remove problem from workbench
#
# !  us er = modify account data
# p assword = define user password
# !  up date = ...
#
# uh unt = open uHunt web
# ud ebug = open uDebug web
# sh ell = open shell terminal
#
# !  b ook = list of uHunt books
# !  l ist = show problems
# !  i nfo = info for problem
# !  v olume = show volumes
# ra nk = rank on UVA
#
# !  ex it = ...


class Toolbox:

    def __init__(self, config):
        if not os.path.isfile(config):
            try:
                with open(config, 'w') as stream:
                    stream.write('# Override default configuration here\n')
            except:
                pass
            self.config = {}
        else:
            with open(config) as stream:
                self.config = yaml.safe_load(stream)
        self.console = Console(self)
        self.account = Account(self)
        self.books = Book.load_all(self)
        self.current_book = self.books[-1]
        self.problemset = ProblemSet(self)
        self.uhunt = UHunt(self)
        self.uva = UVa(self)
        self.process = Process(self)
        self.history = UserHistory(self)
        self.workbench = Workbench(self)
        self.load_commands()

    @property
    def current_problem(self):
        return self.workbench.problem

    def get(self, key, default=None):
        return (self.config.get(key) if key in self.config else
                DEFAULT_SETTINGS.get(key, default))

    def get_language(self, key, default=None):
        key = '%s-%s' % (self.get('language'), key)
        return (self.config.get(key) if key in self.config else
                DEFAULT_SETTINGS.get(key, default))

    def makedir(self, filename):
        path, _ = os.path.split(filename)
        if not os.path.exists(path):
            os.makedirs(path)

    def read_json(self, filename, default=None, or_error=None):
        if not os.path.isfile(filename):
            if or_error:
                raise Exception(or_error)
            return default
        with open(filename, 'r') as stream:
            try:
                return json.load(stream)
            except json.decoder.JSONDecodeError:
                if or_error:
                    raise Exception(on_error)
                return default

    def write_json(self, filename, data):
        self.makedir(filename)
        with open(filename, 'w') as stream:
            json.dump(data, stream)

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
        commands, type the command without arguments.
        """
        if args:
            command = self.get_unique_command(args[0])
            doc = trim(self.commands[command].__doc__)
            self.console.print(command, bold=True)
            self.console.print(doc)
        else:
            self.console.print('List of available commands')
            for name in sorted(self.commands.keys()):
                doc = self.commands[name].__doc__.split('.')[0]
                self.console.alternate('%-10s' % name, doc.strip().lower(),
                                       start_bold=True)

    def command_list(self, *args):
        """
        List all chapters from the current book. To see the divisions of
        a chapter, type the chapter or the section entry, separating
        each number by space or dot. Example:
            >>> list 2.3.1
        """
        self.current_book.get_section(*args).print_content(depth=2)

    def command_book(self, *args):
        """
        Select which book will be used. To list all books available,
        type the command without arguments. To select a book, type its
        number. To see which book is currently selected, type `?`.
        """
        if not args:
            for book in self.books:
                book.print_content(depth=1)
            return
        if args[0] == '?':
            self.console.print(self.current_book.name, 'is currently selected')
            return
        try:
            self.current_book = self.books[int(args[0]) - 1]
            self.console.print(self.current_book.name, 'selected')
        except:
            raise Exception('invalid argument: %s' % args[0])

    def command_info(self, *args):
        """
        Show information about a problem. To show information about the
        current problem, type the command without arguments.  To show
        information about a specific problem, type its number.  To show
        information about the previous problem, type `-`.
        """
        self.problemset.get_problem(*args).print()

    def command_next(self, *args):
        """
        Choose the next problem to solve. The next problem is selected
        from the easiest problems listed in the current book. To choose
        a problem from a specific list, type its index as argument. To
        choose a problem from the entire problemset, type `-` as
        argument.
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

    def command_queue(self, *args):
        """
        Show live queue from online judge. It displays the last ten
        submissions sent to the judge by any user. To list more than ten
        entries up to 100, type a number as argument. To see only your
        last submissions, use the command `check` instead.
        """
        entries = int(args[0]) if args else 10
        self.uhunt.queue(entries)

    def command_download(self, *args):
        """
        Download a problem's statement. To download the statement of the
        current problem, type the command without arguments.  To
        download a specific problem, type its number.  To download the
        previous problem, type `-`.
        """
        problem = self.problemset.get_problem(*args)
        if os.path.exists(problem.filename):
            self.console.print('File already exists')
        else:
            size = problem.download()

    def command_open(self, *args):
        """
        Open a problem's statement in a pdf viewer. If the statement
        file does not exist, it is downloaded first.  To open the
        current problem, type the command without arguments.  To open
        a specific problem, type its number.  To open the previous
        problem, type `-`.
        """
        problem = self.problemset.get_problem(*args)
        if not os.path.exists(problem.filename):
            self.command_download(*args)
        self.process.open('pdfviewer', problem.filename)

    def command_user(self, *args):
        """
        Display account username. To display information about the
        current account, type the command without arguments. To set the
        account to a specific user, type its username as argument. The
        password is not required.
        """
        if args:
            self.account.set(args[0])
        if self.account.user:
            self.console.alternate('User', self.account.user,
                                   ' ID', self.account.id,
                                   ' Name', self.account.name,
                                   ' Submissions', self.history.count)
        else:
            self.console.alternate('Account not defined. Type',
                                   'user `username`',
                                   'to set current user.')

    def command_update(self, *args):
        """
        Download and update data. It includes submission data from
        account user and statistics for all problems. Book descriptors
        are downloaded only if they don't exist.
        """
        self.console.print('Retrieving submission data...')
        self.history.update()

    def command_volume(self, *args):
        """
        List all problems from a volume set. To see an overview of all
        volumes, type the command without arguments. To list the
        problems of a specific volume, type its number as argument.
        """
        try:
            self.problemset.list_volumes(int(args[0]) if args else None)
        except ValueError:
            raise Exception("invalid volume number: %s", args[0])

    def command_add(self, *args):
        """
        Start solving a new problem. The problem is added to the list of
        problems being solved and is selected as the current problem.
        A source code file for the problem will be created and opened.
        To add a specific problem, type its number. To add the previous
        problem, type `-`.
        """
        problem = self.problemset.get_problem(*args, ignore_current=True)
        self.workbench.add(problem)
        self.workbench.select(problem)
        self.workbench.edit()

    def command_edit(self, *args):
        """
        Edit a source code or a test case. This operation opens the
        default text editor with the required file. There must be
        a problem currently being solved (see `add` and `select`). To
        edit the source code for the current problem, type the command
        without arguments. To edit a test case, type its name as
        argument. To add a new test case, type `+`. A letter will be
        used to identify the test case, starting from "a".
        """
        if not args:
            self.workbench.edit()
        else:
            test = args[0] if args[0] != '+' else None
            self.workbench.edit_test(test)

    def command_select(self, *args):
        """
        Change the current problem being solved. The problem must have
        been added previously with the command `add`. To list all
        problems that have been added, type the command without
        arguments. To select a specific problem, type its number as
        argument. To select the previous problem, type `-`.
        """
        problem = self.problemset.get_problem(*args, accept_none=True,
                                              ignore_current=True)
        self.workbench.select(problem)

    def command_remove(self, *args):
        """
        Remove a problem that is being solved. All data related to the
        problem will be permanently removed, except for its archived
        solution (see `archive`). The problem's number must be typed as
        argument.
        """
        problem = self.problemset.get_problem(*args, ignore_current=True)
        assert problem in self.workbench.works, 'problem is not being solved'
        self.workbench.remove(problem)

    def command_compile(self, *args):
        """
        Compile the current problem's source code. The command line to
        compile is defined in the settings. The default command is the
        same used by UVa Online Judge.
        """
        self.workbench.compile()

    def command_test(self, *args):
        """
        Run the solution against a set of tests. All files with ".in"
        extension are considered input test cases. A test case may have
        an answer file indicated by ".ans" extension. To run all test
        cases, type this command without arguments. To run a subset of
        tests, type their names separated by space. To add or edit
        a test case, use the command `edit`. If the source code was
        modified, it will be compiled before the tests (see `compile`).
        """
        self.workbench.test(*args)

    def command_files(self, *args):
        """
        List all files used in the current problem. The file name and
        the date when it was last modified is listed. The source code
        and the test case files are highlighted.
        """
        self.workbench.files()

    def command_submit(self, *args):
        """
        Submit the solution to online judge. In order to connect to the
        online judge server, a valid account with password is required
        (see `password`). All submissions and evaluation scores can be
        checked with the commands `queue` and `check`.
        """
        self.uva.submit()

    def command_check(self, *args):
        """
        Check your last submissions. It displays your last ten
        submissions sent to the online judge. To list more than ten
        entries up to 100, type a number as argument. To see the
        submissions from any user, use the command `queue` instead.
        """
        entries = int(args[0]) if args else 10
        self.history.last_submissions(entries)
