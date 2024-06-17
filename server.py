# gEMA/server.py
import sys, os
from http.server import HTTPServer
from .handler import BackendHandler
from .obtain import *


class BackendServer:
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
        with open("./m5out/stats.txt", "r+") as file:
            file.seek(0)
            file.truncate()

        with open(f"m5out/output{id}.txt", "w") as f:
            sys.stdout = f
            sys.stderr = f
            print(f"Simulation ID: {id} PID: {os.getpid()}")
            self.config = self.handler.saved_configs.get(id)
            if self.config is None:
                print("Failed to obtain config.")
            else:
                print(f"Received config for id: {id}")
                simulator = Simulator(board=self.config)
                simulator.run()
                print(
                    "Exiting @ tick {} because {}.".format(
                        simulator.get_current_tick(), simulator.get_last_exit_event_cause()
                    )
                )
                sys.stdout.flush()
                sys.stderr.flush()

        dump()
        reset()
        m5.statsreset()
