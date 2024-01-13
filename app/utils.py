"""
This module contains utility functions for a Flask application, including token validation,
environment configuration loading, and logging setup. Functions include validating Turnstile
tokens using Cloudflare's API, loading configuration variables from a .env file, and
configuring the application's logging system according to environment variables.
"""

import logging
import os
import sys
import requests

from dotenv import load_dotenv


def validate_turnstile_token(token, secret_key):
    """Validate Turnstile token using Cloudflare's siteverify API."""
    url = 'https://challenges.cloudflare.com/turnstile/v0/siteverify'

    payload = {
        'secret': secret_key,
        'response': token
    }
    response = requests.post(url, data=payload, timeout=5)
    return response.json()


def load_env_configuration():
    """Load config values from dotenv file."""
    load_dotenv()
    required_keys = [
        "LANGCHAIN_DEBUG",
        "OPENAI_API_KEY",
        "THREADS",
        "ENVIRONMENT",
        "TURNSTILE_SECRET"
    ]

    config = {}
    for key in required_keys:
        value = os.getenv(key)
        if not value:
            raise ValueError(f"Key '{key}' missing or invalid.")
        config[key] = value

    return config


def configure_logging():
    """
    Configures the logging system for the application.

    This function sets up logging based on the LOG_LEVEL environment variable.
    It supports different logging levels (e.g., DEBUG, INFO, WARNING, etc.)
    and directs logs to appropriate output streams (stdout for INFO and below,
    stderr for WARNING and above).

    It also specifically configures logging for the 'flask-limiter' component,
    ensuring that its logs are handled in the same way as the application's logs.

    Raises:
        ValueError: If the LOG_LEVEL environment variable contains an invalid logging level.
    """
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
