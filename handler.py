import json, os, multiprocessing
from http.server import BaseHTTPRequestHandler
from .obtain import get_config_opts
from .configure import generate_config


class BackendHandler(BaseHTTPRequestHandler):
    saved_configs = {}

    def _set_headers(self, status=200, content_type="application/json"):
        """Helper method to set HTTP response headers."""
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.end_headers()

    def do_GET(self):
        """Handle GET requests."""
        endpoints = {
                    "/config": self.send_config_options, 
                    "/help": self.list_endpoints
                    }
        handler = endpoints.get(self.path, self.send_not_found)
        handler()

    def do_PUT(self):
        """Handle PUT requests."""
        path = self.path.split('/')
        
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
            self.send_not_found()

    def send_config_options(self):
        """Send configuration options to the client."""
        self._set_headers()
        self.wfile.write(get_config_opts())

    def list_endpoints(self):
        """List available HTTP endpoints."""
        self._set_headers()
        endpoints = {
            "GET /help": "Displays available endpoints",
            "GET /config": "Get configuration options",
            "PUT /simulation/{sim_id}/configure": "Submit user data for simulation configuration",
            "PUT /simulation/{sim_id}/run": "Run the gem5 simulation",
            "PUT /shutdown": "Shutdown the server",
        }
        self.wfile.write(json.dumps(endpoints, indent=4).encode())

    def send_not_found(self):
        """Send a 404 Not Found response."""
        self.send_error(404, "Not Found")

    def handle_run_simulator(self, id):
        """Handle request to run a simulation in a separate process."""
        self._set_headers()
        process = multiprocessing.Process(
            target=self.server_instance.run_gem5_simulator(id)
        )
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
            obj = generate_config(received_data)
            print(f"sim_id: {id} generated.")
            msg = f"Configured gem5 object, sim_id: {id}. Ready to Simulate!".encode()
            self.saved_configs[id] = obj
            self._set_headers()
            self.wfile.write(msg)
        except Exception as e:
            self.send_error(500, f"Internal Server Error: {str(e)}")
