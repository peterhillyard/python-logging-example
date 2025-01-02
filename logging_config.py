import pathlib


APP_NAME = "example_app"
LOGGING_DIR = pathlib.Path("/tmp") # or some other location


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": "[%(levelname)s|%(module)s|L%(lineno)d] %(asctime)s: %(message)s",
            "datefmt": "%Y-%m-%dT%H:%M:%S%z",
        },
        "json": {
            "()": "logger_utils.JSONFormatter", # points to module with this class
            "fmt_keys": {
                "level": "levelname",
                "message": "message",
                "timestamp": "timestamp",
                "logger": "name",
                "module": "module",
                "function": "funcName",
                "line": "lineno",
                "thread_name": "threadName",
            },
        },
    },
    "handlers": {
        # https://stackoverflow.com/questions/75241185/why-does-python-logging-throw-an-error-when-a-handler-name-starts-with-s
        # These must be in alphabetical order!
        "h_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
            "formatter": "json",
            "filename": str(LOGGING_DIR / f"{APP_NAME}.log.jsonl"),
            "maxBytes": 10_000_000,
            "backupCount": 1,
        },
        "h_stderr": {
            "class": "logging.StreamHandler",
            "level": "WARNING",
            "formatter": "simple",
            "stream": "ext://sys.stderr",
        },
        "h_stdout": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "simple",
            "stream": "ext://sys.stdout",
        },
        # # Use this queue handler below if using Python 3.12
        # "queue_handler": {
        #     "class": "logging.handlers.QueueHandler", 
        #     "handlers": [
        #         "h_file",
        #         "h_stderr",
        #         "h_stdout",
        #     ],
        #     "respect_handler_level": True,
        # },
        # Use this queue handler below if using Python <3.12
        "queue_handler": {
            "class": "logger_utils.QueueListenerHandler", 
            "handlers": [
                "h_file",
                "h_stderr",
                "h_stdout",
            ],
            "respect_handler_level": True,
        },
    },
    "loggers": {"root": {"level": "DEBUG", "handlers": ["queue_handler"]}},
}