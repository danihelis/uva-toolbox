import os
import subprocess

class Process:

    def __init__(self, toolbox):
        self.toolbox = toolbox

    def open(self, command, *args, console=None, **kwords):
        exec_params = self.toolbox.get(command).format(*args, **kwords).split()
        if console:
            console.write('Executing:', end=' ')
            console.write(' '.join(exec_params), bold=True)
        process = subprocess.Popen(exec_params, stdout=subprocess.DEVNULL,
                                   stderr=subprocess.DEVNULL)
