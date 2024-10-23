from .toolbox import Toolbox
__all__ = ['init']

def init(config):
    toolbox = Toolbox(config)
    toolbox.run()
