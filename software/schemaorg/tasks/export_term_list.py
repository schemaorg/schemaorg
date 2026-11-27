"""Floating task that exports a flat or type-tagged list of schema.org terms."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

from schemaorg.progress import ProgressReporter
from schemaorg.term_view import TermKind, TermViewCatalog

_TERM_TAGS: dict[TermKind, str] = {
    TermKind.PROPERTY: " p",
    TermKind.TYPE: " t",
    TermKind.DATATYPE: " d",
    TermKind.ENUMERATION: " e",
    TermKind.ENUMERATIONVALUE: " v",
}


def format_term_lines(
    catalog: TermViewCatalog, include_tags: bool
) -> Iterator[str]:
    for term in catalog.all_views():
        suffix = _TERM_TAGS.get(term.termType, "") if include_tags else ""
        yield f"{term.id}{suffix}\n"


@dataclass(frozen=True)
class ExportTermListTask:
    """Writes a sorted list of schema.org term IDs (optionally tagged by kind)."""

    catalog: TermViewCatalog
    include_tags: bool
    output_path: Path
    progress: ProgressReporter

    def run(self) -> Path:
        lines = list(format_term_lines(self.catalog, self.include_tags))
        with self.progress.task(
            f"Writing term list ({self.output_path.name})",
            total=len(lines),
            unit="terms",
        ) as p:
            p.step(self.output_path.name)
            self.output_path.parent.mkdir(parents=True, exist_ok=True)
            self.output_path.write_text("".join(lines), encoding="utf-8")
            p.advance(len(lines))
        return self.output_path
