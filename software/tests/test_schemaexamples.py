#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import SchemaExamples.schemaexamples as schemaexamples
from util.paths import InputLayout


THING_EXAMPLE = """TYPES: #eg-0999 Thing

PRE-MARKUP:
<p>This is a thing</p>

MICRODATA:
<p itemscope itemtype="https://schema.org/Thing">This is a thing</p>

RDFA:
<p vocab="https://schema.org/" typeof="Thing">This is a thing</p>

JSON:

{"@context": "https://schema.org/", "@type": "Thing", }

"""


class TestExampleFileParser(unittest.TestCase):
    """Test the example file parser logic."""

    def setUp(self):
        self.parser = schemaexamples.ExampleFileParser()
        self.temp_file = tempfile.NamedTemporaryFile()
        patcher = patch('SchemaExamples.schemaexamples.paths.DefaultInputLayout')
        mock_input_layout = patcher.start()
        mock_input_layout.return_value = InputLayout(Path(self.temp_file.name).parent)
        self.addCleanup(patcher.stop)

    def test_empty_example(self):
        """An empty example file holds no examples."""
        self.assertEqual(self.parser.parse(self.temp_file.name), [])

    def test_example_without_identifier_is_rejected(self):
        self.temp_file.write(THING_EXAMPLE.replace("#eg-0999 ", "").encode("utf8"))
        self.temp_file.seek(0)
        with self.assertRaisesRegex(ValueError, "Example 1 in file .* has no identifier"):
            self.parser.parse(self.temp_file.name)

    def test_duplicate_identifier_is_rejected(self):
        self.temp_file.write(THING_EXAMPLE.encode("utf8") + b"\n" + THING_EXAMPLE.encode("utf8"))
        self.temp_file.seek(0)
        with self.assertRaisesRegex(ValueError, "Example 2 in file .* has duplicate identifier: 'eg-0999'"):
            self.parser.parse(self.temp_file.name)

    def test_single_example(self):
        """Test parsing of an Example file containing a single entry."""
        self.temp_file.write(THING_EXAMPLE.encode("utf8"))
        self.temp_file.seek(0)
        result = self.parser.parse(self.temp_file.name)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].getIdNum(), 999)
        self.assertEqual(result[0].getMeta("file"), Path(self.temp_file.name).name)
        self.assertCountEqual(result[0].terms, ["Thing"])
        self.assertEqual(
            result[0].getHtml().strip(), "<p>This is a thing</p>", result[0].serialize()
        )
        self.assertEqual(
            result[0].getMicrodata().strip(),
            '<p itemscope itemtype="https://schema.org/Thing">This is a thing</p>',
            result[0].serialize(),
        )
        self.assertEqual(
            result[0].getRdfa().strip(),
            '<p vocab="https://schema.org/" typeof="Thing">This is a thing</p>',
            result[0].serialize(),
        )
        self.assertEqual(
            result[0].getJsonld().strip(),
            '{"@context": "https://schema.org/", "@type": "Thing", }',
            result[0].serialize(),
        )

    def test_two_examples(self):
        """Test parsing of an Example file containing two entries, one of them synthesized."""
        # Write one example
        self.temp_file.write(THING_EXAMPLE.encode("utf8"))
        self.temp_file.write("\n".encode("utf8"))
        # Create a test example object.
        example = schemaexamples.Example(
            terms=["Offer"],
            original_html="<b>Offer</b>",
            microdata="",
            rdfa="",
            jsonld="",
            exmeta={"id": "eg-777", "file": "/bogus", "filepos": -1},
        )
        # Serialize it into second position.
        self.temp_file.write(example.serialize().encode("utf8"))
        self.temp_file.seek(0)
        # Try reading both.
        result = self.parser.parse(self.temp_file.name)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].getIdNum(), 999)
        self.assertCountEqual(result[0].terms, ["Thing"])
        self.assertEqual(result[1].getIdNum(), 777)
        self.assertCountEqual(result[1].terms, ["Offer"])

    def test_serialize(self):
        example = schemaexamples.Example(
            terms=["Thing"],
            original_html="<b>Thing</b>",
            microdata="<b>Thing</b>",
            rdfa="",
            jsonld="<script>{}</script>",
            exmeta={"id": "eg-999", "file": "/bogus", "filepos": -1},
        )
        self.assertEqual(
            example.serialize(),
            """TYPES: #eg-0999 Thing

PRE-MARKUP:
<b>Thing</b>
MICRODATA:
<b>Thing</b>
RDFA:

JSON:
<script>{}</script>""",
        )

    def test_authored_ids_are_kept_as_is(self):
        self.temp_file.write(
            THING_EXAMPLE.replace("#eg-0999", "#eg-3617a").encode("utf8")
            + b"\n"
            + THING_EXAMPLE.replace("#eg-0999", "#3548").encode("utf8")
            + b"\n"
            + THING_EXAMPLE.replace("#eg-0999", "#eg-464").encode("utf8")
        )
        self.temp_file.seek(0)
        result = self.parser.parse(self.temp_file.name)
        self.assertEqual([ex.keyvalue for ex in result], ["eg-3617a", "3548", "eg-0464"])
        self.assertEqual([ex.getIdNum() for ex in result], [-1, -1, 464])
        self.assertEqual([ex.getMeta("filepos") for ex in result], [1, 2, 3])
        self.assertIn("TYPES: #eg-3617a Thing", result[0].serialize())

    def test_example_requires_identifier(self):
        with self.assertRaises(ValueError):
            schemaexamples.Example(
                terms=["Thing"], original_html="", microdata="", rdfa="", jsonld="",
                exmeta={"file": "/bogus", "filepos": 1},
            )


