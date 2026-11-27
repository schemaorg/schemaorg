#!/usr/bin/env python3
"""CLI runner for the schema.org unit test suite."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
import logging
from pathlib import Path
import sys

from schemaorg import constants
from schemaorg.progress import LogProgressReporter
from schemaorg.tasks.run_unit_tests import RunUnitTestsTask

log: logging.Logger = logging.getLogger(__name__)


def _configure_runner_logger() -> None:
    if not log.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(levelname)s %(name)s: %(message)s"))
        log.addHandler(handler)
    log.setLevel(logging.INFO)
    log.propagate = False


def main(
    test_path: str | None = None,
    args: argparse.Namespace | None = None,
    argv: Sequence[str] | None = None,
) -> int:
    _configure_runner_logger()

    if test_path is None:
        test_path = str(constants.PROJECT_ROOT / "software/tests")
    if args is None:
        parser = argparse.ArgumentParser(
            description="Configurable testing of schema.org."
        )
        parser.add_argument(
            "--skipbasics", action="store_true", help="Skip basic tests."
        )
        args = parser.parse_args(argv)

    summary = RunUnitTestsTask(
        tests_dir=Path(test_path),
        skip_basics=bool(args.skipbasics),
        progress=LogProgressReporter(logger=log, log_steps=False),
    ).run()
    return 0 if summary.ok else 1


if __name__ == "__main__":
    sys.exit(main())
