"""Floating task that exports a CSV summary of examples linked to terms."""

from __future__ import annotations

from collections.abc import Sequence
import csv
import logging
from pathlib import Path

from rdflib import URIRef

from schemaorg.model import Vocabulary
from schemaorg.progress import ProgressReporter, TaskProgress
from schemaorg.sdo_uri import SdoUri
from SchemaExamples.schemaexamples import Example, SchemaExamples


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


def _resolve_terms(
    vocab: Vocabulary,
    term_names: Sequence[str],
    recursive: bool,
    progress_handle: TaskProgress,
) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()

    for term_name in term_names:
        term = vocab.term(term_name)
        if term is None:
            progress_handle.log(f"No such term: {term_name}", logging.WARNING)
            continue
        if term.id not in seen:
            seen.add(term.id)
            result.append(term.id)
        if recursive:
            _add_subterms(vocab, term.uri, seen, result)

    return result


class ExportTermExamplesTask:
    """Exports a CSV summary of examples linked to one or more terms."""

    def __init__(
        self,
        vocab: Vocabulary,
        examples: SchemaExamples,
        term_names: Sequence[str],
        recursive: bool,
        output_path: Path,
        progress: ProgressReporter,
    ) -> None:
        self.vocab: Vocabulary = vocab
        self.examples: SchemaExamples = examples
        self.term_names: tuple[str, ...] = tuple(term_names)
        self.recursive: bool = recursive
        self.output_path: Path = output_path
        self.progress: ProgressReporter = progress

    def run(self) -> Path:
        target_path = (
            self.output_path
            if self.output_path.suffix == ".csv"
            else self.output_path.with_name(f"{self.output_path.name}.csv")
        )

        with self.progress.task(
            f"Exporting term examples ({target_path.name})",
            total=None,
            unit="examples",
        ) as p:
            p.step("resolving terms")
            resolved_terms = _resolve_terms(
                vocab=self.vocab,
                term_names=self.term_names,
                recursive=self.recursive,
                progress_handle=p,
            )

            p.step("collecting examples")
            matched: list[Example] = sorted(
                {
                    ex
                    for term_id in resolved_terms
                    for ex in self.examples.examplesForTerm(term_id)
                },
                key=lambda ex: ex.keyvalue,
            )

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
                    writer.writerow(
                        {
                            "Example Id": example.keyvalue,
                            "Source File": example.getMeta("source"),
                            "Linked to Terms": ", ".join(example.terms),
                        }
                    )
                    p.advance(1)

        return target_path
