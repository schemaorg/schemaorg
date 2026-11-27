#!/usr/bin/env python3
"""Export a CSV summary of examples linked to one or more schema.org terms."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
import logging
from pathlib import Path

from schemaorg import constants
from schemaorg.graph_loader import GraphLoader
from schemaorg.layout import InputLayout, Issues
from schemaorg.model import VocabularyLoader
from schemaorg.progress import LogProgressReporter
from schemaorg.tasks.export_term_examples import ExportTermExamplesTask
from SchemaExamples.schemaexamples import SchemaExamples

log: logging.Logger = logging.getLogger(__name__)


def main(argv: Sequence[str] | None = None) -> None:
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-t",
        "--term",
        required=True,
        default=[],
        action="extend",
        nargs="+",
        help="Term to use (repeatable)",
    )
    parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="Use term and subtypes",
    )
    parser.add_argument("-o", "--output", required=True, help="CSV output file")
    args = parser.parse_args(argv)

    input_layout = InputLayout(constants.PROJECT_ROOT)
    graph = GraphLoader.load(Issues(input_layout).get_ttl_files())
    vocab = VocabularyLoader(graph).load()
    examples = SchemaExamples.from_layout(input_layout)

    ExportTermExamplesTask(
        vocab=vocab,
        examples=examples,
        term_names=args.term,
        recursive=args.recursive,
        output_path=Path(args.output),
        progress=LogProgressReporter(logger=log, log_steps=False),
    ).run()


if __name__ == "__main__":
    main()
