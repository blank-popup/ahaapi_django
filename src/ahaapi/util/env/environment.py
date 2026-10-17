import logging
import os
import re
from pathlib import Path

from dotenv import dotenv_values

# Base root: ahaapi/
BASE_DIR = Path(__file__).resolve().parents[4]

# Directory containing environment files
ENV_DIR = BASE_DIR / "env"


def load_environment(environment: str) -> None:
    """Load common and environment-specific environment files."""

    if not re.fullmatch(r"[a-z][a-z0-9_]*", environment):
        raise ValueError(
            f"Invalid environment name: {environment!r}"
        )

    common_file = ENV_DIR / ".env"
    specific_file = ENV_DIR / f".env.{environment}"

    if not specific_file.is_file():
        raise FileNotFoundError(
            f"Environment file not found: {specific_file}"
        )

    values = {}

    for env_file in (common_file, specific_file):
        if env_file.is_file():
            values.update(
                {
                    key: value
                    for key, value in dotenv_values(env_file).items()
                    if value is not None
                }
            )

    # Preserve OS environment variables.
    for key, value in values.items():
        os.environ.setdefault(key, value)


def env_bool(name: str, default: bool = False) -> bool:
    """Read a boolean environment variable."""
    value = os.getenv(name)

    if value is None:
        return default

    return value.strip().lower() in {"1", "true", "yes", "on"}


def env_int(name: str, default: int) -> int:
    """Read an integer environment variable."""
    value = os.getenv(name)

    if value is None or not value.strip():
        return default
    if not isinstance(value, int):
        return default

    return int(value)


def env_level(name: str, default: str) -> int:
    """Convert a logging level name to its numeric value."""
    value = os.getenv(name, default).upper()
    level = logging.getLevelNamesMapping().get(value)

    if not isinstance(level, int):
        raise TypeError(f"Invalid logging level: {value}")

    return level
