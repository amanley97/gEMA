# gEMA/__init__.py
# gEMA: gem5 External Modules API


__version__ = "0.1"
from .server import *

# Optional: Define what is available for `from my_package import *`
# __all__ = ['hello', 'goodbye']

# Initialization code, e.g., setting up a logger
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info(f"initialized. version: {__version__}")
