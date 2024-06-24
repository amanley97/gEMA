# gEMA/manager.py

import os
from datetime import datetime
from gem5.utils.multiprocessing import Process
from gem5.simulate.simulator import Simulator


class gEMASimManager:
    def __init__(self, root) -> None:
        """Initialize the gEMA simulation manager class."""
        self.root = root

    def get_lowest_sim_id(self, config_id):
        """Returns the lowest possible simulation ID that is not already in use."""
        sim_id = 1
        sims = self.root.sims[f"config_{config_id}"]['simulations']
        existing_sim_ids = {simulation["sim_id"] for simulation in sims}

        while sim_id in existing_sim_ids:
            sim_id += 1
        return sim_id

    def save_sim(self, sim_id, config_id):
        """Saves the simulation information tied to the configuration."""
        if self.root.sims.get(f"config_{config_id}") is not None:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log=f"{os.getcwd()}/m5out/config_{config_id}_sim_{sim_id}"
            tmp_storage = dict(sim_id=sim_id, simulated_on=timestamp, logs=log)
            self.root.sims[f"config_{config_id}"]['simulations'].append(tmp_storage)

    def start_subprocess(self, sim_id, config_id):
        """Uses gem5 multiprocessing to start the simulation as a subprocess."""
        self.save_sim(sim_id, config_id)
        process = Process(
            target=self.run_gem5_simulator, args=(sim_id, config_id), name=f"config_{config_id}_sim_{sim_id}"
        )
        process.start()

    def run_gem5_simulator(self, sim_id, config_id):
        """Generates the config and runs the simulation."""
        print(f"Simulation ID: {sim_id} PPID: {os.getppid()} PID: {os.getpid()}")
        config = self.root.sims.get(f"config_{config_id}").get("config")
        board = self.root.configurator.generate_config(config)

        simulator = Simulator(board=board)
        simulator.run()
        print(
            f"Exiting @ tick {simulator.get_current_tick()} because {simulator.get_last_exit_event_cause()}."
        )
