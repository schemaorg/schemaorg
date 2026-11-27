"""Floating task that exports a CSV summary of examples linked to terms."""

from __future__ import annotations

from collections.abc import Sequence
import csv
from dataclasses import dataclass
import logging
from pathlib import Path

from rdflib import URIRef

from schemaorg.model import Vocabulary
from schemaorg.progress import ProgressReporter
from schemaorg.sdo_uri import SdoUri
from SchemaExamples.schemaexamples import Example, SchemaExamples


def _resolve_terms(
    vocab: Vocabulary,
    term_names: Sequence[str],
    recursive: bool,
) -> tuple[set[str], list[str]]:
    seen: set[str] = set()
    missing: list[str] = []
    stack: list[URIRef] = []

    for term_name in term_names:
        term = vocab.term(term_name)
        if term is None:
            missing.append(term_name)
            continue
        if term.id not in seen:
            seen.add(term.id)
            if recursive:
                stack.append(term.uri)

    while stack:
        uri = stack.pop()
        for sub_uri in vocab.subs.get(uri, ()):
            sub_id = SdoUri(sub_uri).term_name()
            if sub_id not in seen:
                seen.add(sub_id)
                stack.append(sub_uri)

    return seen, missing


@dataclass(frozen=True)
class ExportTermExamplesTask:
    """Exports a CSV summary of examples linked to one or more terms."""

    vocab: Vocabulary
    examples: SchemaExamples
    term_names: Sequence[str]
    recursive: bool
    output_path: Path
    progress: ProgressReporter

    def run(self) -> Path:
        target_path = (
            self.output_path
            if self.output_path.suffix == ".csv"
            else self.output_path.with_name(f"{self.output_path.name}.csv")
        )
        resolved_terms, missing_terms = _resolve_terms(
            vocab=self.vocab,
            term_names=self.term_names,
            recursive=self.recursive,
        )
        matched: list[Example] = sorted(
            {
                ex
                for term_id in resolved_terms
                for ex in self.examples.examplesForTerm(term_id)
            },
            key=lambda ex: ex.keyvalue,
        )

        with self.progress.task(
            f"Exporting term examples ({target_path.name})",
            total=len(matched),
            unit="examples",
        ) as p:
            for term_name in missing_terms:
                p.log(f"No such term: {term_name}", logging.WARNING)

            p.step(target_path.name)
            fields = ["Example Id", "Source File", "Linked to Terms"]
            target_path.parent.mkdir(parents=True, exist_ok=True)
            with target_path.open("w", encoding="utf-8", newline="") as csvfile:
                writer = csv.DictWriter(
                    csvfile,
                    fieldnames=fields,
                    quoting=csv.QUOTE_ALL,
                    lineterminator="\n",
                )
                writer.writeheader()
                for example in matched:
                    writer.writerow({
                        "Example Id": example.keyvalue,
                        "Source File": example.getMeta("source"),
                        "Linked to Terms": ", ".join(example.terms),
                    })
                    p.advance(1)

        return target_path
