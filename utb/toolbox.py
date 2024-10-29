from collections import OrderedDict
import json
import os
import yaml

from .book import Book
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
        self.load_books()

    def load_books(self):
        self.books = OrderedDict()
        for index in range(self.config.get('number-books', 4)):
            filename = os.path.join(self.config.get('data-dir', '.data'),
                                    'book-%d.json' % (index + 1))
            if os.path.isfile(filename):
                with open(filename) as stream:
                    data = json.loads(stream.read())
                    self.books[index + 1] = Book.parse(index + 1, data)

    def run(self):
        self.console.run()
