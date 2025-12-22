import os
import shutil
import logging
import sys

# Import schema.org libraries
if not os.getcwd() in sys.path:
    sys.path.insert(1, os.getcwd())

import software
import software.util.fileutils as fileutils
import software.util.schemaglobals as schemaglobals
import software.SchemaTerms.sdotermsource as sdotermsource
import software.util.buildfiles as buildfiles
import software.util.pretty_logger as pretty_logger

log = logging.getLogger(__name__)


def snapshot_ttl(output_dir: str = "software/tests/snapshot"):
    # Take some copies of globals we need to manipulate.
    # TODO: these globals should be arguments or similar
    outputdir_copy = schemaglobals.OUTPUTDIR
    selectors_copy = fileutils.FILESET_SELECTORS
    protocols_copy = fileutils.FILESET_PROTOCOLS
    schemaglobals.OUTPUTDIR = ""
    fileutils.FILESET_SELECTORS = ("all",)
    fileutils.FILESET_PROTOCOLS = ("https",)

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
