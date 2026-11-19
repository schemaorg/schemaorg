#!/usr/bin/env python3
"""CLI shell generating a flat list of schema.org term IDs."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
import logging
from pathlib import Path

from schemaorg import constants
from schemaorg.graph_loader import GraphLoader
from schemaorg.layout import Domain, InputLayout, Issues, Releases
from schemaorg.model import VocabularyLoader
from schemaorg.progress import LogProgressReporter
from schemaorg.tasks.export_term_list import ExportTermListTask
from schemaorg.term_view import TermViewCatalog
from schemaorg.version import Version
import util.pretty_logger as pretty_logger

log: logging.Logger = logging.getLogger(__name__)


def _load_default_catalog(input_layout: InputLayout) -> TermViewCatalog:
    version = Version(input_layout.file(Domain.ROOT, constants.VERSIONS_FILE))
    target = version.next()
    rel_ttl = Releases(input_layout, version).file(target)
    ttl_files = (
        [rel_ttl]
        if rel_ttl.is_file()
        else Issues(input_layout).get_ttl_files()
    )
    graph = GraphLoader.load(ttl_files)
    vocab = VocabularyLoader(graph, version=target).load()
    return TermViewCatalog.from_graph(graph, vocab)


def main(argv: Sequence[str] | None = None) -> None:
    logging.basicConfig(level=logging.INFO)
    pretty_logger.MakeRootLogPretty()

    parser = argparse.ArgumentParser(
        description="Build list of schema.org terms."
    )
    parser.add_argument(
        "-t",
        "--tagtype",
        action="store_true",
        help="Add a termtype to name",
    )
    parser.add_argument("-o", "--output", required=True, help="output file")
    args = parser.parse_args(argv)

    catalog = _load_default_catalog(InputLayout(constants.PROJECT_ROOT))
    ExportTermListTask(
        catalog=catalog,
        include_tags=bool(args.tagtype),
        output_path=Path(args.output),
        progress=LogProgressReporter(logger=log, log_steps=False),
    ).run()


if __name__ == "__main__":
    main()
