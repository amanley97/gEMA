# gEMA/gEMA.py

from gEMA.config import gEMAConfigGenerator, gEMAConfigRetreiver
from gEMA.manager import gEMASimManager
from gEMA.server import gEMAServer

class gEMA:
    """ Main application class. """

    def __init__(self, port):
        self.configurator = gEMAConfigGenerator(self)
        self.retriever = gEMAConfigRetreiver(self)
        self.manager = gEMASimManager(self)
        self.server = gEMAServer(self, port)
        self.configs = {}
        self.sims = {}

    def run(self):
        self.server.run()
