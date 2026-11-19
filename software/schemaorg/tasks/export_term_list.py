"""Floating task that exports a flat or type-tagged list of schema.org terms."""

from __future__ import annotations

from collections.abc import Iterator
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


class ExportTermListTask:
    """Writes a sorted list of schema.org term IDs (optionally tagged by kind)."""

    def __init__(
        self,
        catalog: TermViewCatalog,
        include_tags: bool,
        output_path: Path,
        progress: ProgressReporter,
    ) -> None:
        self.catalog: TermViewCatalog = catalog
        self.include_tags: bool = include_tags
        self.output_path: Path = output_path
        self.progress: ProgressReporter = progress

    def run(self) -> Path:
        views = self.catalog.all_views()
        with self.progress.task(
            f"Writing term list ({self.output_path.name})",
            total=len(views),
            unit="terms",
        ) as p:
            p.step(self.output_path.name)
            lines: list[str] = []
            for term in views:
                suffix = (
                    _TERM_TAGS.get(term.termType, "")
                    if self.include_tags
                    else ""
                )
                lines.append(f"{term.id}{suffix}\n")
                p.advance(1)
            self.output_path.parent.mkdir(parents=True, exist_ok=True)
            self.output_path.write_text("".join(lines), encoding="utf-8")
        return self.output_path
