from lib.server import serve
from lib.landing import launch_app
from concurrent.futures import ThreadPoolExecutor
from logging.handlers import RotatingFileHandler
import logging
import signal
import time
import os

if __name__ == "__main__":
    logging.basicConfig(
        handlers=[
            RotatingFileHandler("./unlovable.log", maxBytes=100_000_000, backupCount=3),
            logging.StreamHandler(),
        ],
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s]: %(message)s",
    )

    shutdown_requested = [False]

    def interrupt_handler(sig, handler):
        print()
        logging.info("Exiting unlovable...")
        shutdown_requested[0] = True
        os._exit(0)

    signal.signal(signal.SIGINT, interrupt_handler)

    with ThreadPoolExecutor(max_workers=20) as executor:
        server_future = executor.submit(serve, executor)
        executor.submit(launch_app)

        try:
            while not shutdown_requested[0]:
                time.sleep(0.1)
        except KeyboardInterrupt:
            logging.info("Exiting unlovable...")
            os._exit(0)
