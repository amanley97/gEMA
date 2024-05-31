# gEMA/server.py
import sys, os
from http.server import HTTPServer
from .handler import BackendHandler
from .obtain import *

class BackendServer:
    def __init__(self, port=5000):
        self.port = port
        self.brd_config = None
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
        server_address = ('', self.port)
        httpd = HTTPServer(server_address, self.handler)

        print(f'Starting server on port {self.port}...')
        httpd.serve_forever()

    def run_gem5_simulator(self):
        with open("./m5out/stats.txt", 'r+') as file:
            file.seek(0)
            file.truncate()

        with open('m5out/output.txt', "w") as f:
            sys.stdout = f
            sys.stderr = f
            print("Simulation PID: ", os.getpid())
            user_id = 'default'
            data = self.handler.user_data_storage.get(user_id)
            if self.brd_config is None:
                self.brd_config = generate_config(data)
            else:
                del self.brd_config
                self.brd_config = generate_config(data)
            simulator = Simulator(board=self.brd_config)
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
