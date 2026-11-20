"""Examples text-bundle renderer."""

from __future__ import annotations

from collections.abc import Sequence
import logging
from pathlib import Path

import SchemaExamples.schemaexamples as schemaexamples

log: logging.Logger = logging.getLogger(__name__)


def render_examples(example_files: Sequence[Path]) -> str:
    """Concatenate all parsed examples into one release text bundle."""
    if not example_files:
        log.warning("No example files given; writing an empty examples file")
        return ""
    loaded = schemaexamples.SchemaExamples.from_files(example_files)
    return "\n".join(ex.serialize() for ex in loaded.allExamples())
