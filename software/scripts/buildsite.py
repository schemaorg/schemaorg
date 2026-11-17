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

from schemaorg import constants, markdown
from schemaorg.collaborators import CollaboratorRegistry
from schemaorg.graph_loader import GraphLoader
from schemaorg.jsonld_slice import TermJsonLdIndex
from schemaorg.layout import (
    InputLayout,
    NEXT_VERSION,
    OutputLayout,
    Releases,
    checkDataDirectories,
)
from schemaorg.model import Vocabulary, VocabularyLoader
from schemaorg.term_view import TermViewCatalog
from schemaorg.version import VersionItem
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
        help="create the release files (always the complete set; any value such as ALL triggers it)",
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
    parser.add_argument(
        "--version",
        default=NEXT_VERSION,
        help="Target release version ('next', 'latest', or declared X.Y)",
    )

    parsed_args = parser.parse_args(args_list)

    # Copy lists so overriding schema.config.* below leaves parsed_args intact.
    schema.config.BUILDOPTS = list(parsed_args.buildoption)
    schema.config.TERMS = list(parsed_args.terms)
    schema.config.PAGES = list(parsed_args.docspages)
    schema.config.FILES = list(parsed_args.files)
    schema.config.TARGET_VERSION = parsed_args.version

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

    markdown.Markdown.setWikilinkCssClass("localLink")
    markdown.Markdown.setWikilinkPrePath("/")
    markdown.Markdown.setWikilinkPostPath("")

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

    with pretty_logger.BlockLog(
        logger=log, message="Preparing GCloud files"
    ) as block:
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


def load_site_bundle(
    input_layout: InputLayout | None = None,
    target: VersionItem | None = None,
) -> tuple[TermViewCatalog, TermJsonLdIndex, Path]:
    """Load Vocabulary, Collaborators, and JSON-LD slice index once from Releases."""
    layout = input_layout or paths.DefaultInputLayout()
    resolved = target or schema.target_version()
    releases = Releases(layout, schema.VERSION)
    release_file = releases.file(resolved)
    if not release_file.exists():
        raise FileNotFoundError(
            f"Release file not found: {release_file}. "
            "Please run --buildrelease first."
        )
    release_jsonld = releases.file(resolved, extension=".jsonld")

    with pretty_logger.BlockLog(
        logger=log,
        message=f"Loading vocabulary from release {release_file}",
        timing=True,
    ):
        graph = GraphLoader.load([release_file])
        vocab = VocabularyLoader(graph, version=resolved).load()
        collaborators = CollaboratorRegistry.from_layout(layout, vocab)
        catalog = TermViewCatalog.from_graph(graph, vocab, collaborators)
        jsonld_index = TermJsonLdIndex.from_graph(
            graph, jsonld_file=release_jsonld
        )
    return catalog, jsonld_index, release_file


def processTerms(
    terms: Iterable[str],
    catalog: TermViewCatalog,
    jsonld_index: TermJsonLdIndex,
    release_file: Path,
) -> None:
    if any(terms):
        with pretty_logger.BlockLog(
            logger=log, message="Building term definition pages", timing=True
        ):
            config = {
                "stats_providers": stats.get_stats_providers(),
                "build_opts": schema.config.BUILDOPTS,
                "term_docs_dir": schema.constants.TERMDOCSDIR,
                "target_version": schema.config.TARGET_VERSION,
                "output_dir": schema.config.OUTPUTDIR,
                "release_file": str(release_file),
            }
            buildtermpages.buildTerms(
                terms,
                config=config,
                catalog=catalog,
                jsonld_index=jsonld_index,
            )


def processDocs(pages: Iterable[str], catalog: TermViewCatalog) -> None:
    if any(pages):
        with pretty_logger.BlockLog(
            logger=log,
            message="Building dynamic documentation pages",
            timing=True,
        ):
            buildocspages.buildDocs(pages, catalog=catalog)


def processFiles(vocab: Vocabulary | None = None) -> None:
    with pretty_logger.BlockLog(logger=log, message="Building supporting files"):
        buildfiles.export_site_docs(
            input_layout=paths.DefaultInputLayout(),
            output_layout=paths.DefaultOutputLayout(),
            version=schema.target_version(),
            vocab=vocab,
        )


def runShaclTests(releases_output_dir: str | Path | None = None) -> None:
    """Run the SHACL validation tests on the generated examples."""
    with pretty_logger.BlockLog(
        logger=log, message="Running SHACL validation tests"
    ):
        cmd = [
            sys.executable,
            str(
                constants.PROJECT_ROOT
                / "software/scripts/validate_examples_shacl.py"
            ),
            "--version",
            schema.target_version().number(),
        ]
        if releases_output_dir is not None:
            cmd.extend(["-o", str(releases_output_dir)])
        status = subprocess.run(cmd, check=False).returncode
        if status:
            log.error(
                "SHACL validation reported errors (exit code %d). Failing build.",
                status,
            )
            sys.exit(status)


def main(argv: Sequence[str] | None = None) -> None:
    global args
    args = initialize(argv)

    checkDataDirectories()

    target = schema.target_version()
    log.info(
        "Version: %s Released: %s",
        target.number(),
        target.date() or "unreleased",
    )

    tests_ran = False
    shacl_ran = False

    # STAGE 1: Build Release
    if args.buildrelease or args.release:
        log.info("=== STAGE 1: BUILDING RELEASE VERSION ===")
        runtests()
        tests_ran = True

        with pretty_logger.BlockLog(
            logger=log, message="Building release files"
        ):
            buildfiles.export_release_files(
                input_layout=paths.DefaultInputLayout(),
                output_layout=OutputLayout(constants.PROJECT_ROOT / "data"),
                version=target,
            )

        runShaclTests()
        shacl_ran = True

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
        catalog, jsonld_index, release_file = load_site_bundle(target=target)
        schema.config.OUTPUTDIR = args.output or str(
            constants.PROJECT_ROOT / "software/site"
        )

        initdir(output_dir_str=schema.config.OUTPUTDIR)
        if not tests_ran:
            runtests()
            tests_ran = True

        processTerms(
            terms=schema.config.TERMS,
            catalog=catalog,
            jsonld_index=jsonld_index,
            release_file=release_file,
        )
        processDocs(pages=schema.config.PAGES, catalog=catalog)
        if any(schema.config.FILES) or args.buildsite:
            processFiles(vocab=catalog.vocab)

        if args.shacltests and not shacl_ran:
            runShaclTests()
            shacl_ran = True

        log.info("=== STAGE 2: SITE BUILD COMPLETED SUCCESSFULLY ===")

    # Global Testing Trigger
    if (args.runtests or args.shacltests) and not (
        build_site_requested or args.buildrelease or args.release
    ):
        log.info("=== RUNNING SCRIBED TEST SUITES ===")
        if not tests_ran:
            runtests()
        if args.shacltests and not shacl_ran:
            runShaclTests()


if __name__ == "__main__":
    main()
