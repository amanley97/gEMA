# gEMA/obtain.py
# Obtains available configuration oftions from gem5.

import inspect, json
from .configure import *
from gem5.components import *
from gem5.components.boards.simple_board import SimpleBoard
from gem5.components.boards.x86_board import X86Board
from gem5.components.memory import multi_channel, single_channel
from gem5.components.processors.cpu_types import get_cpu_types_str_set
from gem5.components.processors.simple_processor import SimpleProcessor


def collect_memory_functions(module):
    return [name for name, obj in inspect.getmembers(module) if inspect.isfunction(obj)]


# Collecting functions from memory modules
single_channel_memory = collect_memory_functions(single_channel)
multi_channel_memory = collect_memory_functions(multi_channel)


def get_init_parameters(*classes):
    params_dict = {
        cls.__name__: [
            param
            for param in inspect.signature(cls.__init__).parameters
            if param not in ("self", "cls", "*args", "**kwargs")
        ]
        for cls in classes
    }
    return params_dict


def get_config_opts():
    try:
        cache_types = [
            "NoCache",
            "PrivateL1SharedL2CacheHierarchy",
            "PrivateL1PrivateL2CacheHierarchy",
            "PrivateL1CacheHierarchy",
        ]  # TODO: Fetch the cache types dynamically.
        cache_class_objects = [
            globals()[name] for name in cache_types if name in globals()
        ]

        classes_to_inspect = [
            SimpleBoard,
            X86Board,
            SimpleProcessor,
            *cache_class_objects,
        ]
        class_params = get_init_parameters(*classes_to_inspect)

        mem_types = single_channel_memory + multi_channel_memory
        board_config = {}
        for board_class in [SimpleBoard, X86Board]:
            board_name = board_class.__name__
            cpu_types = list(get_cpu_types_str_set())
            board_config[board_name] = {
                "clk_freq": class_params[board_name],
                "Memory": mem_types,
                "Processor": cpu_types,
                "Cache Hierarchy": {
                    name: class_params[name]
                    for name in cache_types
                    if name in class_params
                },
            }

        json_config = json.dumps(board_config, indent=2)
        return json_config.encode("utf-8")
    except KeyError as e:
        print(f"Key error: {e} - Check if cache class names are correct and imported")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
