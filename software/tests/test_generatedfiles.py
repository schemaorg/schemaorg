#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import List
import unittest

import util.paths as paths


class BasicFileTests(unittest.TestCase):
    """Basic tests for file level integrity."""

    # Source example files only. Release archives under data/releases/ are
    # deliberately excluded: they are frozen historical artefacts and the
    # older ones legitimately predate the https migration.
    EXAMPLE_GLOBS: List[str] = ["*example*.txt", "ext/*/*example*.txt"]

    HTTP_SCHEMA_ORG: str = "http://schema.org"

    def testNoHttpExamples(self):
        """Examples must use https://schema.org, never http://schema.org."""
        layout = paths.DefaultInputLayout()
        files = layout.domain_files(paths.Domain.DATA, self.EXAMPLE_GLOBS)

        # A glob that matches nothing would make this test pass for the most
        # boring of reasons, so assert we actually looked at something.
        self.assertTrue(
            files, f"No example files matched {self.EXAMPLE_GLOBS} under "
                   f"{layout.domain_dir(paths.Domain.DATA)}"
        )

        offenders: List[str] = []
        for path in files:
            lines = path.read_text(encoding="utf-8").splitlines()
            for number, line in enumerate(lines, start=1):
                if self.HTTP_SCHEMA_ORG in line:
                    offenders.append(
                        f"  {layout.relative(path)}:{number}: {line.strip()}"
                    )

        if offenders:
            self.fail(
                f"{len(offenders)} line(s) in the example files reference "
                f"'{self.HTTP_SCHEMA_ORG}'. Replace them with "
                f"'https://schema.org' and rerun:\n" + "\n".join(offenders)
            )
