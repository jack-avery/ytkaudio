import logging
import time
from platformdirs import user_log_dir


def setup() -> None:
    """
    Sets up only a file handler for logging into `user_log_dir`.
    """
    log_handlers = []
    formatter = logging.Formatter(
        "%(asctime)s | %(module)s [%(levelname)s] %(message)s",
    )
    log_folder = user_log_dir("ytkaudio", "jack-avery", ensure_exists=True)
    log_file = (
        f"{log_folder}/" + f"{time.asctime().replace(':','-').replace(' ','_')}.log"
    )
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    log_handlers.append(file_handler)
    logging.basicConfig(handlers=log_handlers, level=logging.DEBUG)
    return log_file
