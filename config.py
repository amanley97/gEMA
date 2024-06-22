# gEMA/config.py

import m5, json, inspect
from datetime import datetime
from gem5.components import *
from gem5.components.processors.cpu_types import *
from gem5.components.memory import *
from gem5.resources.resource import *
from gem5.components.boards.simple_board import SimpleBoard
from gem5.components.cachehierarchies.classic.no_cache import NoCache
from gem5.components.boards.x86_board import X86Board
from gem5.components.memory import multi_channel, single_channel
from gem5.components.processors.cpu_types import get_cpu_types_str_set
from gem5.components.processors.simple_processor import SimpleProcessor
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


class gEMAConfigRetreiver:
    """ Obtains available configuration options from gem5. """

    def __init__(self, root) -> None:
        self.root = root
        self.single_channel_memory = [name for name, obj in inspect.getmembers(single_channel) if inspect.isfunction(obj)]
        self.multi_channel_memory = [name for name, obj in inspect.getmembers(multi_channel) if inspect.isfunction(obj)]
        self.cache_types = [
                "NoCache",
                "PrivateL1SharedL2CacheHierarchy",
                "PrivateL1PrivateL2CacheHierarchy",
                "PrivateL1CacheHierarchy",
            ]  # TODO: Fetch the cache types dynamically.

    def _get_init_parameters(self, *classes):
        params_dict = {
            cls.__name__: [
                param
                for param in inspect.signature(cls.__init__).parameters
                if param not in ("self", "cls", "*args", "**kwargs")
            ]
            for cls in classes
        }
        return params_dict

    def get_config_opts(self):
        try:
            cache_class_objects = [
                globals()[name] for name in self.cache_types if name in globals()
            ]

            classes_to_inspect = [
                SimpleBoard,
                X86Board,
                SimpleProcessor,
                *cache_class_objects,
            ]
            class_params = self._get_init_parameters(*classes_to_inspect)

            mem_types = self.single_channel_memory + self.multi_channel_memory
            config = {}
            for board_class in [SimpleBoard, X86Board]:
                board_name = board_class.__name__
                cpu_types = list(get_cpu_types_str_set())
                config[board_name] = {
                    "clk_freq": class_params[board_name],
                    "Memory": mem_types,
                    "Processor": cpu_types,
                    "Cache Hierarchy": {
                        name: class_params[name]
                        for name in self.cache_types
                        if name in class_params
                    },
                }
            return config
        except KeyError as e:
            print(f"Key error: {e} - Check if cache class names are correct and imported")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

class gEMAConfigGenerator:
    """ Configures a user defined simulation object. """

    def __init__(self, root):
        self.root = root

    def generate_config(self, data):
        brd = eval(data["board"]["type"])
        clk = f"{data['board']['clk']}GHz"
        proc = eval(data["processor"]["type"])
        cpu_type = CPUTypes[data["processor"]["cpu"].upper()]
        isa = ISA[data["processor"]["isa"].upper()]
        ncores = int(data["processor"]["ncores"])
        mem_type = eval(data["memory"]["type"])
        msize = f"{data['memory']['size']}MB"
        cache = self.get_cache_configuration(data["cache"])

        configuration = brd(
            clk_freq=clk,
            processor=proc(cpu_type=cpu_type, isa=isa, num_cores=ncores),
            memory=mem_type(size=msize),
            cache_hierarchy=cache,
        )

        resource_type = data["resource"][0]
        resource = data["resource"][1]
        self.set_resource(configuration, resource_type, resource)

        self.print_config_summary(
            brd, clk, proc, cpu_type, isa, ncores, mem_type, msize, cache
        )

        return configuration

    def save_config(self, id, data=None):
        if self.root.configs.get(f"config_{id}") is not None:
            if data is None:
                print(
                    f"Regenerating configuration for id {id} using previously saved configuration."
                )
                data = self.root.configs.get(f"config_{id}").get("config")
            else:
                print(f"Regenerating configuration for id {id} using new data.")
            del self.root.configs[f"config_{id}"]
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        tmp_storage = dict(sim_id=id, generated_on=timestamp, config=data)
        self.root.configs[f"config_{id}"] = tmp_storage

    def get_cache_configuration(self, cache_config):
        cache_opts = {
            "class": globals()[cache_config["type"]],
            "l1d_size": f"{cache_config['l1d_size']}KiB",
            "l1i_size": f"{cache_config['l1i_size']}KiB",
            "l2_size": f"{cache_config['l2_size']}KiB",
            "l1d_assoc": cache_config["l1d_assoc"],
            "l1i_assoc": cache_config["l1i_assoc"],
            "l2_assoc": cache_config["l2_assoc"],
        }

        cache_params = [
            param
            for param in inspect.signature(cache_opts["class"].__init__).parameters
            if param not in ("self", "cls", "*args", "**kwargs")
        ]

        init_params = {
            key: value for key, value in cache_opts.items() if key in cache_params
        }

        try:
            return cache_opts["class"](**init_params)
        except ValueError:
            print(f"Failed to generate cache: {cache_opts['class']}")

    def set_resource(self, board, resource_type, resource):
        if resource_type == "default":
            board.set_se_binary_workload(obtain_resource(resource))
        elif resource_type == "custom":
            board.set_se_binary_workload(BinaryResource(resource))
        else:
            print("Invalid resource type specified")

    def print_config_summary(
        self, board, clk, proc, cpu, isa, cores, mem_type, mem_size, cache
    ):
        print("\n======CONFIGURATION======")
        print(
            f"Board: {board}, \nClock Frequency: {clk}, \nProcessor: {proc} \nCPU Type: {cpu}, \nISA: {isa}, "
            f"\nNumber of Cores: {cores}, \nMemory Type: {mem_type}, \nMemory Size: {mem_size}, \nCache Type: {cache}\n"
        )

    def json_configuration(self, board):
        config = [
            {
                "object": str(obj),
                "params": {
                    name: {
                        "Type": desc.ptype_str,
                        "Desc": desc.desc,
                        "Default": (
                            str(desc.default) if hasattr(desc, "default") else None
                        ),
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
