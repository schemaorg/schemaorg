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
import util.pretty_logger as pretty_logger

log: logging.Logger = logging.getLogger(__name__)


def main(
    test_path: str | None = None,
    args: argparse.Namespace | None = None,
    argv: Sequence[str] | None = None,
) -> int:
    logging.basicConfig(level=logging.INFO)
    pretty_logger.MakeRootLogPretty()

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
    return (
        summary.failure_count
        + summary.error_count
        + summary.unexpected_success_count
    )


if __name__ == "__main__":
    sys.exit(main())
