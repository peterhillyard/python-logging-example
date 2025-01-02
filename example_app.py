import atexit
from logging_config import LOGGING_CONFIG
import logging
import logging.config
import logging.handlers
from logging_config import IS_PYTHON_3_12

logger = logging.getLogger("example_app")

def setup_logging() -> None:
    logging.config.dictConfig(LOGGING_CONFIG)

    if not IS_PYTHON_3_12:
        return

    queue_handler = logging.getHandlerByName("queue_handler")
    if queue_handler is not None:
        queue_handler.listener.start()
        atexit.register(queue_handler.listener.stop)


def main() -> None:
    for i in range(10):
        logger.debug(f"index {i}")
        logger.info(f"index {i}")
        logger.warning(f"index {i}")
        logger.error(f"index {i}")
        logger.critical(f"index {i}")
    
    try:
        1 / 0
    except ZeroDivisionError:
        logger.exception("exception message")

if __name__ == "__main__":
    setup_logging()
    main()