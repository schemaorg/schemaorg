#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Backward-compatibility adapter delegating to schemaorg.layout."""

from pathlib import Path

from schemaorg.constants import PROJECT_ROOT
from schemaorg.layout import Domain, InputLayout, OutputLayout
import util.schema as schema


def DefaultInputLayout() -> InputLayout:
    """Returns the default InputLayout instance relative to PROJECT_ROOT."""
    return InputLayout(PROJECT_ROOT)


def DefaultOutputLayout() -> OutputLayout:
    """Returns the default OutputLayout instance relative to schema.config.OUTPUTDIR."""
    return OutputLayout(Path(schema.config.OUTPUTDIR))


__all__ = [
    "Domain",
    "InputLayout",
    "OutputLayout",
    "DefaultInputLayout",
    "DefaultOutputLayout",
]
