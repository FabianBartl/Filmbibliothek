
import logging, os
from datetime import datetime

def init(name, *, name_is_path:bool=True):
    # extract filename from path
    if name_is_path:
        name = os.path.basename(name)

    # logging parameter
    level = 10
    timestamp = datetime.today().strftime("%Y-%m-%d_%H-%M-%S")
    path = os.path.abspath(os.path.join("logs", f"{name}_{timestamp}.log"))
    encoding = "utf-8"
    format = "%(asctime)s | %(levelname)8s | %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"

    # file hanlder for logging
    file_handler = logging.FileHandler(path, encoding=encoding)
    file_handler.setLevel(level)
    file_handler.setFormatter(logging.Formatter(fmt=format, datefmt=datefmt))

    # logging config
    logging.basicConfig(level=level, encoding=encoding, format=format, datefmt=datefmt, handlers=[file_handler])

    return logging.getLogger(name)
