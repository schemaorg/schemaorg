#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Program that builds the whole schema.org website."""

import argparse
import contextlib
import datetime
import glob
import json
import logging
import os
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Any, Dict, Generator, Iterable, List, Optional, Sequence, Tuple, Type, Union

if os.getcwd() not in sys.path:
    sys.path.insert(1, os.getcwd())
import software

import SchemaExamples.schemaexamples as schemaexamples
import SchemaExamples.utils.assign_example_ids
import SchemaTerms.localmarkdown
import SchemaTerms.sdocollaborators as sdocollaborators
import SchemaTerms.sdotermsource as sdotermsource
import scripts.buildfiles as buildfiles
import scripts.runtests as runtests_lib
import util.buildocspages as buildocspages
import util.buildtermpages as buildtermpages
import util.copystaticdocsplusinsert as copystaticdocsplusinsert
import util.fileutils as fileutils
import util.paths as paths
import util.pretty_logger as pretty_logger
import util.schema as schema
import util.stats as stats


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
    parser.add_argument(
        "--buildrelease",
        default=False,
        action="store_true",
        help="Build the release files and save them into the releases data directory",
    )
    parser.add_argument(
        "--buildsite",
        default=False,
        action="store_true",
        help="Build the website from the releases directory + static content + stats",
    )

    args: argparse.Namespace = parser.parse_args()

    op: List[str]
    for op in args.buildoption:
        schema.config.BUILDOPTS.extend(op)

    ter: List[str]
    for ter in args.terms:
        schema.config.TERMS.extend(ter)

    pgs: List[str]
    for pgs in args.docspages:
        schema.config.PAGES.extend(pgs)

    fls: List[str]
    for fls in args.files:
        schema.config.FILES.extend(fls)

    if args.output:
        schema.config.OUTPUTDIR = args.output

    if args.autobuild or args.release or args.shacltests or args.buildrelease:
        schema.config.TERMS = ["ALL"]
        schema.config.PAGES = ["ALL"]
        schema.config.FILES = ["ALL"]

    SchemaTerms.localmarkdown.Markdown.setWikilinkCssClass("localLink")
    SchemaTerms.localmarkdown.Markdown.setWikilinkPrePath("/")
    SchemaTerms.localmarkdown.Markdown.setWikilinkPostPath("")

    pretty_logger.MakeRootLogPretty()

    return args


def clear() -> None:
    if args.clearfirst or args.autobuild:
        output_dir: Path = Path(schema.config.OUTPUTDIR)
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
            cmd = [sys.executable, "software/scripts/runtests.py"]
            status = subprocess.call(cmd)
            if status:
                log.error(f"Errors returned: {status}")
                sys.exit(status)


def initdir(output_dir_str: str, handler_path: str) -> None:
    output_dir: Path = Path(output_dir_str)
    log.info(f'Building site in "{output_dir}" directory')
    output_dir.mkdir(parents=True, exist_ok=True)
    clear()

    (output_dir / "docs" / "contributors").mkdir(parents=True, exist_ok=True)
    (output_dir / "empty").mkdir(parents=True, exist_ok=True)
    (output_dir / "releases" / schema.getVersion()).mkdir(parents=True, exist_ok=True)

    gdir: Path = output_dir / "gcloud"
    gdir.mkdir(parents=True, exist_ok=True)

    with pretty_logger.BlockLog(logger=log, message="Copying docs static files"):
        copystaticdocsplusinsert.copyFiles(str(paths.DefaultInputLayout().domain_dir(paths.Domain.DOCS)), str(paths.DefaultOutputLayout().domain_dir(paths.Domain.DOCS)))

    with pretty_logger.BlockLog(logger=log, message="Preparing GCloud files") as block:
        gcloud_files: List[Path] = paths.DefaultInputLayout().domain_files(paths.Domain.GCLOUD, "*.yaml")
        path: Path
        for path in gcloud_files:
            shutil.copy(path, gdir)
        block.append(f"copied {len(gcloud_files)} files")

    version: str = schema.getVersion()
    message: str = f"Creating {handler_path} from {schema.constants.HANDLER_TEMPLATE} for version: {version}"
    with pretty_logger.BlockLog(logger=log, message=message):
        template_file: Path = paths.DefaultInputLayout().domain_file(paths.Domain.GCLOUD, "handlers-template.yaml")
        template_data: str = template_file.read_text()
        handler_data: str = template_data.replace("{{ver}}", version)
        paths.DefaultOutputLayout().domain_file(paths.Domain.GCLOUD, "handlers.yaml").write_text(handler_data)


LOADEDTERMS: Optional[str] = None


def loadTerms(source: Optional[str] = None, force: bool = False) -> None:
    global LOADEDTERMS

    # If no source is requested, and we already loaded something, we're done.
    if source is None:
        if LOADEDTERMS is not None:
            return
        # Default fallback for lazy calls that happen before explicit stage loading
        source = "release"

    # If the requested source is already loaded, and we don't force, we're done.
    if LOADEDTERMS == source and not force:
        return

    init_graph: bool = (LOADEDTERMS is not None) or force
    LOADEDTERMS = source

    if not sdotermsource.SdoTermSource.SOURCEGRAPH or init_graph:
        if source == "default":
            with pretty_logger.BlockLog(logger=log, message="Loading development triples files (default)"):
                sdotermsource.SdoTermSource.loadSourceGraph("default", init=init_graph)
        elif source == "release":
            protocol: str = "https" if sdotermsource.SdoTermSource.vocabUri().startswith("https") else "http"
            release_file: Path = paths.DefaultInputLayout().release_file(protocol)

            if not release_file.exists():
                raise FileNotFoundError(
                    f"Release file not found: {release_file}. "
                    "Please run --buildrelease first."
                )

            with pretty_logger.BlockLog(logger=log, message=f"Loading triples from release file {release_file}"):
                sdotermsource.SdoTermSource.loadSourceGraph(str(release_file), init=init_graph)
        else:
            raise ValueError(f"Invalid term source: {source}")

        if init_graph:
            sdocollaborators.collaborator.COLLABORATORS.clear()
            sdocollaborators.collaborator.CONTRIBUTORS.clear()

        with pretty_logger.BlockLog(logger=log, message="Loading contributors"):
            sdocollaborators.collaborator.loadContributors()


