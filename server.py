# gEMA/server.py

import json, os
from http.server import BaseHTTPRequestHandler, HTTPServer as gEMAHTTP


class gEMAServer:
    """Server class for managing gEMA backend operations."""

    def __init__(self, root, port):
        self.root = root
        self.port = port
        self.handler = lambda *args, **kwargs: gEMAHandler(self.root, *args, **kwargs)

    def run(self):
        server_address = ("", self.port)
        gEMAhttp = gEMAHTTP(server_address, self.handler)
        print(f"Starting server on port {self.port}.")
        print("For help, access /help on the server URL or consult the documentation.")
        gEMAhttp.serve_forever()


class gEMAHandler(BaseHTTPRequestHandler):
    """HTTP request handler with routes defined for service operations."""

    def __init__(self, root, *args, **kwargs):
        self.root = root
        super().__init__(*args, **kwargs)

    def _set_headers(self, status=200, content_type="application/json"):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Connection", "close")
        self.end_headers()

    def _send_output(self, data):
        self._set_headers()
        response = json.dumps(data, indent=4).encode()
        self.wfile.write(response)

    def _not_found(self):
        self.send_error(404, "Not Found")

    def do_GET(self):
        endpoints = {
            "/config/options": self.send_config_options,
            "/config/saved": self.send_saved_configs,
            "/help": self.list_endpoints,
        }
        handler = endpoints.get(self.path, self._not_found)
        handler()

    def do_PUT(self):
        path = self.path.split("/")

        if self.path == "/shutdown":
            self.handle_shutdown()
        elif len(path) == 4 and path[1] == "simulation":
            sim_id = path[2]
            action = path[3]
            if action == "run":
                self.handle_run_simulator(sim_id)
            elif action == "configure":
                self.handle_external_data(sim_id)
            else:
                self._send_output({"error": "Simulation subcommand invalid."})
        else:
            self._not_found()

    def send_config_options(self):
        options = self.root.retriever.get_config_opts()
        self._send_output(options)

    def send_saved_configs(self):
        configs = self.root.configs
        self._send_output(configs)

    def list_endpoints(self):
        endpoints = {
            "GET /help": "Displays available endpoints",
            "GET /config/options": "Get configuration options",
            "GET /config/saved": "Get saved configurations",
            "PUT /simulation/{sim_id}/configure": "Submit user data for simulation configuration",
            "PUT /simulation/{sim_id}/run": "Run the simulation",
            "PUT /shutdown": "Shutdown the server",
        }
        self._send_output(endpoints)

    def handle_run_simulator(self, sim_id):
        self._send_output(f"Starting simulation id: {sim_id}")

    def handle_shutdown(self):
        message = f"Terminating gEMA server process, pid: {os.getpid()}"
        self._send_output(message)
        print(message)
        os._exit(0)

    def handle_external_data(self, sim_id):
        try:
            content_length = int(self.headers["Content-Length"])
            data = self.rfile.read(content_length)
            received_data = json.loads(data.decode("utf-8"))
            self.root.configurator.save_config(sim_id, received_data)
            response_message = (
                f"Configured gem5 object, sim_id: {sim_id}. Ready to Simulate!"
            )
            print(response_message)
            self._send_output(response_message)
        except Exception as e:
            self.send_error(500, f"Internal Server Error: {str(e)}")
