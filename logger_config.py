from __future__ import annotations

import logging
from enum import StrEnum
from typing import Any


class LogLevel(StrEnum):
    """String Enum for log levels to ensure type safety."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

    @classmethod
    def get_logging_level(cls, level: str) -> int:
        try:
            return getattr(logging, level.upper())
        except AttributeError as exc:
            raise ValueError(f"Invalid log level string: {level}") from exc

    @classmethod
    def from_logging_level(cls, level: int) -> LogLevel:
        for member in cls:
            if getattr(logging, member.value) == level:
                return member
        raise ValueError(f"No LogLevel member corresponds to logging level {level}")


class CustomFormatter(logging.Formatter):
    """Custom formatter with colored output for console."""

    COLORS: dict[LogLevel, str] = {
        LogLevel.DEBUG: "\x1b[38;20m",
        LogLevel.INFO: "\x1b[32;1m",
        LogLevel.WARNING: "\x1b[33;20m",
        LogLevel.ERROR: "\x1b[31;20m",
        LogLevel.CRITICAL: "\x1b[31;1m",
    }

    RESET = "\x1b[0m"
    BASE_FORMAT = "%(asctime)s - %(name)s - [%(levelname)8s] - %(message)s"

    def format(self, record: logging.LogRecord) -> str:
        level_enum = LogLevel.from_logging_level(record.levelno)
        color = self.COLORS.get(level_enum, self.RESET)

        log_fmt = f"{color}{self.BASE_FORMAT}{self.RESET}"
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


class LoggerSingleton:
    _instance: LoggerSingleton | None = None

    def __new__(cls, config: dict[str, Any] | None = None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize_logger(config)
        return cls._instance

    def _initialize_logger(self, config: dict[str, Any] | None = None):
        self.logger = logging.getLogger("kafka_consumer")

        default_config: dict[str, Any] = {
            "level": LogLevel.INFO,
            "handlers": ["console"],
            "console_level": LogLevel.INFO,
            "file_enabled": False,
            "file_path": "logs/app.log",
            "file_level": LogLevel.INFO,
        }

        if config:
            default_config.update(config)

        self.logger.handlers.clear()

        self.logger.setLevel(
            LogLevel.get_logging_level(default_config["level"])
        )

        if "console" in default_config["handlers"]:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(
                LogLevel.get_logging_level(default_config["console_level"])
            )
            console_handler.setFormatter(CustomFormatter())
            self.logger.addHandler(console_handler)

        if default_config["file_enabled"] and "file" in default_config["handlers"]:
            file_handler = logging.FileHandler(default_config["file_path"])
            file_handler.setLevel(
                LogLevel.get_logging_level(default_config["file_level"])
            )
            file_handler.setFormatter(
                logging.Formatter(CustomFormatter.BASE_FORMAT)
            )
            self.logger.addHandler(file_handler)

    @classmethod
    def get_logger(
        cls,
        console_only: bool = True,
        level: LogLevel = LogLevel.INFO,
    ) -> logging.Logger:
        config: dict[str, Any] = {
            "level": level,
            "handlers": ["console"] if console_only else ["console", "file"],
            "console_level": level,
            "file_enabled": not console_only,
            "file_level": level,
        }
        return LoggerSingleton(config).logger
