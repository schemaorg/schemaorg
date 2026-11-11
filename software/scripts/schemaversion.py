#!/usr/bin/env python3
"""Print the current schema.org version number."""

from __future__ import annotations

from util.schema import VERSION


def main() -> None:
    print(VERSION.current().number())


if __name__ == "__main__":
    main()