def processTerms(terms: Iterable[str]) -> None:
    if any(terms):
        with pretty_logger.BlockLog(
            logger=log, message="Building term definition pages", timing=True
        ):
            loadTerms()
            schemaexamples.SchemaExamples.loaded()
            config = {
                "stats_providers": stats.get_stats_providers(),
                "build_opts": schema.config.BUILDOPTS,
                "term_docs_dir": schema.constants.TERMDOCSDIR,
            }
            buildtermpages.buildTerms(terms, config=config)


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
        version: str = schema.getVersion()
        shacl_file: Path = Path.cwd() / schema.constants.RELEASE_DIR / version / "schemaorg-shapes.shacl"
        if not shacl_file.exists():
            log.warning(f"SHACL file {shacl_file} not found. Skipping SHACL validation.")
            return

        cmd: List[str] = [
            sys.executable,
            "software/scripts/validate_examples_shacl.py",
            "-o",
            schema.config.OUTPUTDIR,
        ]
        status: int = subprocess.call(cmd)
        if status:
            log.error(f"SHACL validation reported errors (exit code {status}). Failing build.")
            sys.exit(status)


def copyReleaseFiles(release_dir: str) -> None:
    version: str = schema.getVersion()
    srcdir: Path = paths.DefaultInputLayout().domain_dir(paths.Domain.RELEASE_DATA)
    destdir: Path = paths.DefaultOutputLayout().domain_dir(paths.Domain.RELEASE)
    if not srcdir.is_dir():
        log.warning(f"Release data directory {srcdir} not found. Skipping copying release files.")
        return
    with pretty_logger.BlockLog(
        message=f"Copying release files from {srcdir} to {destdir}",
        logger=log,
    ):
        fileutils.mycopytree(str(srcdir), str(destdir))
        cmd: List[str] = ["git", "add", "-f", str(destdir)]
        subprocess.check_call(cmd)


if __name__ == "__main__":
    args = initialize()

    software.CheckWorkingDirectory()
    log.info(
        f"Version: {schema.getVersion()} Released: {schema.getCurrentVersionDate()}"
    )

    # STAGE 1: Build Release
    if args.buildrelease or args.release:
        log.info("=== STAGE 1: BUILDING RELEASE VERSION ===")
        loadTerms(source="default")

        with pretty_logger.BlockLog(
            message="Checking Examples for assigned identifiers", logger=log
        ):
            SchemaExamples.utils.assign_example_ids.AssignExampleIds()

        schema.config.OUTPUTDIR = "data"

        # Run tests first
        runtests()

        # Generate schema-all.html (the FullRelease documentation page)
        processDocs(pages=["FullRelease"])

        # Generate all vocabulary/schema release files
        release_files = ["Context", "Owl", "Httpequivs", "Examples", "RDFExports", "CSVExports", "Shex_Shacl"]
        processFiles(files=release_files)

        # Validate the generated release files against shapes
        runShaclTests()

        temp_docs_dir = Path("data/docs")
        if temp_docs_dir.is_dir():
            log.info("Cleaning up temporary files in data/docs")
            shutil.rmtree(temp_docs_dir)

        log.info("=== STAGE 1: RELEASE BUILD COMPLETED SUCCESSFULLY ===")

    # STAGE 2: Build Site
    if args.buildsite or args.autobuild or any(args.files) or any(args.docspages) or any(args.terms):
        log.info("=== STAGE 2: BUILDING SITE ===")
        loadTerms(source="release")
        schema.config.OUTPUTDIR = "software/site"

        if args.examplesnum or args.autobuild:
            with pretty_logger.BlockLog(
                message="Checking Examples for assigned identifiers", logger=log
            ):
                SchemaExamples.utils.assign_example_ids.AssignExampleIds()

        initdir(output_dir_str=schema.config.OUTPUTDIR, handler_path=schema.constants.HANDLER_FILE)
        runtests()
        if args.buildsite or args.autobuild:
            copyReleaseFiles(release_dir=schema.constants.RELEASE_DIR)

        processTerms(terms=schema.config.TERMS)
        processDocs(pages=schema.config.PAGES)
        processFiles(files=schema.config.FILES)

        if args.shacltests:
            runShaclTests()

        log.info("=== STAGE 2: SITE BUILD COMPLETED SUCCESSFULLY ===")

    # Global Testing Trigger
    if (args.runtests or args.shacltests) and not (args.buildsite or args.autobuild or args.buildrelease or args.release or any(args.files) or any(args.docspages) or any(args.terms)):
        log.info("=== RUNNING SCRIBED TEST SUITES ===")
        runtests()
        if args.shacltests:
            runShaclTests()
