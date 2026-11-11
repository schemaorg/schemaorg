#!/usr/bin/env python3
"""Program that builds the whole schema.org website."""

from __future__ import annotations

import argparse
from collections.abc import Iterable, Sequence
import logging
from pathlib import Path
import shutil
import subprocess
import sys

from schemaorg import constants
from schemaorg.layout import Releases, checkDataDirectories
import SchemaTerms.localmarkdown
import SchemaTerms.sdocollaborators as sdocollaborators
import SchemaTerms.sdotermsource as sdotermsource
import scripts.buildfiles as buildfiles
import util.buildocspages as buildocspages
import util.buildtermpages as buildtermpages
import util.copystaticdocsplusinsert as copystaticdocsplusinsert
import util.paths as paths
import util.pretty_logger as pretty_logger
import util.schema as schema
import util.stats as stats

log: logging.Logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

args: argparse.Namespace


def initialize(args_list: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse CLI flags and initialize build configuration."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-a",
        "--autobuild",
        action="store_true",
        help="clear output directory and build all components - overrides all other settings",
    )
    parser.add_argument(
        "-c",
        "--clearfirst",
        action="store_true",
        help="clear output directory before creating contents",
    )
    parser.add_argument(
        "-d",
        "--docspages",
        default=[],
        action="extend",
        nargs="*",
        help="create docs page(repeatable) - ALL = all pages",
    )
    parser.add_argument(
        "-f",
        "--files",
        default=[],
        action="extend",
        nargs="*",
        help="create files(repeatable) - ALL = all files",
    )
    parser.add_argument(
        "-o", "--output", help="output site directory (default: ./software/site)"
    )
    parser.add_argument(
        "-r",
        "--runtests",
        action="store_true",
        help="run test scripts before creating contents",
    )
    parser.add_argument(
        "-s",
        "--static",
        action="store_true",
        help="Refresh static docs in site image",
    )
    parser.add_argument(
        "-t",
        "--terms",
        default=[],
        action="extend",
        nargs="*",
        help="create page for term (repeatable) - ALL = all terms",
    )
    parser.add_argument(
        "-b",
        "--buildoption",
        default=[],
        action="extend",
        nargs="*",
        help="build option(repeatable) - flags to be passed to build code",
    )
    parser.add_argument(
        "--shacltests",
        action="store_true",
        help="run the post generation SHACL tests",
    )
    parser.add_argument(
        "-release",
        "--release",
        action="store_true",
        help="Build the release files into the releases data directory",
    )
    parser.add_argument(
        "--buildrelease",
        action="store_true",
        help="Build the release files and save them into the releases data directory",
    )
    parser.add_argument(
        "--buildsite",
        action="store_true",
        help="Build the website from the releases directory + static content + stats",
    )

    parsed_args = parser.parse_args(args_list)

    # Copy lists so overriding schema.config.* below leaves parsed_args intact.
    schema.config.BUILDOPTS = list(parsed_args.buildoption)
    schema.config.TERMS = list(parsed_args.terms)
    schema.config.PAGES = list(parsed_args.docspages)
    schema.config.FILES = list(parsed_args.files)

    if parsed_args.output:
        schema.config.OUTPUTDIR = parsed_args.output

    if (
        parsed_args.autobuild
        or parsed_args.release
        or parsed_args.shacltests
        or parsed_args.buildrelease
    ):
        schema.config.TERMS = ["ALL"]
        schema.config.PAGES = ["ALL"]
        schema.config.FILES = ["ALL"]

    SchemaTerms.localmarkdown.Markdown.setWikilinkCssClass("localLink")
    SchemaTerms.localmarkdown.Markdown.setWikilinkPrePath("/")
    SchemaTerms.localmarkdown.Markdown.setWikilinkPostPath("")

    pretty_logger.MakeRootLogPretty()

    return parsed_args


def clear() -> None:
    if args.clearfirst or args.autobuild:
        output_dir = Path(schema.config.OUTPUTDIR)
        log.info("Clearing %s directory", output_dir)
        if output_dir.is_dir():
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
            cmd = [
                sys.executable,
                str(constants.PROJECT_ROOT / "software/scripts/runtests.py"),
            ]
            status = subprocess.run(cmd, check=False).returncode
            if status:
                log.error("Errors returned: %d", status)
                sys.exit(status)


def initdir(output_dir_str: str) -> None:
    log.info('Building site in "%s" directory', output_dir_str)
    clear()

    input_layout = paths.DefaultInputLayout()
    output_layout = paths.DefaultOutputLayout()
    output_layout.dir(paths.Domain.EMPTY)

    with pretty_logger.BlockLog(logger=log, message="Copying docs static files"):
        copystaticdocsplusinsert.copyFiles(
            str(input_layout.dir(paths.Domain.DOCS)),
            str(output_layout.dir(paths.Domain.DOCS)),
        )

    with pretty_logger.BlockLog(logger=log, message="Preparing GCloud files") as block:
        gdir = output_layout.dir(paths.Domain.GCLOUD)
        gcloud_files = input_layout.files(paths.Domain.GCLOUD, "*.yaml")
        for path in gcloud_files:
            shutil.copy(path, gdir)
        block.append(f"copied {len(gcloud_files)} files")

    version = schema.VERSION.current().number()
    message = (
        f"Creating {schema.constants.HANDLER_FILE} from "
        f"{schema.constants.HANDLER_TEMPLATE} for version: {version}"
    )
    with pretty_logger.BlockLog(logger=log, message=message):
        template_file = input_layout.file(
            paths.Domain.GCLOUD, schema.constants.HANDLER_TEMPLATE
        )
        template_data = template_file.read_text(encoding="utf-8")
        handler_data = template_data.replace("{{ver}}", version)
        output_layout.file(
            paths.Domain.GCLOUD, schema.constants.HANDLER_FILE
        ).write_text(handler_data, encoding="utf-8")


