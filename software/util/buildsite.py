#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Program that builds the whole schema.org website."""

import argparse
import contextlib
import datetime
import glob
import os
import shutil
import subprocess
import sys
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union, Iterable, Sequence, Generator, Type

if os.getcwd() not in sys.path:
    sys.path.insert(1, os.getcwd())

import software
import software.util.buildfiles as buildfiles
import software.util.buildocspages as buildocspages
import software.util.buildtermpages as buildtermpages
import software.util.copystaticdocsplusinsert as copystaticdocsplusinsert
import software.util.fileutils as fileutils
import software.util.runtests as runtests_lib
import software.util.schemaglobals as schemaglobals
import software.util.schemaversion as schemaversion
import software.util.pretty_logger as pretty_logger
import software.SchemaExamples.schemaexamples as schemaexamples
import software.SchemaExamples.utils.assign_example_ids
import software.SchemaTerms.localmarkdown
import software.SchemaTerms.sdocollaborators as sdocollaborators
import software.SchemaTerms.sdotermsource as sdotermsource

log: logging.Logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

args: argparse.Namespace

def initialize() -> argparse.Namespace:
    """Initialize various systems, returns the args object"""
    parser: argparse.ArgumentParser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-a",
        "--autobuild",
        default=False,
        action="store_true",
        help="clear output directory and build all components - overrides all other settings (except -examplesnum)",
    )
    parser.add_argument(
        "-c",
        "--clearfirst",
        default=False,
        action="store_true",
        help="clear output directory before creating contents",
    )
    parser.add_argument(
        "-d",
        "--docspages",
        default=[],
        action="append",
        nargs="*",
        help="create docs page(repeatable) - ALL = all pages",
    )
    parser.add_argument(
        "-e",
        "--examplesnum",
        default=False,
        action="store_true",
        help="Add missing example ids",
    )
    parser.add_argument(
        "-f",
        "--files",
        default=[],
        action="append",
        nargs="*",
        help="create files(repeatable) - ALL = all files",
    )
    parser.add_argument(
        "-o", "--output", help="output site directory (default: ./software/site)"
    )
    parser.add_argument(
        "-r",
        "--runtests",
        default=False,
        action="store_true",
        help="run test scripts before creating contents",
    )
    parser.add_argument(
        "-s",
        "--static",
        default=False,
        action="store_true",
        help="Refresh static docs in site image",
    )
    parser.add_argument(
        "-t",
        "--terms",
        default=[],
        action="append",
        nargs="*",
        help="create page for term (repeatable) - ALL = all terms",
    )
    parser.add_argument(
        "-b",
        "--buildoption",
        default=[],
        action="append",
        nargs="*",
        help="build option(repeatable) - flags to be passed to build code",
    )
    parser.add_argument(
        "--shacltests",
        default=False,
        action="store_true",
        help="run the post generation SHACL tests",
    )
    parser.add_argument(
        "-release",
        "--release",
        default=False,
        action="store_true",
        help="create page for term (repeatable) - ALL = all terms",
    )

    args: argparse.Namespace = parser.parse_args()

    op: List[str]
    for op in args.buildoption:
        schemaglobals.BUILDOPTS.extend(op)

    ter: List[str]
    for ter in args.terms:
        schemaglobals.TERMS.extend(ter)

    pgs: List[str]
    for pgs in args.docspages:
        schemaglobals.PAGES.extend(pgs)

    fls: List[str]
    for fls in args.files:
        schemaglobals.FILES.extend(fls)

    if args.output:
        schemaglobals.OUTPUTDIR = args.output

    if args.autobuild or args.release or args.shacltests:
        schemaglobals.TERMS = ["ALL"]
        schemaglobals.PAGES = ["ALL"]
        schemaglobals.FILES = ["ALL"]

    software.SchemaTerms.localmarkdown.Markdown.setWikilinkCssClass("localLink")
    software.SchemaTerms.localmarkdown.Markdown.setWikilinkPrePath("/")
    software.SchemaTerms.localmarkdown.Markdown.setWikilinkPostPath("")

    pretty_logger.MakeRootLogPretty()

    return args


def clear() -> None:
    if args.clearfirst or args.autobuild:
        output_dir: Path = Path(schemaglobals.OUTPUTDIR)
        log.info(f"Clearing {output_dir} directory")
        if output_dir.is_dir():
            item: Path
            for item in output_dir.iterdir():
                if item.name == ".gitkeep":
                    continue
                if item.is_dir():
                    shutil.rmtree(item)
                else:
                    item.unlink()


def runtests() -> None:
    if args.runtests or args.autobuild:
        with pretty_logger.BlockLog(
            logger=log, message="Running test scripts before proceeding…"
        ):
            errorcount: int = runtests_lib.main("./software/tests/")
            if errorcount:
                log.error(f"Errors returned: {errorcount}")
                sys.exit(errorcount)


