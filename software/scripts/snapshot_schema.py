import logging
import os
import shutil
import sys
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, Set, Tuple, Union
import typing

if os.getcwd() not in sys.path:
    sys.path.insert(1, os.getcwd())
import software

import SchemaTerms.sdotermsource as sdotermsource
import scripts.buildfiles as buildfiles
import util.fileutils as fileutils
import util.pretty_logger as pretty_logger
import util.schemaglobals as schemaglobals

log: logging.Logger = logging.getLogger(__name__)


def snapshot_ttl(output_dir: str = "software/tests/snapshot") -> None:
    # Take some copies of globals we need to manipulate.
    # TODO: these globals should be arguments or similar
    outputdir_copy: str = schemaglobals.OUTPUTDIR
    selectors_copy: Set[str] = fileutils.FILESET_SELECTORS
    protocols_copy: Set[str] = fileutils.FILESET_PROTOCOLS
    schemaglobals.OUTPUTDIR = ""
    fileutils.FILESET_SELECTORS = {"all"}
    fileutils.FILESET_PROTOCOLS = {"https"}

    log.info("Building snapshot file...")
    sdotermsource.SdoTermSource.loadSourceGraph("default")
    buildfiles.exportrdf("RDFExport.turtle", subdirectory_path=output_dir)
    log.info(f"Snapshot file created in {output_dir}")

    # Put back the original values.
    schemaglobals.OUTPUTDIR = outputdir_copy
    fileutils.FILESET_SELECTORS = selectors_copy
    fileutils.FILESET_PROTOCOLS = protocols_copy


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    snapshot_ttl()