LOADEDTERMS: str | None = None


def loadTerms(source: str | None = None, force: bool = False) -> None:
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

    init_graph = (LOADEDTERMS is not None) or force
    LOADEDTERMS = source

    if not sdotermsource.SdoTermSource.SOURCEGRAPH or init_graph:
        if source == "default":
            with pretty_logger.BlockLog(
                logger=log, message="Loading development triples files (default)"
            ):
                sdotermsource.SdoTermSource.loadSourceGraph("default", init=init_graph)
        elif source == "release":
            release_file = Releases(
                paths.DefaultInputLayout(), schema.VERSION
            ).file()

            if not release_file.exists():
                raise FileNotFoundError(
                    f"Release file not found: {release_file}. "
                    "Please run --buildrelease first."
                )

            with pretty_logger.BlockLog(
                logger=log, message=f"Loading triples from release file {release_file}"
            ):
                sdotermsource.SdoTermSource.loadSourceGraph(
                    str(release_file), init=init_graph
                )
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
            buildfiles.buildFiles(files)


def runShaclTests() -> None:
    """Run the SHACL validation tests on the generated examples."""
    with pretty_logger.BlockLog(logger=log, message="Running SHACL validation tests"):
        cmd = [
            sys.executable,
            str(constants.PROJECT_ROOT / "software/scripts/validate_examples_shacl.py"),
            "-o",
            schema.config.OUTPUTDIR,
        ]
        status = subprocess.run(cmd, check=False).returncode
        if status:
            log.error(
                "SHACL validation reported errors (exit code %d). Failing build.",
                status,
            )
            sys.exit(status)


def copyReleaseFiles() -> None:
    """Copy the built release files into the site tree for deployment.

    The destination is *disposable build output*. Its only consumers are the
    deploy scripts, which `cd software/site` and upload whatever is there.

    This function used to end with `git add -f <destdir>`, which is why 36
    files / 54 MB of scratch output landed in the repository in the 30.1
    release commit. The `-f` was specifically overriding the
    `software/site/*` .gitignore rule. It was never right: the only caller is
    STAGE 2, where OUTPUTDIR is `software/site`, so it could only ever stage
    the throwaway copy -- never the real archive in `data/releases/`, which
    STAGE 1 produces and which a human commits deliberately.

    Do not re-add it. A build script has no business touching the index.
    """
    srcdir = Releases(paths.DefaultInputLayout(), schema.VERSION).dir()
    destdir = Releases(paths.DefaultOutputLayout(), schema.VERSION).dir()
    if not srcdir.is_dir():
        log.warning(
            "Release data directory %s not found. Skipping copying release files.",
            srcdir,
        )
        return
    with pretty_logger.BlockLog(
        message=f"Copying release files from {srcdir} to {destdir}",
        logger=log,
    ):
        shutil.copytree(srcdir, destdir, dirs_exist_ok=True)


def main(argv: Sequence[str] | None = None) -> None:
    global args
    args = initialize(argv)

    checkDataDirectories()

    log.info(
        "Version: %s Released: %s",
        schema.VERSION.current().number(),
        schema.VERSION.current().date(),
    )

    tests_ran = False

    # STAGE 1: Build Release
    if args.buildrelease or args.release:
        log.info("=== STAGE 1: BUILDING RELEASE VERSION ===")
        loadTerms(source="default")

        schema.config.OUTPUTDIR = str(constants.PROJECT_ROOT / "data")

        runtests()
        tests_ran = True

        # Generate schema-all.html (the FullRelease documentation page)
        processDocs(pages=["FullRelease"])

        # Generate all vocabulary/schema release files
        release_files = [
            "Context",
            "Owl",
            "Httpequivs",
            "Examples",
            "RDFExports",
            "CSVExports",
            "Shex_Shacl",
        ]
        processFiles(files=release_files)

        # Validate the generated release files against shapes
        runShaclTests()

        temp_docs_dir = constants.PROJECT_ROOT / "data/docs"
        if temp_docs_dir.is_dir():
            log.info("Cleaning up temporary files in data/docs")
            shutil.rmtree(temp_docs_dir)

        log.info("=== STAGE 1: RELEASE BUILD COMPLETED SUCCESSFULLY ===")

    # STAGE 2: Build Site
    build_site_requested = (
        args.buildsite
        or args.autobuild
        or args.static
        or bool(args.files)
        or bool(args.docspages)
        or bool(args.terms)
    )
    if build_site_requested:
        log.info("=== STAGE 2: BUILDING SITE ===")
        loadTerms(source="release")
        schema.config.OUTPUTDIR = args.output or str(
            constants.PROJECT_ROOT / "software/site"
        )

        initdir(output_dir_str=schema.config.OUTPUTDIR)
        if not tests_ran:
            runtests()
            tests_ran = True
        if args.buildsite or args.autobuild:
            copyReleaseFiles()

        processTerms(terms=schema.config.TERMS)
        processDocs(pages=schema.config.PAGES)
        processFiles(files=schema.config.FILES)

        if args.shacltests:
            runShaclTests()

        log.info("=== STAGE 2: SITE BUILD COMPLETED SUCCESSFULLY ===")

    # Global Testing Trigger
    if (args.runtests or args.shacltests) and not (
        build_site_requested or args.buildrelease or args.release
    ):
        log.info("=== RUNNING SCRIBED TEST SUITES ===")
        if not tests_ran:
            runtests()
        if args.shacltests:
            runShaclTests()


if __name__ == "__main__":
    main()
