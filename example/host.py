# gEMA/example/host.py
# Example host to run gEMA instance.

import argparse

parser = argparse.ArgumentParser("gEMA host")
parser.add_argument("port", help="Port to use for API", type=int)
args = parser.parse_args()

if __name__ == '__m5_main__':
    try:
        from gem5.gEMA import BackendServer
        s = BackendServer(port=args.port)
        s.run_server()
    except ImportError:
        print("Failed to import gEMA")