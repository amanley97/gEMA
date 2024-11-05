# ----------------------------------------------------------------------------
# File: <options>.py
#
# Description:
# <Handles retrieval of available gem5 configuration options>.
#
# Contact:
# For inquiries, please contact Alex Manley (amanley97@ku.edu).
#
# License:
# This project is licensed under the MIT License. See the LICENSE file
# in the repository root for more information.
# ----------------------------------------------------------------------------

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from gem5.utils.gema import Gema

import inspect

from gem5.components import *
from gem5.components.boards.simple_board import SimpleBoard
from gem5.components.boards.x86_board import X86Board
from gem5.components.boards.arm_board import ArmBoard
from gem5.components.cachehierarchies.classic.no_cache import NoCache
from gem5.components.cachehierarchies.classic.private_l1_cache_hierarchy import (
    PrivateL1CacheHierarchy,
)
from gem5.components.cachehierarchies.classic.private_l1_private_l2_cache_hierarchy import (
    PrivateL1PrivateL2CacheHierarchy,
)
from gem5.components.cachehierarchies.classic.private_l1_shared_l2_cache_hierarchy import (
    PrivateL1SharedL2CacheHierarchy,
)
from gem5.components.memory import *
from gem5.components.memory import (
    multi_channel,
    single_channel,
)
from gem5.components.processors.cpu_types import *
from gem5.components.processors.cpu_types import get_cpu_types_str_set
from gem5.components.processors.simple_processor import SimpleProcessor
from gem5.resources.resource import *
from gem5.utils.gema.rpc_data import *


class GemaOptionRetreiver:
    """A class responsible for discovering and retrieving available gem5 configuration options.

    This class introspectively examines the gem5 library to identify valid configuration
    options for different simulation components, including memory channels, cache
    hierarchies, processors, and boards. It provides a centralized way to discover
    what options are available for configuring a gem5 simulation.

    Attributes:
        root (Gema): Reference to the root Gema object.
        single_channel_memory (list[str]): List of available single-channel memory configurations.
        multi_channel_memory (list[str]): List of available multi-channel memory configurations.
        cache_types (list[str]): List of supported cache hierarchy types.
    """

    def __init__(self, root: Gema) -> None:
        """Initialize the gem5 configuration option retriever.

        This constructor uses introspection to discover available memory configurations
        and initializes the list of supported cache hierarchy types.

        Args:
            root (Gema): Reference to the root Gema object that this retriever is
                        associated with. This object provides context for the configuration
                        discovery process.
        """
        self.root = root
        # Discover available single-channel memory configurations through introspection
        self.single_channel_memory = [
            name
            for name, obj in inspect.getmembers(single_channel)
            if inspect.isfunction(obj)
        ]
        # Discover available multi-channel memory configurations through introspection
        self.multi_channel_memory = [
            name
            for name, obj in inspect.getmembers(multi_channel)
            if inspect.isfunction(obj)
        ]
        # Define supported cache hierarchy types
        self.cache_types = [
            "NoCache",
            "PrivateL1SharedL2CacheHierarchy",
            "PrivateL1PrivateL2CacheHierarchy",
            "PrivateL1CacheHierarchy",
        ]

    def _get_init_parameters(self, *classes):
        """Extract initialization parameters from the provided classes.

        This method uses introspection to examine the __init__ methods of the provided
        classes and extract their parameter lists, excluding standard Python parameters
        like self, cls, and variable argument parameters.

        Args:
            *classes: Variable number of class objects to inspect.

        Returns:
            dict: A dictionary mapping class names to lists of their initialization
                 parameters. The format is:
                 {
                     'ClassName': ['param1', 'param2', ...],
                     ...
                 }

        Example:
            For a class with __init__(self, param1, param2), the result would include:
            {'ClassName': ['param1', 'param2']}
        """
        return {
            cls.__name__: [
                param
                for param in inspect.signature(cls.__init__).parameters
                if param not in ("self", "cls", "*args", "**kwargs")
            ]
            for cls in classes
        }

    def get_config_options(self):
        """Retrieve all available configuration options from the gem5 library.

        This method performs a comprehensive discovery of configuration options by:
        1. Loading available cache classes based on supported types
        2. Inspecting board, processor, and cache classes for their parameters
        3. Organizing the options into a structured configuration dictionary

        Returns:
            dict: A nested dictionary containing all available configuration options,
                 organized by board type. The structure is:
                 {
                     'BoardType': {
                         'board': [parameters],
                         'memory': [available_memory_types],
                         'processor': [available_cpu_types],
                         'cache_hierarchy': {
                             'CacheType': [parameters],
                             ...
                         }
                     },
                     ...
                 }
                 Returns None if an error occurs during the discovery process.

        Note:
            - The method handles both KeyError and general exceptions silently,
              returning None in case of any error
            - Memory types include both single and multi-channel configurations
            - Processor types are obtained from gem5's CPU type registry
            - Cache parameters are collected for all supported cache hierarchy types
        """
        cache_classes = [
            globals()[name] for name in self.cache_types if name in globals()
        ]
        classes_to_inspect = [
            SimpleBoard,
            X86Board,
            ArmBoard,
            SimpleProcessor,
            *cache_classes,
        ]

        try:
            class_params = self._get_init_parameters(*classes_to_inspect)
            config = {}

            for board_class in [SimpleBoard, X86Board, ArmBoard]:
                board_name = board_class.__name__
                config[board_name] = {
                    "board": class_params[board_name][0],
                    "memory": self.single_channel_memory
                    + self.multi_channel_memory,
                    "processor": list(get_cpu_types_str_set()),
                    "cache_hierarchy": {
                        name: class_params[name]
                        for name in self.cache_types
                        if name in class_params
                    },
                }
            return config
        except KeyError:
            # Handle missing key in dictionary operations
            pass
        except Exception:
            # Handle any other unexpected errors during configuration discovery
            pass
