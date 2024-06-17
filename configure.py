# gEMA/configure.py
# Configures a user defined simulation object.

import m5, json, inspect
from gem5.components import *
from gem5.components.processors.cpu_types import *
from gem5.components.memory import *
from m5.stats import *
from gem5.resources.resource import *
from gem5.simulate.simulator import Simulator
from gem5.components.boards.simple_board import SimpleBoard
from gem5.components.cachehierarchies.classic.no_cache import NoCache
from gem5.components.cachehierarchies.classic.private_l1_shared_l2_cache_hierarchy import (
    PrivateL1SharedL2CacheHierarchy,
)
from gem5.components.cachehierarchies.classic.private_l1_private_l2_cache_hierarchy import (
    PrivateL1PrivateL2CacheHierarchy,
)
from gem5.components.cachehierarchies.classic.private_l1_cache_hierarchy import (
    PrivateL1CacheHierarchy,
)
from gem5.components.processors.simple_processor import SimpleProcessor

def generate_config(board_info):
    brd = eval(board_info["board"]["type"])
    clk = f"{board_info['board']['clk']}GHz"
    proc = eval(board_info["processor"]["type"])
    cpu_type = CPUTypes[board_info["processor"]["cpu"].upper()]
    isa = ISA[board_info["processor"]["isa"].upper()]
    ncores = int(board_info["processor"]["ncores"])
    mem_type = eval(board_info["memory"]["type"])
    msize = f"{board_info['memory']['size']}MB"
    cache = get_cache_configuration(board_info["cache"])

    configuration = brd(
        clk_freq=clk,
        processor=proc(cpu_type=cpu_type, isa=isa, num_cores=ncores),
        memory=mem_type(size=msize),
        cache_hierarchy=cache,
    )

    resource_type = board_info["resource"][0]
    resource = board_info["resource"][1]
    set_resource(configuration, resource_type, resource) 

    print_config_summary(brd, clk, cpu_type, isa, ncores, mem_type, msize, cache)

    return configuration


def get_cache_configuration(cache_config):
    cache_opts = {
        "class" : globals()[cache_config["type"]],
        "l1d_size" : f"{cache_config['l1d_size']}KiB",
        "l1i_size" : f"{cache_config['l1i_size']}KiB",
        "l2_size" : f"{cache_config['l2_size']}KiB",
        "l1d_assoc" : cache_config["l1d_assoc"],
        "l1i_assoc" : cache_config["l1i_assoc"],
        "l2_assoc" : cache_config["l2_assoc"]
        }

    cache_params = [
        param
        for param in inspect.signature(cache_opts["class"].__init__).parameters
        if param not in ("self", "cls", "*args", "**kwargs")
        ]

    init_params = {key: value for key, value in cache_opts.items() if key in cache_params}

    try:
        return cache_opts["class"](**init_params)
    except ValueError:
        print(f"Failed to generate cache: {cache_opts['class']}")


def set_resource(board, resource_type, resource):
    if resource_type == "default":
        board.set_se_binary_workload(obtain_resource(resource))
    elif resource_type == "custom":
        board.set_se_binary_workload(BinaryResource(resource))
    else:
        print("Invalid resource type specified")


def print_config_summary(board, clk, cpu, isa, cores, mem_type, mem_size, cache):
    print("\n======CONFIGURATION======")
    print(
        f"Board: {board}, \nClock Frequency: {clk}, \nCPU Type: {cpu}, \nISA: {isa}, "
        f"\nNumber of Cores: {cores}, \nMemory Type: {mem_type}, \nMemory Size: {mem_size}, \nCache Type: {cache}\n"
    )


def json_configuration(board):
    config = [
        {
            "object": str(obj),
            "params": {
                name: {
                    "Type": desc.ptype_str,
                    "Desc": desc.desc,
                    "Default": str(desc.default) if hasattr(desc, "default") else None,
                }
                for name, desc in obj._params.items()
            },
            "ports": {
                name: {
                    "Role": desc.role,
                    "Is source": desc.is_source,
                    "Is vector": isinstance(desc, m5.params.VectorPort),
                    "Desc": desc.desc,
                }
                for name, desc in obj._ports.items()
            },
        }
        for obj in board.descendants()
    ]

    with open("./m5out/config.json", "w") as file:
        json.dump(config, file, indent=4)