class TestSchemaExamples(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.root = Path(self.temp_dir.name)
        patcher = patch("SchemaExamples.schemaexamples.paths.DefaultInputLayout")
        mock_input_layout = patcher.start()
        mock_input_layout.return_value = InputLayout(self.root)
        self.addCleanup(patcher.stop)

    def _write(self, name: str, content: str) -> Path:
        path = self.root / name
        path.write_text(content, encoding="utf-8")
        return path

    def test_empty(self):
        examples = schemaexamples.SchemaExamples.from_files([])
        self.assertEqual(len(examples), 0)
        self.assertEqual(list(examples.allExamples()), [])
        self.assertEqual(examples.examplesForTerm("Thing"), [])

    def test_from_files_indexes_by_term_and_sorts(self):
        f_b = self._write(
            "b-examples.txt",
            THING_EXAMPLE.replace("#eg-0999 Thing", "#eg-0020 Thing, Offer")
            + "\n"
            + THING_EXAMPLE.replace("#eg-0999 Thing", "#eg-0005 Thing"),
        )
        f_a = self._write(
            "a-examples.txt",
            THING_EXAMPLE.replace("#eg-0999 Thing", "#eg-0010 Offer"),
        )
        examples = schemaexamples.SchemaExamples.from_files([f_b, f_a])

        self.assertEqual(len(examples), 3)
        self.assertEqual(
            [ex.keyvalue for ex in examples.examplesForTerm("Thing")],
            ["eg-0005", "eg-0020"],
        )
        self.assertEqual(
            [ex.keyvalue for ex in examples.examplesForTerm("Offer")],
            ["eg-0010", "eg-0020"],
        )
        self.assertEqual(
            [ex.keyvalue for ex in examples.allExamples()],
            ["eg-0020", "eg-0005", "eg-0010"],
        )

    def test_duplicate_identifier_across_files_is_rejected(self):
        first = self._write("first-examples.txt", THING_EXAMPLE)
        second = self._write("second-examples.txt", THING_EXAMPLE)
        with self.assertRaisesRegex(
            ValueError,
            r"Duplicate example identifier 'eg-0999' in .*second-examples\.txt, "
            r"already defined in .*first-examples\.txt",
        ):
            schemaexamples.SchemaExamples.from_files([first, second])

    def test_instances_are_independent(self):
        first = self._write(
            "first-examples.txt",
            THING_EXAMPLE.replace("#eg-0999 Thing", "#eg-0001 Thing"),
        )
        second = self._write(
            "second-examples.txt",
            THING_EXAMPLE.replace("#eg-0999 Thing", "#eg-0002 Offer"),
        )
        ex_first = schemaexamples.SchemaExamples.from_files([first])
        ex_second = schemaexamples.SchemaExamples.from_files([second])

        self.assertEqual([e.keyvalue for e in ex_first.examplesForTerm("Thing")], ["eg-0001"])
        self.assertEqual(ex_first.examplesForTerm("Offer"), [])
        self.assertEqual([e.keyvalue for e in ex_second.examplesForTerm("Offer")], ["eg-0002"])
        self.assertEqual(ex_second.examplesForTerm("Thing"), [])


if __name__ == "__main__":
    unittest.main()
