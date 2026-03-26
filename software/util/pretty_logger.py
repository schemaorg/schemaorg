#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import colorama
import logging
import os
import sys
import time
import typing
from typing import Any, Dict, List, Optional, Tuple, Union, Iterable, Sequence, Set, Callable, Type


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
            fmt = "%(levelname)s (" + str(shard) + ") %(name)s: %(message)s"
        logging.Formatter.__init__(self, fmt=fmt)
        self.use_color: bool = use_color

    @classmethod
    def _computeLevelName(cls, record: logging.LogRecord) -> str:
        lower_msg: str = record.getMessage().casefold()
        if lower_msg == "done" or lower_msg[:5] == "done:":
            return colorama.Fore.LIGHTGREEN_EX + record.levelname + colorama.Fore.RESET
        if record.levelname in cls.COLORS:
            return cls.COLORS[record.levelname] + record.levelname + colorama.Fore.RESET
        return record.levelname

    @classmethod
    def _computeName(cls, record: logging.LogRecord) -> str:
        components: List[str] = record.name.split(".")
        return colorama.Style.DIM + components[-1] + colorama.Style.RESET_ALL

    def format(self, record: logging.LogRecord) -> str:
        if self.use_color:
            record.levelname = self._computeLevelName(record)
            record.name = self._computeName(record)
        return str(logging.Formatter.format(self, record))


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

        if isinstance(exc_value, Exception):
            self.logger.error(f"Failed: {self.message}")
        else:
            if self.elapsed:
                self.logger.info(
                    f"Done: {self.message} in {self.elapsed:.2f} seconds",
                )
            else:
                self.logger.info(f"Done: {self.message}")

    def append(self, message: str) -> None:
        self.message = self.message + " " + message


def MakeRootLogPretty(shard: Optional[int] = None) -> None:
    """Makes the root log pretty if stdandard output is a terminal."""
    handler: logging.StreamHandler = logging.StreamHandler(sys.stdout)
    formatter: PrettyLogFormatter = PrettyLogFormatter(
        use_color=os.isatty(sys.stdout.fileno()), shard=shard
    )
    handler.setFormatter(formatter)

    root_log: logging.Logger = logging.getLogger()
    root_log.handlers = [handler]
