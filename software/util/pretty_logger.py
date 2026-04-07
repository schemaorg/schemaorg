#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import colorama
import logging
import os
import sys
import time
from typing import Any, Dict, Optional, List, Type


class PrettyLogFormatter(logging.Formatter):
    """Helper class to format the log messages from the various parts of the project."""

    COLORS: Dict[str, str] = {
        "WARNING": colorama.Fore.YELLOW,
        "INFO": colorama.Fore.CYAN,
        "DEBUG": colorama.Fore.BLUE,
        "CRITICAL": colorama.Fore.MAGENTA,
        "ERROR": colorama.Fore.RED,
    }

    def __init__(self, use_color: bool = True, shard: Optional[int] = None) -> None:
        fmt: str = "%(levelname)s %(name)s: %(message)s"
        if shard is not None:
            fmt = f"%(levelname)s ({shard}) %(name)s: %(message)s"
        super().__init__(fmt=fmt)
        self.use_color: bool = use_color

    @classmethod
    def _computeLevelName(cls, record: logging.LogRecord) -> str:
        msg: str = record.getMessage().casefold()
        if msg == "done" or msg.startswith("done:"):
            return f"{colorama.Fore.LIGHTGREEN_EX}{record.levelname}{colorama.Fore.RESET}"
        color: Optional[str] = cls.COLORS.get(record.levelname)
        if color:
            return f"{color}{record.levelname}{colorama.Fore.RESET}"
        return record.levelname

    @classmethod
    def _computeName(cls, record: logging.LogRecord) -> str:
        name: str = record.name.split(".")[-1]
        return f"{colorama.Style.DIM}{name}{colorama.Style.RESET_ALL}"

    def format(self, record: logging.LogRecord) -> str:
        if self.use_color:
            record.levelname = self._computeLevelName(record)
            record.name = self._computeName(record)
        return super().format(record)


class BlockLog:
    def __init__(self, logger: logging.Logger, message: str, timing: bool = False, displayStart: bool = True) -> None:
        self.logger: logging.Logger = logger
        self.message: str = message
        self.timing: bool = timing
        self.displayStart: bool = displayStart
        self.start_time: Optional[float] = None
        self.elapsed: Optional[float] = None

    def __enter__(self) -> "BlockLog":
        if self.displayStart:
            self.logger.info(f"Start: {self.message}")
        if self.timing:
            self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type: Optional[Type[BaseException]], exc_value: Optional[BaseException], traceback: Any) -> None:
        if self.timing and self.start_time is not None:
            self.elapsed = time.perf_counter() - self.start_time

        if exc_value:
            self.logger.error(f"Failed: {self.message}")
        else:
            if self.elapsed is not None:
                self.logger.info(
                    f"Done: {self.message} in {self.elapsed:.2f} seconds",
                )
            else:
                self.logger.info(f"Done: {self.message}")

    def append(self, message: str) -> None:
        self.message = f"{self.message} {message}"


def MakeRootLogPretty(shard: Optional[int] = None) -> None:
    """Makes the root log pretty if standard output is a terminal."""
    handler: logging.StreamHandler = logging.StreamHandler(sys.stdout)
    formatter: PrettyLogFormatter = PrettyLogFormatter(
        use_color=sys.stdout.isatty(), shard=shard
    )
    handler.setFormatter(formatter)

    root_log: logging.Logger = logging.getLogger()
    root_log.handlers = [handler]
