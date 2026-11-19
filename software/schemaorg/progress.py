"""Progress reporting protocol and logger-backed implementations."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import AbstractContextManager, contextmanager
import logging
from typing import Protocol

import util.pretty_logger as pretty_logger


class TaskProgress(Protocol):
    """Active handle for one running task."""

    def step(self, label: str) -> None:
        """Update the current sub-step or item label."""
        ...

    def advance(self, n: int) -> None:
        """Increment completed work units by n."""
        ...

    def log(self, message: str, level: int) -> None:
        """Emit a diagnostic log line safely alongside active progress."""
        ...


class ProgressReporter(Protocol):
    """Factory for scoped task progress handles."""

    def task(
        self,
        description: str,
        total: int | None,
        unit: str,
    ) -> AbstractContextManager[TaskProgress]: ...


class _NullTaskProgress:
    def step(self, label: str) -> None:
        pass

    def advance(self, n: int) -> None:
        pass

    def log(self, message: str, level: int) -> None:
        pass


class NullProgressReporter:
    """Silent no-op reporter for unit tests and non-interactive callers."""

    @contextmanager
    def task(
        self,
        description: str,
        total: int | None,
        unit: str,
    ) -> Iterator[TaskProgress]:
        yield _NullTaskProgress()


class _LogTaskProgress:
    def __init__(
        self,
        logger: logging.Logger,
        description: str,
        log_steps: bool,
    ) -> None:
        self.logger = logger
        self.description = description
        self.log_steps = log_steps
        self.completed: int = 0
        self.current_step: str = ""

    def step(self, label: str) -> None:
        self.current_step = label
        if self.log_steps:
            self.logger.info("%s: %s", self.description, label)

    def advance(self, n: int) -> None:
        self.completed += n

    def log(self, message: str, level: int) -> None:
        self.logger.log(level, "%s", message)


class LogProgressReporter:
    """Logger-backed reporter using pretty_logger.BlockLog."""

    def __init__(self, logger: logging.Logger, log_steps: bool) -> None:
        self.logger: logging.Logger = logger
        self.log_steps: bool = log_steps

    @contextmanager
    def task(
        self,
        description: str,
        total: int | None,
        unit: str,
    ) -> Iterator[TaskProgress]:
        handle = _LogTaskProgress(self.logger, description, self.log_steps)
        with pretty_logger.BlockLog(
            logger=self.logger,
            message=description,
            timing=True,
        ) as block:
            yield handle
            if total is not None:
                block.append(f"({handle.completed}/{total} {unit})")
            elif handle.completed:
                block.append(f"({handle.completed} {unit})")
