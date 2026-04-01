import logging
import logging.handlers
import json
from pathlib import Path
from datetime import datetime

LOG_DIR = Path(__file__).parent.parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

class CustomJSONFormatter(logging.Formatter):


    def format(self, record):
        log_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_record)
    
def setup_logger(name: str) -> logging.Logger:


    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(console_formatter)

    file_handler = logging.handlers.RotatingFileHandler(
        LOG_DIR / f"{name}.log",
        maxBytes=5 * 1024 * 1024,
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(CustomJSONFormatter())

    error_handler = logging.handlers.RotatingFileHandler(
        LOG_DIR / f"{name}_error.log",
        maxBytes=5 * 1024 * 1024,
        backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(CustomJSONFormatter())

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.addHandler(error_handler)

    return logger


logger = setup_logger("app_logger")