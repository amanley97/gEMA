# gEMA/example/host.py
# Example host to run gEMA instance.

import argparse
from gem5.utils.multiprocessing import Process
from gem5.gEMA import gEMAServer
parser = argparse.ArgumentParser("gEMA host")
parser.add_argument("port", help="Port to use for API", type=int)
args = parser.parse_args()

if __name__ == '__m5_main__':
    server = gEMAServer()
    main = Process(target=server.run_server)
    main.start()
    main.join()