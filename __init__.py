# gEMA/__init__.py
# gEMA: gem5 External Modules API

__version__ = "0.1"
__all__ = ["gEMA"]

# Import the gEMA class from the gEMA.py file
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info(f"gEMA initialized. version: {__version__}")

from gEMA.config import gEMAConfigGenerator, gEMAConfigRetreiver
from gEMA.manager import gEMASimManager
from gEMA.server import gEMAServer


class gEMA:
    """Main application class."""

    def __init__(self, port):
        self.configurator = gEMAConfigGenerator(self)
        self.retriever = gEMAConfigRetreiver(self)
        self.manager = gEMASimManager(self)
        self.server = gEMAServer(self, port)
        self.configs = {}
        self.sims = {}

    def run(self):
        self.server.run()