def initdir(output_dir_str: str, handler_path: str) -> None:
    output_dir: Path = Path(output_dir_str)
    log.info(f'Building site in "{output_dir}" directory')
    output_dir.mkdir(parents=True, exist_ok=True)
    clear()

    (output_dir / "docs" / "contributors").mkdir(parents=True, exist_ok=True)
    (output_dir / "empty").mkdir(parents=True, exist_ok=True)
    (output_dir / "releases" / schemaversion.getVersion()).mkdir(parents=True, exist_ok=True)

    gdir: Path = output_dir / "gcloud"
    gdir.mkdir(parents=True, exist_ok=True)

    with pretty_logger.BlockLog(logger=log, message="Copying docs static files"):
        copystaticdocsplusinsert.copyFiles("./docs", str(output_dir / "docs"))

    with pretty_logger.BlockLog(logger=log, message="Preparing GCloud files") as block:
        gcloud_files: List[Path] = sorted(Path("software/gcloud").glob("*.yaml"))
        path: Path
        for path in gcloud_files:
            shutil.copy(path, gdir)
        block.append(f"copied {len(gcloud_files)} files")

    version: str = schemaversion.getVersion()
    message: str = f"Creating {handler_path} from {schemaglobals.HANDLER_TEMPLATE} for version: {version}"
    with pretty_logger.BlockLog(logger=log, message=message):
        template_file: Path = gdir / schemaglobals.HANDLER_TEMPLATE
        template_data: str = template_file.read_text()
        handler_data: str = template_data.replace("{{ver}}", version)
        (gdir / handler_path).write_text(handler_data)


LOADEDTERMS: bool = False


def loadTerms() -> None:
    global LOADEDTERMS
    if LOADEDTERMS:
        return
    LOADEDTERMS = True
    if not sdotermsource.SdoTermSource.SOURCEGRAPH:
        with pretty_logger.BlockLog(logger=log, message="Loading triples files"):
            sdotermsource.SdoTermSource.loadSourceGraph("default")

        with pretty_logger.BlockLog(logger=log, message="Loading contributors"):
            sdocollaborators.collaborator.loadContributors()


def processTerms(terms: Iterable[str]) -> None:
    if any(terms):
        with pretty_logger.BlockLog(
            logger=log, message="Building term definition pages", timing=True
        ):
            loadTerms()
            schemaexamples.SchemaExamples.loaded()
            buildtermpages.buildTerms(terms)


def processDocs(pages: Iterable[str]) -> None:
    if any(pages):
        with pretty_logger.BlockLog(
            logger=log, message="Building dynamic documentation pages", timing=True
        ):
            loadTerms()
            buildocspages.buildDocs(pages)


def processFiles(files: Iterable[str]) -> None:
    if any(files):
        with pretty_logger.BlockLog(logger=log, message="Building supporting files"):
            loadTerms()
            schemaexamples.SchemaExamples.loaded()
            buildfiles.buildFiles(files)


def runShaclTests() -> None:
    """Run the SHACL validation tests on the generated examples."""
    with pretty_logger.BlockLog(logger=log, message="Running SHACL validation tests"):
        version: str = schemaversion.getVersion()
        shacl_file: Path = Path.cwd() / schemaglobals.RELEASE_DIR / version / "schemaorg-shapes.shacl"
        if not shacl_file.exists():
            log.warning(f"SHACL file {shacl_file} not found. Skipping SHACL validation.")
            return

        cmd: List[str] = [sys.executable, "software/scripts/validate_examples_shacl.py"]
        status: int = subprocess.call(cmd)
        if status:
            log.error(f"SHACL validation reported errors (exit code {status}). Failing build.")
            sys.exit(status)


def copyReleaseFiles(release_dir: str) -> None:
    version: str = schemaversion.getVersion()
    srcdir: Path = Path.cwd() / "data" / "releases" / version
    destdir: Path = Path.cwd() / release_dir / version
    with pretty_logger.BlockLog(
        message=f"Copying release files from {srcdir} to {destdir}",
        logger=log,
    ):
        fileutils.mycopytree(str(srcdir), str(destdir))
        cmd: List[str] = ["git", "add", str(destdir)]
        subprocess.check_call(cmd)


if __name__ == "__main__":
    args = initialize()

    software.CheckWorkingDirectory()
    log.info(
        f"Version: {schemaversion.getVersion()} Released: {schemaversion.getCurrentVersionDate()}"
    )
    if args.shacltests:
        args.autobuild = True
    if args.release:
        args.autobuild = True
        log.info("BUILDING RELEASE VERSION")
    if args.examplesnum or args.release or args.autobuild:
        with pretty_logger.BlockLog(
            message="Checking Examples for assigned identifiers", logger=log
        ):
            software.SchemaExamples.utils.assign_example_ids.AssignExampleIds()
    initdir(output_dir_str=schemaglobals.OUTPUTDIR, handler_path=schemaglobals.HANDLER_FILE)
    runtests()
    processTerms(terms=schemaglobals.TERMS)
    processDocs(pages=schemaglobals.PAGES)
    processFiles(files=schemaglobals.FILES)

    if args.release:
        copyReleaseFiles(release_dir=schemaglobals.RELEASE_DIR)
    if args.shacltests:
        runShaclTests()
