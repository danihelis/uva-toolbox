import os
import yaml

from .console import Console

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

    def run(self):
        self.console.run()
