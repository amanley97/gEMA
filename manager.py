# gEMA/manager.py

import os
from gem5.utils.multiprocessing import Process
from gem5.simulate.simulator import Simulator


class gEMASimManager:
    def __init__(self, root) -> None:
        self.root = root

    def start_subprocess(self, id):
        process = Process(
            target=self.run_gem5_simulator, args=(id,), name=f"simulation_{id}"
        )
        process.start()

    def run_gem5_simulator(self, id):
        print(f"Simulation ID: {id} PPID: {os.getppid()} PID: {os.getpid()}")
        board = self.root.configurator.generate_config(
            self.root.configs.get(f"config_{id}").get("config")
        )

        simulator = Simulator(board=board)
        simulator.run()
        print(
            f"Exiting @ tick {simulator.get_current_tick()} because {simulator.get_last_exit_event_cause()}."
        )
