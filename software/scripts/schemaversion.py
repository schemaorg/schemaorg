#!/usr/bin/env python3
"""Print the current schema.org version number."""

from __future__ import annotations

from util.schema import VERSION


if __name__ == "__main__":
    print(VERSION.current().number())
