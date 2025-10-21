#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import colorama
import logging
import os
import sys
import time


class PrettyLogFormatter(logging.Formatter):
    """Helper class to format the log messages from the various parts of the project."""

    COLORS = {
        "WARNING": colorama.Fore.YELLOW,
        "INFO": colorama.Fore.CYAN,
        "DEBUG": colorama.Fore.BLUE,
        "CRITICAL": colorama.Fore.MAGENTA,
        "ERROR": colorama.Fore.RED,
    }

    def __init__(self, use_color=True, shard=None):
        fmt = "%(levelname)s %(name)s: %(message)s"
        if shard is not None:
            fmt = "%(levelname)s (" + str(shard) + ") %(name)s: %(message)s"
        logging.Formatter.__init__(self, fmt=fmt)
        self.use_color = use_color

    @classmethod
    def _computeLevelName(cls, record):
        lower_msg = record.getMessage().casefold()
        if lower_msg == "done" or lower_msg[:5] == "done:":
            return colorama.Fore.LIGHTGREEN_EX + record.levelname + colorama.Fore.RESET
        if record.levelname in cls.COLORS:
            return cls.COLORS[record.levelname] + record.levelname + colorama.Fore.RESET
        return record.levelname

    @classmethod
    def _computeName(cls, record):
        components = record.name.split(".")
        return colorama.Style.DIM + components[-1] + colorama.Style.RESET_ALL

    def format(self, record):
        if self.use_color:
            record.levelname = self._computeLevelName(record)
            record.name = self._computeName(record)
        return logging.Formatter.format(self, record)


class BlockLog:
    def __init__(self, logger, message, timing=False, displayStart=True):
        self.logger = logger
        self.message = message
        self.timing = timing
        self.displayStart = displayStart
        self.start_time = None
        self.elapsed = None

    def __enter__(self):
        if self.displayStart:
            self.logger.info(f"Start: {self.message}")
        if self.timing:
            self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.timing:
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

    def append(self, message):
        self.message = self.message + " " + message


def MakeRootLogPretty(shard=None):
    """Makes the root log pretty if stdandard output is a terminal."""
    handler = logging.StreamHandler(sys.stdout)
    formatter = PrettyLogFormatter(
        use_color=os.isatty(sys.stdout.fileno()), shard=shard
    )
    handler.setFormatter(formatter)

    root_log = logging.getLogger()
    root_log.handlers = [handler]
