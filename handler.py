# gEMA/handler.py
# Handles API endpoints.

import json, os
from gem5.utils.multiprocessing import Process
from http.server import BaseHTTPRequestHandler
from .obtain import get_config_opts
from .configure import gEMAConfigurator


class gEMAHandler(BaseHTTPRequestHandler):
    configurator = gEMAConfigurator()

    def _set_headers(self, status=200, content_type="application/json"):
        """Helper method to set HTTP response headers."""
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.end_headers()

    def _not_found(self):
        """Send a 404 Not Found response."""
        self.send_error(404, "Not Found")

    def do_GET(self):
        """Handle GET requests."""
        endpoints = {
            "/config/options": self.send_config_options,
            "/config/saved": self.send_saved_configs,
            "/help": self.list_endpoints,
        }
        handler = endpoints.get(self.path, self._not_found)
        handler()

    def do_PUT(self):
        """Handle PUT requests."""
        path = self.path.split("/")

        if self.path == "/shutdown":
            self.handle_shutdown()
        elif len(path) == 4 and path[1] == "simulation":
            sim_id = path[2]
            if path[3] == "run":
                self.handle_run_simulator(sim_id)
            elif path[3] == "configure":
                self.handle_external_data(sim_id)
            else:
                self.wfile.write(b"Simulation subcommand invalid.")
        else:
            self._not_found()

    def send_config_options(self):
        """Send configuration options to the client."""
        self._set_headers()
        self.wfile.write(get_config_opts())

    def send_saved_configs(self):
        """Send saved configurations to the client."""

        def filter_objects(data, exclude_keys):
            if isinstance(data, dict):
                return {
                    k: filter_objects(v, exclude_keys)
                    for k, v in data.items()
                    if k not in exclude_keys
                }
            elif isinstance(data, list):
                return [filter_objects(item, exclude_keys) for item in data]
            else:
                return data

        self._set_headers()
        json_configs = filter_objects(self.configurator.configs, "object")
        self.wfile.write(json.dumps(json_configs, indent=4).encode())

    def list_endpoints(self):
        """List available HTTP endpoints."""
        self._set_headers()
        endpoints = {
            "GET /help": "Displays available endpoints",
            "GET /config/options": "Get configuration options",
            "GET /config/saved": "Get saved configurations",
            "PUT /simulation/{sim_id}/configure": "Submit user data for simulation configuration",
            "PUT /simulation/{sim_id}/run": "Run the gem5 simulation",
            "PUT /shutdown": "Shutdown the server",
        }
        self.wfile.write(json.dumps(endpoints, indent=4).encode())

    def handle_run_simulator(self, id):
        """Handle request to run a simulation in a separate process."""
        self._set_headers()
        process = Process(target=self.configurator.run_gem5_simulator, args=(id,))
        process.start()
        self.wfile.write((f"Starting simulation id: {id}\n").encode())
        process.join()
        self.wfile.write(b"Simulation Complete\n")

    def handle_shutdown(self):
        """Handle request to shutdown the server."""
        self._set_headers()
        self.wfile.write(b"Shutting down server\n")
        self.wfile.flush()
        print(f"Terminating process {os.getpid()}.")
        os._exit(0)

    def handle_external_data(self, id):
        """Handle request to store user data."""
        try:
            content_length = int(self.headers["Content-Length"])
            data = self.rfile.read(content_length)
            received_data = json.loads(data.decode("utf-8"))
            self.configurator.save_config(id, received_data)

            print(f"sim_id: {id} generated.")
            msg = f"Configured gem5 object, sim_id: {id}. Ready to Simulate!".encode()
            self._set_headers()
            self.wfile.write(msg)
        except Exception as e:
            self.send_error(500, f"Internal Server Error: {str(e)}")
