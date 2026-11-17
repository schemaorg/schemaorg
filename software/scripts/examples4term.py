#!/usr/bin/env python3
"""Export a CSV summary of examples linked to one or more schema.org terms."""

from __future__ import annotations

import argparse
from collections.abc import Iterable, Sequence
import csv
from pathlib import Path

from rdflib import URIRef

from schemaorg import constants
from schemaorg.graph_loader import GraphLoader
from schemaorg.layout import InputLayout, Issues
from schemaorg.model import Vocabulary, VocabularyLoader
from schemaorg.sdo_uri import SdoUri
from SchemaExamples.schemaexamples import Example, SchemaExamples


def _load_default_vocab() -> tuple[int, Vocabulary]:
    files = Issues(InputLayout(constants.PROJECT_ROOT)).get_ttl_files()
    graph = GraphLoader.load(files)
    return len(graph), VocabularyLoader(graph).load()


def _add_subterms(
    vocab: Vocabulary, uri: URIRef, seen: set[str], result: list[str]
) -> None:
    for sub_uri in vocab.subs.get(uri, ()):
        sub_id = SdoUri(sub_uri).term_name()
        if sub_id not in seen:
            seen.add(sub_id)
            result.append(sub_id)
        if vocab.term(sub_uri) is not None:
            _add_subterms(vocab, sub_uri, seen, result)


def getterms(
    terms: Iterable[str],
    recursive: bool,
    vocab: Vocabulary | None = None,
) -> list[str]:
    loaded = vocab if vocab is not None else _load_default_vocab()[1]
    result: list[str] = []
    seen: set[str] = set()

    for term_name in terms:
        term = loaded.term(term_name)
        if term is None:
            print(f"No such term: {term_name}")
            continue
        if term.id not in seen:
            seen.add(term.id)
            result.append(term.id)
        if recursive:
            _add_subterms(loaded, term.uri, seen, result)

    return result


def getexamples(
    terms: Iterable[str],
    examples: SchemaExamples | None = None,
) -> list[Example]:
    loaded = examples if examples is not None else SchemaExamples.from_default()
    return sorted(
        {e for t in terms for e in loaded.examplesForTerm(t)},
        key=lambda e: e.keyvalue,
    )


def buildcsvoutput(examples: Iterable[Example], fname: str | Path) -> None:
    output_path = Path(fname)
    if output_path.suffix != ".csv":
        output_path = output_path.with_name(f"{output_path.name}.csv")

    fields = ["Example Id", "Source File", "Linked to Terms"]
    rows = [
        {
            "Example Id": e.keyvalue,
            "Source File": e.getMeta("source"),
            "Linked to Terms": ", ".join(e.terms),
        }
        for e in examples
    ]

    print(f"examples4term: Writing to: {output_path}")
    with output_path.open("w", encoding="utf-8", newline="") as csvfile:
        writer = csv.DictWriter(
            csvfile, fieldnames=fields, quoting=csv.QUOTE_ALL, lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def main(argv: Sequence[str] | None = None) -> None:
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

    print("Loading triples files")
    triple_count, vocab = _load_default_vocab()
    print(f"loaded {triple_count} triples - {len(vocab.all_terms())} terms")

    terms = getterms(args.term, args.recursive, vocab=vocab)
    examples = getexamples(terms)
    buildcsvoutput(examples, args.output)


if __name__ == "__main__":
    main()
