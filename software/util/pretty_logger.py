#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import colorama
import logging
import os
import sys


class PrettyLogFormatter(logging.Formatter):
    """Helper class to format the log messages from the various parts of the project."""

    COLORS = {
        'WARNING': colorama.Fore.YELLOW,
        'INFO': colorama.Fore.CYAN,
        'DEBUG': colorama.Fore.BLUE,
        'CRITICAL': colorama.Fore.MAGENTA,
        'ERROR': colorama.Fore.RED,
    }

    def __init__(self, use_color=True):
        logging.Formatter.__init__(self, fmt='%(levelname)s %(name)s: %(message)s')
        self.use_color = use_color

    @classmethod
    def _computeLevelName(cls, record):
        lower_msg = record.getMessage().casefold()
        if lower_msg == 'done' or lower_msg[:5] == 'done:':
            return colorama.Fore.LIGHTGREEN_EX + record.levelname + colorama.Fore.RESET
        if record.levelname in cls.COLORS:
            return cls.COLORS[record.levelname] + record.levelname + colorama.Fore.RESET
        return record.levelname

    @classmethod
    def _computeName(cls, record):
        components = record.name.split('.')
        return colorama.Style.DIM + components[-1] + colorama.Style.RESET_ALL

    def format(self, record):
        if self.use_color:
            record.levelname = self.__class__._computeLevelName(record)
            record.name = self.__class__._computeName(record)
        return logging.Formatter.format(self, record)


class BlockLog:
    def __init__(self, logger, message):
        self.logger = logger
        self.message = message

    def __enter__(self):
        self.logger.info('Start: %s', self.message)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if isinstance(exc_value, Exception):
          self.logger.error('Failed: %s', self.message)
        else:
          self.logger.info('Done: %s', self.message)

    def append(self, message):
        self.message = self.message + ' ' + message


def MakeRootLogPretty():
    """Makes the root log pretty if stdandard output is a terminal."""
    handler = logging.StreamHandler(sys.stdout)
    formatter = PrettyLogFormatter(use_color=os.isatty(sys.stdout.fileno()))
    handler.setFormatter(formatter)

    root_log = logging.getLogger()
    root_log.handlers = [handler]