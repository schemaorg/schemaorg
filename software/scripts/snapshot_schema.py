#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
import shutil
import sys
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, Set, Tuple, Union
import typing

import SchemaTerms.sdotermsource as sdotermsource
import scripts.buildfiles as buildfiles
import util.fileutils as fileutils
import util.pretty_logger as pretty_logger
import util.schema as schema

from schemaorg import constants
PROJECT_ROOT = constants.PROJECT_ROOT

log: logging.Logger = logging.getLogger(__name__)


def snapshot_ttl(output_dir: Optional[str] = None) -> None:
    if output_dir is None:
        output_dir = str(PROJECT_ROOT / "software/tests/snapshot")
    # Take some copies of globals we need to manipulate.
    # TODO: these globals should be arguments or similar
    outputdir_copy: str = schema.config.OUTPUTDIR
    selectors_copy: Set[str] = fileutils.FILESET_SELECTORS
    protocols_copy: Set[str] = fileutils.FILESET_PROTOCOLS
    schema.config.OUTPUTDIR = ""
    fileutils.FILESET_SELECTORS = {"all"}
    fileutils.FILESET_PROTOCOLS = {"https"}

    log.info("Building snapshot file...")
    sdotermsource.SdoTermSource.loadSourceGraph("default")
    buildfiles.exportrdf("RDFExport.turtle", subdirectory_path=output_dir)
    log.info(f"Snapshot file created in {output_dir}")

    # Put back the original values.
    schema.config.OUTPUTDIR = outputdir_copy
    fileutils.FILESET_SELECTORS = selectors_copy
    fileutils.FILESET_PROTOCOLS = protocols_copy


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    snapshot_ttl()
