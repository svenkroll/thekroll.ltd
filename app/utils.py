import logging
import os
import sys

from dotenv import load_dotenv


def load_env_configuration():
    load_dotenv()
    required_keys = ["LANGCHAIN_DEBUG", "OPENAI_API_KEY", "THREADS", "ENVIRONMENT"]

    config = {}
    for key in required_keys:
        value = os.getenv(key)
        if not value:
            raise ValueError(f"Key '{key}' missing or invalid.")
        config[key] = value

    return config


def configure_logging():
    # Get log level from environment variable
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    numeric_level = getattr(logging, log_level, None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {log_level}')

    # Configure logging
    logging.basicConfig(level=numeric_level)

    # StreamHandler for stdout
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.INFO)
    stdout_handler.addFilter(lambda record: record.levelno <= logging.INFO)

    # StreamHandler for stderr
    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(logging.WARNING)

    # Add handlers to the root logger
    logging.getLogger().addHandler(stdout_handler)
    logging.getLogger().addHandler(stderr_handler)

    logging.getLogger("flask-limiter").addHandler(stdout_handler)
    logging.getLogger("flask-limiter").addHandler(stderr_handler)