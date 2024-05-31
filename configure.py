# gEMA/configure.py
import m5, json
from gem5.components import *
from gem5.components.processors.cpu_types import *
from gem5.components.memory import *
from gem5.components import *
from m5.stats import *
from gem5.resources.resource import *
from gem5.simulate.simulator import Simulator
from gem5.components.boards.simple_board import SimpleBoard
from gem5.components.cachehierarchies.classic.no_cache import NoCache
from gem5.components.cachehierarchies.classic.private_l1_shared_l2_cache_hierarchy import PrivateL1SharedL2CacheHierarchy
from gem5.components.cachehierarchies.classic.private_l1_private_l2_cache_hierarchy import PrivateL1PrivateL2CacheHierarchy
from gem5.components.cachehierarchies.classic.private_l1_cache_hierarchy import PrivateL1CacheHierarchy
from gem5.components.processors.simple_processor import SimpleProcessor

def generate_config(board_info):
    brd = str(board_info['Board Configuration']['type'])
    clk = str(board_info['Board Configuration']['clk']) + "GHz"
    cpu = eval("CPUTypes." + str(board_info['Processor Configuration']['type']).upper())
    isa = eval(board_info['Processor Configuration']['isa'])
    ncores = int(board_info['Processor Configuration']['ncores'])
    mem = eval(board_info['Memory Configuration']['type'])
    msize = str(board_info['Memory Configuration']['size']) + "MB"
    cache_type = board_info['Cache Configuration']['type']
    cache = None
    cache_for_display = ""
    if cache_type == "NoCache":
        cache = eval(board_info['Cache Configuration']['type'] + "()")
        cache_for_display = board_info['Cache Configuration']['type']
    elif cache_type == "PrivateL1CacheHierarchy":
        cache = PrivateL1CacheHierarchy(
            l1d_size = str(board_info['Cache Configuration']['l1d_size']) + "KiB",
            l1i_size = str(board_info['Cache Configuration']['l1i_size']) + "KiB"
        )
        cache_for_display = str(board_info['Cache Configuration']['type']) + "\nL1d: " +str(board_info['Cache Configuration']['l1d_size']) + "KiB" + "\nL1i: " +str(board_info['Cache Configuration']['l1i_size']).replace(",","") + "KiB"
    elif cache_type == "PrivateL1SharedL2CacheHierarchy":
        cache = PrivateL1SharedL2CacheHierarchy(
            l1d_size=str(board_info['Cache Configuration']['l1d_size']) + "KiB",
            l1i_size=str(board_info['Cache Configuration']['l1i_size']) + "KiB",
            l2_size=str(board_info['Cache Configuration']['l2_size']) + "KiB",
            l1d_assoc = board_info['Cache Configuration']['l1d_assoc'],
            l1i_assoc = board_info['Cache Configuration']['l1i_assoc'],
            l2_assoc = board_info['Cache Configuration']['l2_assoc']
        )
        cache_for_display = str(board_info['Cache Configuration']['type']) + "\nL1d: " +str(board_info['Cache Configuration']['l1d_size']) + "KiB" + "\nL1i: " +str(board_info['Cache Configuration']['l1i_size']) + "KiB" + "\nL2: " +str(board_info['Cache Configuration']['l2_size']) + "KiB" + "\nL1d_assoc: " +str(board_info['Cache Configuration']['l1d_assoc']) + "\nL1i_assoc: " +str(board_info['Cache Configuration']['l1i_assoc']) + "\nL2_assoc: " +str(board_info['Cache Configuration']['l2_assoc']).replace(",","")
    elif cache_type == "PrivateL1PrivateL2CacheHierarchy":
        cache = PrivateL1PrivateL2CacheHierarchy(
            l1d_size = str(board_info['Cache Configuration']['l1d_size']) + "KiB",
            l1i_size = str(board_info['Cache Configuration']['l1i_size']) + "KiB",
            l2_size = str(board_info['Cache Configuration']['l2_size']) + "KiB"
        )
        cache_for_display = str(board_info['Cache Configuration']['type']) + "\nL1d: " +str(board_info['Cache Configuration']['l1d_size']) + "KiB" + "\nL1i: " +str(board_info['Cache Configuration']['l1i_size']) + "KiB" +  "\nL2: " +str(board_info['Cache Configuration']['l2_size']).replace(",","") + "KiB"

    rtype = board_info['resource'][0]
    resource = str(board_info['resource'][1])
    print("\n======CONFIGURATION======")

    print(f"Board: {brd}, \nClock Frequency: {clk}, \nCPU Type: {cpu}, \nISA: {isa}, \nNumber of Cores: {ncores}, \nMemory Type: {mem}, \nMemory Size: {msize}, \nCache Type: {cache_for_display}, \nUsing Resource: {resource}\n")

    #TODO: Add support for other board types

    configuration = SimpleBoard(
        clk_freq=clk,
        processor=SimpleProcessor(cpu_type=cpu, isa=isa, num_cores=ncores),
        memory=mem(size=msize),
        cache_hierarchy=cache
    )

    if rtype == 'default':
        configuration.set_se_binary_workload(
            obtain_resource(resource)
        )
    elif rtype == 'custom':
        configuration.set_se_binary_workload(
            BinaryResource(resource)
        )
    else:
        print("invalid resource")

    json_configuration(configuration)
    return configuration

def json_configuration(brd):
        config = []
        
        for obj in brd.descendants():
            obj_info = {
                "object": str(obj),
                "params": {},
                "ports": {}
            }
            
            for name, desc in obj._params.items():
                param_info = {
                    "Type": desc.ptype_str,
                    "Desc": desc.desc
                }
                if hasattr(desc, 'default'):
                    try:
                        json.dumps(desc.default)  # Test if default is JSON serializable
                        param_info["Default"] = desc.default
                    except (TypeError, ValueError):
                        param_info["Default"] = str(desc.default)  # Convert to string if not serializable
                obj_info["params"][name] = param_info
            
            for name, desc in obj._ports.items():
                port_info = {
                    "Role": desc.role,
                    "Is source": desc.is_source,
                    "Is vector": isinstance(desc, m5.params.VectorPort),
                    "Desc": desc.desc
                }
                obj_info["ports"][name] = port_info
            
            config.append(obj_info)
        
            with open('./m5out/config.json', 'w') as file:
                json.dump(config, file, indent=4)
