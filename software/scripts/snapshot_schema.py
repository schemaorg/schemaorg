#!/usr/bin/env python3
"""Export a standalone HTTPS Turtle snapshot of the full vocabulary."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
import logging
from pathlib import Path

from schemaorg import constants
import SchemaTerms.sdotermsource as sdotermsource
import scripts.buildfiles as buildfiles
import util.fileutils as fileutils
import util.schema as schema

log: logging.Logger = logging.getLogger(__name__)


def snapshot_ttl(output_dir: str | Path | None = None) -> None:
    target_dir = Path(
        output_dir or constants.PROJECT_ROOT / "software/tests/snapshot"
    )
    target_dir.mkdir(parents=True, exist_ok=True)

    # Take some copies of globals we need to manipulate.
    # TODO: these globals should be arguments or similar
    outputdir_copy = schema.config.OUTPUTDIR
    selectors_copy = fileutils.FILESET_SELECTORS
    protocols_copy = fileutils.FILESET_PROTOCOLS
    try:
        schema.config.OUTPUTDIR = ""
        fileutils.FILESET_SELECTORS = frozenset(("all",))
        fileutils.FILESET_PROTOCOLS = frozenset(("https",))

        log.info("Building snapshot file...")
        sdotermsource.SdoTermSource.loadSourceGraph("default")
        buildfiles.exportrdf("RDFExport.turtle", subdirectory_path=str(target_dir))
        log.info("Snapshot file created in %s", target_dir)
    finally:
        # Put back the original values.
        schema.config.OUTPUTDIR = outputdir_copy
        fileutils.FILESET_SELECTORS = selectors_copy
        fileutils.FILESET_PROTOCOLS = protocols_copy


def main(argv: Sequence[str] | None = None) -> None:
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-o",
        "--output",
        help="Output directory for snapshot Turtle file",
    )
    args = parser.parse_args(argv)
    snapshot_ttl(output_dir=args.output)


if __name__ == "__main__":
    main()
