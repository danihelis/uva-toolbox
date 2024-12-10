import os
import subprocess

class Process:

    def __init__(self, toolbox):
        self.toolbox = toolbox

    def open(self, command, *args, **kwords):
        exec_params = self.toolbox.get(command).format(*args, **kwords).split()
        self.toolbox.console.alternate('Executing', ' '.join(exec_params))
        process = subprocess.Popen(exec_params, stdout=subprocess.DEVNULL,
                                   stderr=subprocess.DEVNULL)
