import datetime as dt
import json
import logging
import logging.handlers
from atexit import register
from logging.config import ConvertingList
from multiprocessing import Queue
from typing import Any, Dict, List, Union

# https://github.com/mCodingLLC/VideosSampleCode/tree/master/videos/135_modern_logging
LOG_RECORD_BUILTIN_ATTRS = {
    "args",
    "asctime",
    "created",
    "exc_info",
    "exc_text",
    "filename",
    "funcName",
    "levelname",
    "levelno",
    "lineno",
    "module",
    "msecs",
    "message",
    "msg",
    "name",
    "pathname",
    "process",
    "processName",
    "relativeCreated",
    "stack_info",
    "thread",
    "threadName",
    "taskName",
}


class JSONFormatter(logging.Formatter):
    def __init__(
        self,
        *,
        fmt_keys: Union[Dict[str, str], None] = None,
    ):
        super().__init__()
        self.fmt_keys = fmt_keys if fmt_keys is not None else {}

    # @override
    def format(self, record: logging.LogRecord) -> str:
        message = self._prepare_log_dict(record)
        return json.dumps(message, default=str)

    def _prepare_log_dict(self, record: logging.LogRecord) -> Dict[str, Union[str, Any]]:
        always_fields = {
            "message": record.getMessage(),
            "timestamp": dt.datetime.fromtimestamp(record.created, tz=dt.timezone.utc).isoformat(),
        }
        if record.exc_info is not None:
            always_fields["exc_info"] = self.formatException(record.exc_info)

        if record.stack_info is not None:
            always_fields["stack_info"] = self.formatStack(record.stack_info)

        message = {
            key: msg_val if (msg_val := always_fields.pop(val, None)) is not None else getattr(record, val)
            for key, val in self.fmt_keys.items()
        }
        message.update(always_fields)

        for key, val in record.__dict__.items():
            if key not in LOG_RECORD_BUILTIN_ATTRS:
                message[key] = val

        return message


# https://rob-blackbourn.medium.com/how-to-use-python-logging-queuehandler-with-dictconfig-1e8b1284e27a
class QueueListenerHandler(logging.handlers.QueueHandler):
    def __init__(
        self,
        handlers: ConvertingList,
        respect_handler_level: bool = True,
        auto_run: bool = False,
        queue: Queue = Queue(maxsize=-1),
    ) -> None:
        super().__init__(queue)
        resolved_handlers = self._resolve_handlers(handlers)
        self._listener = logging.handlers.QueueListener(
            self.queue, *resolved_handlers, respect_handler_level=respect_handler_level
        )

        if auto_run:
            self.start()
            register(self.stop)

    def start(self) -> None:
        self._listener.start()

    def stop(self) -> None:
        self._listener.stop()

    def emit(self, record: logging.LogRecord) -> None:
        return super().emit(record)

    def _resolve_handlers(self, handlers: ConvertingList) -> List[logging.Handler]:
        if not isinstance(handlers, ConvertingList):
            return handlers

        # Indexing the list performs the evaluation.
        return [handlers[i] for i in range(len(handlers))]
