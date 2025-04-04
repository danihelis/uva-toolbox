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
import shlex
import subprocess


class Process:

    def __init__(self, toolbox):
        self.toolbox = toolbox

    def open(self, command, *args, **kwargs):
        command = self.toolbox.get(command).format(*args, **kwargs)
        params = shlex.split(command)
        self.toolbox.console.alternate('Executing', command)
        process = subprocess.Popen(params,
                                   stdout=subprocess.DEVNULL,
                                   stderr=subprocess.DEVNULL)

    def run(self,
            command,
            *args,
            dir=None,
            echo=True,
            shell=True,
            timeout=None,
            language=False,
            **kwargs):
        method = 'get_language' if language else 'get'
        command = getattr(self.toolbox, method)(command).format(*args, **kwargs)
        if echo:
            self.toolbox.console.alternate('Executing', command)
        output = subprocess.PIPE if echo else subprocess.DEVNULL
        try:
            process = subprocess.run(command,
                                     shell=shell,
                                     check=False,
                                     stdout=output,
                                     stderr=subprocess.STDOUT,
                                     text=True,
                                     cwd=dir,
                                     timeout=timeout)
        except subprocess.TimeoutExpired:
            process.kill()
            if echo:
                self.toolbox.console.print('Timeout expired')
            return -1
        if echo:
            if process.stdout:
                self.toolbox.console.write(process.stdout)
            if process.returncode == 0:
                self.toolbox.console.print('Success', bold=True)
            else:
                self.toolbox.console.print('Command ended with error status',
                                           bold=True)
        return process.returncode
