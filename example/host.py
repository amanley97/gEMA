# gEMA/example/host.py
# Example host to run gEMA instance.

# import argparse
from gem5.gEMA.configure import gEMAConfigurator
from gem5.utils.multiprocessing import Process
from gem5.gEMA import gEMAServer
# parser = argparse.ArgumentParser("gEMA host")
# parser.add_argument("port", help="Port to use for API", type=int)
# args = parser.parse_args()

if __name__ == '__m5_main__':
    # try:
    #     from gem5.gEMA import gEMAServer
    #     s = gEMAServer(port=args.port)
    #     s.run()
    # except ImportError:
    #     print("Failed to import gEMA")
    # cfg = gEMAConfigurator()
    server = gEMAServer()
    main = Process(target=server.run_server)
    # sub = Process(target=cfg.run_gem5_simulator, args=(1,))
    main.start()
    # sub.start()
    main.join()
    # sub.join()