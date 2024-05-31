# gEMA/handler.py
import json
import multiprocessing
from http.server import BaseHTTPRequestHandler
from .obtain import get_mem_types, get_cpu_types, get_board_types

class BackendHandler(BaseHTTPRequestHandler):
    user_data_storage = {}

    def do_GET(self):
        if self.path == '/get-mem-types':
            self.handle_mem_types()
        elif self.path == '/get-cpu-types':
            self.handle_cpu_types()
        elif self.path == '/get-board-types':
            self.handle_board_types()
        else:
            self.send_error(404, 'Not Found')

    def do_PUT(self):
        if self.path == '/run-simulation':
            self.handle_run_simulator()
        elif self.path == '/shutdown':
            self.handle_shutdown()
        elif self.path == '/user-data':
            self.handle_user_data()
        else:
            self.send_error(404, 'Not Found')

    def handle_mem_types(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(get_mem_types())

    def handle_cpu_types(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(get_cpu_types())

    def handle_board_types(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(get_board_types())

    def handle_run_simulator(self):
        process = multiprocessing.Process(target=self.server_instance.run_gem5_simulator)
        process.start()
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b"Simulator started in a separate thread\n")
        process.join()

        self.wfile.write(b"Simulation Complete\n")

    def handle_shutdown(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b"Shutting down server\n")

    def get_user_data(cls, user_id):
        return cls.user_data_storage.get(user_id)

    def handle_user_data(self):
        try:
            content_length = int(self.headers['Content-Length'])
            data = self.rfile.read(content_length)
            received_data = json.loads(data.decode('utf-8'))

            user_id = 'default'
            BackendHandler.user_data_storage[user_id] = received_data
            self.send_response(200)

        except Exception as e:
            print(f"Error processing PUT request: {e}")
            self.send_response(500, {"error": "Internal Server Error"})

        self.end_headers()
        self.wfile.write(b"Successfully configured gem5. Ready to Simulate!")
