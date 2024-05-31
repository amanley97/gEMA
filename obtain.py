# gEMA/obtain.py
import inspect, json
from .configure import *
from gem5.components import *
from gem5.components.boards.simple_board import SimpleBoard
from gem5.components.boards.x86_board import X86Board
from gem5.components.memory import dram_interfaces, multi_channel, single_channel
from gem5.components.processors.cpu_types import get_cpu_types_str_set
from gem5.components.processors.simple_processor import SimpleProcessor

MemTypes = {name:obj for name,obj in inspect.getmembers(dram_interfaces, inspect.ismodule)}
def collect_memory_functions(module):
    function_names = []
    for name, obj in inspect.getmembers(module):
        if inspect.isfunction(obj):
            function_names.append(name)
    return function_names

# Collecting functions from both modules
single_channel_memory = collect_memory_functions(single_channel)
multi_channel_memory = collect_memory_functions(multi_channel)
def get_init_parameters(*classes):
    class_params_dict = {}
    for cls in classes:
        init_signature = inspect.signature(cls.__init__)
        parameters = list(init_signature.parameters.keys())
        # Filter out 'self' and any other non-attribute parameters you don't want
        filtered_parameters = [param for param in parameters if param not in ['self', 'cls', '*args', '**kwargs']]
        class_params_dict[cls.__name__] = filtered_parameters
    return class_params_dict

def get_cls(file, mask):
    cls = []
    for name, obj in inspect.getmembers(file):
        if inspect.isclass(obj) and name != mask:
            cls.append(name)
    return cls

def get_board_types():
    cache_types = ['NoCache', 'PrivateL1SharedL2CacheHierarchy','PrivateL1PrivateL2CacheHierarchy', 'PrivateL1CacheHierarchy'] # TODO - get from gem5 automatically
    cache_class_objects = [globals()[class_name] for class_name in cache_types]
    # List of the classes we want to inspect
    classes_to_inspect = [SimpleBoard, X86Board, SimpleProcessor, *cache_class_objects]
    # Get the dictionary of class names and their init parameters
    board_info = get_init_parameters(*classes_to_inspect)
    for board in ['SimpleBoard', 'X86Board']:
        processor_info = board_info['SimpleProcessor']
        cache_hierarchy_info = {k: board_info[k] for k in cache_types}
        board_info[board] = {
            'clk_freq': [board_info[board][0]],  # Assuming clk_freq is a string and not another key
            'Memory': [board_info[board][2], "size"],  # Assuming memory is a string and not another key
            'Processor': processor_info,
            'Cache Hierarchy': cache_hierarchy_info
        }
    # Remove extra items from the dictionary
    for key in ['SimpleProcessor', *cache_types]:
        board_info.pop(key, None)

    board_types = {}
    for name, idx in board_info.items():
        # print(name, idx)
        board_types.update({name : idx})
    board_types_b = json.dumps(board_types, indent=2).encode('utf-8')
    return board_types_b

def get_mem_types():
    # mem_types = {}
    # for name, idx in MemTypes.items():
    #     mem_types.update({name : get_cls(idx, 'DRAMInterface')})
    mem_types = single_channel_memory + multi_channel_memory
    mem_types_b = json.dumps(mem_types, indent=2).encode('utf-8')
    # print("MTB", mem_types_b)
    return mem_types_b

def get_cpu_types():
    cpu_types = list(get_cpu_types_str_set())
    cpu_types_b = json.dumps(cpu_types, indent=2).encode('utf-8')
    return cpu_types_b
