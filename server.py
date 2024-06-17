# gEMA/server.py
# Runs the gEMA backend and awaits external commands.

import sys, os, copy
from http.server import HTTPServer
from .handler import BackendHandler
from .obtain import *


class gEMAServer:
    def __init__(self, port=5000):
        self.port = port
        self.config = None
        self.handler = self.handler_factory()

    def handler_factory(self):
        # Factory function to create a handler with access to the server instance
        server_instance = self

        class CustomHandler(BackendHandler):
            def __init__(self, *args, **kwargs):
                self.server_instance = server_instance
                super().__init__(*args, **kwargs)

        return CustomHandler

    def run_server(self):
        server_address = ("", self.port)
        httpd = HTTPServer(server_address, self.handler)

        print(f"""
        Starting server on port {self.port}.
        For help, access /help on the server URL or consult the documentation.
        """)
        httpd.serve_forever()

    def run_gem5_simulator(self, id):
        print(f"Simulation ID: {id} PID: {os.getpid()}")
        print(self.handler.saved_configs.get(id))
        self.config = copy.deepcopy(self.handler.saved_configs.get(id)) #TODO: Fix this so that the same config can be run many times
        if self.config is None:
            print("Failed to obtain config.")
        else:
            print(f"Received config for id: {id}")
            simulator = Simulator(board=self.config)
            simulator.run()
            print(f"Exiting @ tick {simulator.get_current_tick()} because {simulator.get_last_exit_event_cause()}.")
        del simulator
        del self.config
        print(self.handler.saved_configs.get(id))
        dump()
        reset()