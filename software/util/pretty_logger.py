from __future__ import annotations

import logging
import sys
import time
from types import TracebackType

import colorama


class PrettyLogFormatter(logging.Formatter):
    """Helper class to format the log messages from the various parts of the project."""

    COLORS: dict[str, str] = {
        "WARNING": colorama.Fore.YELLOW,
        "INFO": colorama.Fore.CYAN,
        "DEBUG": colorama.Fore.BLUE,
        "CRITICAL": colorama.Fore.MAGENTA,
        "ERROR": colorama.Fore.RED,
    }

    def __init__(self, use_color: bool = True, shard: int | None = None) -> None:
        fmt = "%(levelname)s %(name)s: %(message)s"
        if shard is not None:
            fmt = f"%(levelname)s ({shard}) %(name)s: %(message)s"
        super().__init__(fmt=fmt)
        self.use_color: bool = use_color

    @classmethod
    def _computeLevelName(cls, record: logging.LogRecord) -> str:
        msg = record.getMessage().casefold()
        if msg == "done" or msg.startswith("done:"):
            return f"{colorama.Fore.LIGHTGREEN_EX}{record.levelname}{colorama.Fore.RESET}"
        if color := cls.COLORS.get(record.levelname):
            return f"{color}{record.levelname}{colorama.Fore.RESET}"
        return record.levelname

    @classmethod
    def _computeName(cls, record: logging.LogRecord) -> str:
        name = record.name.rsplit(".", 1)[-1]
        return f"{colorama.Style.DIM}{name}{colorama.Style.RESET_ALL}"

    def format(self, record: logging.LogRecord) -> str:
        if not self.use_color:
            return super().format(record)
        orig_levelname = record.levelname
        orig_name = record.name
        try:
            record.levelname = self._computeLevelName(record)
            record.name = self._computeName(record)
            return super().format(record)
        finally:
            record.levelname = orig_levelname
            record.name = orig_name


class BlockLog:
    def __init__(
        self,
        logger: logging.Logger,
        message: str,
        timing: bool = False,
        displayStart: bool = True,
    ) -> None:
        self.logger: logging.Logger = logger
        self.message: str = message
        self.timing: bool = timing
        self.displayStart: bool = displayStart
        self.start_time: float | None = None
        self.elapsed: float | None = None

    def __enter__(self) -> BlockLog:
        if self.displayStart:
            self.logger.info("Start: %s", self.message)
        if self.timing:
            self.start_time = time.perf_counter()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if self.timing and self.start_time is not None:
            self.elapsed = time.perf_counter() - self.start_time

        if exc_value is not None:
            self.logger.error("Failed: %s", self.message)
        elif self.elapsed is not None:
            self.logger.info("Done: %s in %.2f seconds", self.message, self.elapsed)
        else:
            self.logger.info("Done: %s", self.message)

    def append(self, message: str) -> None:
        self.message = f"{self.message} {message}"


def MakeRootLogPretty(shard: int | None = None) -> None:
    """Makes the root log pretty if standard output is a terminal."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        PrettyLogFormatter(use_color=sys.stdout.isatty(), shard=shard)
    )
    logging.getLogger().handlers = [handler]
