"""Floating tasks that lint, merge, and annotate schema.org Turtle files."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
import tempfile

import rdflib
from rdflib.compare import isomorphic
from rdflib.namespace import RDF, RDFS

from schemaorg.graph_loader import GraphLoader
from schemaorg.progress import ProgressReporter
# shortcut: CustomTurtleSerializer lives in legacy schemaorg.publish until
# tasks-cleanup removes schemaorg/publish/ and inlines it here.
from schemaorg.publish.turtle import CustomTurtleSerializer
from schemaorg.sdo_uri import SDO, SdoUri

VALID_PARTS: tuple[str, ...] = ("pending", "attic", "meta", "GA")


def _graphs_equal(a: rdflib.Graph, b: rdflib.Graph) -> bool:
    if not (a - b) and not (b - a):
        return True
    if any(isinstance(node, rdflib.BNode) for triple in a for node in triple):
        return isomorphic(a, b)
    return False


def _write_turtle_atomic(
    graph: rdflib.Graph,
    target: Path,
    *,
    verify: bool,
    error_message: str = "",
) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            dir=target.parent, delete=False, suffix=".tmp"
        ) as stream:
            tmp_path = Path(stream.name)
            CustomTurtleSerializer(graph).serialize(stream)
        if verify:
            written = GraphLoader.load([tmp_path])
            if not _graphs_equal(graph, written):
                raise ValueError(error_message)
        tmp_path.replace(target)
    except BaseException:
        if tmp_path is not None:
            tmp_path.unlink(missing_ok=True)
        raise


@dataclass(frozen=True)
class LintTurtleTask:
    """Reformats Turtle file(s) deterministically and verifies round-trip parity."""

    files: Sequence[Path]
    output: Path | None
    progress: ProgressReporter

    def __post_init__(self) -> None:
        if not self.files:
            raise ValueError("LintTurtleTask requires at least one file.")
        if self.output is not None and len(self.files) > 1:
            raise ValueError("Cannot use output path with multiple files.")

    def run(self) -> list[Path]:
        written: list[Path] = []
        with self.progress.task(
            "Linting Turtle files",
            total=len(self.files),
            unit="files",
        ) as p:
            for source_path in self.files:
                p.step(source_path.name)
                target_path = (
                    self.output if self.output is not None else source_path
                )
                g = GraphLoader.load([source_path])
                _write_turtle_atomic(
                    g,
                    target_path,
                    verify=True,
                    error_message=f"Linting file {source_path} lost information.",
                )
                written.append(target_path)
                p.advance(1)
        return written


@dataclass(frozen=True)
class MergeTurtleTask:
    """Merges multiple Turtle files into one deterministic Turtle file."""

    files: Sequence[Path]
    output: Path
    progress: ProgressReporter

    def __post_init__(self) -> None:
        if not self.files:
            raise ValueError("MergeTurtleTask requires at least one file.")

    def run(self) -> Path:
        with self.progress.task(
            f"Merging Turtle files ({self.output.name})",
            total=len(self.files),
            unit="files",
        ) as p:
            p.step(self.output.name)
            merged = GraphLoader.load(self.files)
            _write_turtle_atomic(
                merged,
                self.output,
                verify=True,
                error_message=(
                    f"Merging files into {self.output} lost information."
                ),
            )
            p.advance(len(self.files))
        return self.output


@dataclass(frozen=True)
class AnnotateTurtleTask:
    """Sets or clears schema:isPartOf annotations on types and properties."""

    files: Sequence[Path]
    output: Path | None
    part_of: str
    progress: ProgressReporter

    def __post_init__(self) -> None:
        if not self.files:
            raise ValueError("AnnotateTurtleTask requires at least one file.")
        if self.output is not None and len(self.files) > 1:
            raise ValueError("Cannot use output path with multiple files.")
        if self.part_of not in VALID_PARTS:
            raise ValueError(
                f"PartOf annotation {self.part_of!r} is not valid: "
                f"select one of {list(VALID_PARTS)}"
            )

    def run(self) -> list[Path]:
        # GA is the unannotated state.
        new_part: rdflib.URIRef | None = (
            SdoUri.for_layer(self.part_of).uri if self.part_of != "GA" else None
        )
        written: list[Path] = []
        with self.progress.task(
            f"Annotating Turtle files ({self.part_of})",
            total=len(self.files),
            unit="files",
        ) as p:
            for source_path in self.files:
                p.step(source_path.name)
                target_path = (
                    self.output if self.output is not None else source_path
                )
                g = GraphLoader.load([source_path])
                g.remove((None, SDO.isPartOf, None))
                if new_part is not None:
                    for rdf_type in (RDFS.Class, RDF.Property):
                        for sub in g.subjects(RDF.type, rdf_type):
                            g.add((sub, SDO.isPartOf, new_part))
                _write_turtle_atomic(g, target_path, verify=False)
                written.append(target_path)
                p.advance(1)
        return written
