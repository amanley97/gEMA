# gEMA/server.py
# Runs the gEMA backend and awaits external commands.

from http.server import HTTPServer as gEMAHTTP
from .handler import gEMAHandler


class gEMAServer:
    def __init__(self, port=5000):
        self.port = port
        self.config = None
        self.handler = gEMAHandler

    def run_server(self):
        server_address = ("", self.port)
        httpd = gEMAHTTP(server_address, self.handler)

        print(
            f"""
        Starting server on port {self.port}.
        For help, access /help on the server URL or consult the documentation.
        """
        )
        httpd.serve_forever()
