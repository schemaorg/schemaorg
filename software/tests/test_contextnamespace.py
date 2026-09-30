#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Guards the namespace agreement between the context and the SHACL shapes.

Background
----------
schema.org is https-canonical, but its published JSON-LD context maps every
term into the **http** namespace:

    "@context": { "@vocab": "http://schema.org/", ... }

So an example written as `"@context": "https://schema.org"` expands into
http triples, and the generated SHACL shapes -- which target http class
IRIs -- match them. The whole example-validation gate rests on that
coincidence.

If the context ever starts expanding terms into https while the shapes keep
targeting http, nothing errors. The shapes simply select zero focus nodes,
every example trivially conforms, and the validator prints "All examples
validated successfully" having inspected precisely nothing. A green build,
a useless gate, and no way to tell from the output.

These tests make that divergence loud. They are cheap insurance against the
single failure mode that can render the entire SHACL suite meaningless
without anybody noticing.
"""

import json
import unittest

import rdflib
from rdflib.namespace import SH

import util.paths as paths


class ContextShapesNamespaceTests(unittest.TestCase):
    """The generated context and the generated shapes must agree."""

    CONTEXT_FILENAME = "schemaorgcontext.jsonld"
    SHAPES_FILENAME = "schemaorg-shapes.shacl"

    EXPECTED_VOCAB = "http://schema.org/"

    @classmethod
    def _release_file(cls, filename):
        return paths.DefaultInputLayout().domain_file(
            paths.Domain.RELEASE_DATA, filename
        )

    def _load_vocab(self):
        path = self._release_file(self.CONTEXT_FILENAME)
        if not path.is_file():
            self.skipTest(f"{path} not built")
        with open(path, encoding="utf-8") as handle:
            document = json.load(handle)
        self.assertIn("@context", document, f"{path} has no @context")
        return document["@context"].get("@vocab"), path

    def testContextVocabIsHttp(self):
        """The generated context must expand terms into the http namespace."""
        vocab, path = self._load_vocab()
        self.assertEqual(
            vocab,
            self.EXPECTED_VOCAB,
            f"{path} declares @vocab {vocab!r}, expected "
            f"{self.EXPECTED_VOCAB!r}. The generated SHACL shapes target the "
            "http namespace, so changing this makes every shape match zero "
            "focus nodes and the example validation silently pass without "
            "checking anything.",
        )

    def testShapesTargetTheSameNamespaceAsTheContext(self):
        """schema.org shapes must target the namespace the context expands to.

        This is the assertion that actually matters. The one above pins a
        known-good constant; this one catches the two artifacts drifting
        apart no matter which of them moves.

        Note that a healthy shapes file legitimately targets *foreign*
        vocabularies too -- schema.org references SNOMED CT, IFLA LRM and
        others -- so this deliberately does not demand that every target
        live in the schema.org namespace. What it forbids is the specific
        failure: shapes targeting the http/https *twin* of whatever the
        context expands to. That combination is never intentional, and it
        is exactly what turns the gate into an expensive no-op.
        """
        vocab, _ = self._load_vocab()

        shapes_path = self._release_file(self.SHAPES_FILENAME)
        if not shapes_path.is_file():
            self.skipTest(f"{shapes_path} not built")

        graph = rdflib.Graph()
        graph.parse(source=str(shapes_path), format="turtle")

        targets = {str(t) for t in graph.objects(None, SH.targetClass)}
        self.assertTrue(
            targets,
            f"{shapes_path} declares no sh:targetClass at all, so it can "
            "never select a focus node.",
        )

        if vocab.startswith("http://"):
            twin = "https://" + vocab[len("http://"):]
        else:
            twin = "http://" + vocab[len("https://"):]

        agreeing = sorted(t for t in targets if t.startswith(vocab))
        conflicting = sorted(t for t in targets if t.startswith(twin))

        self.assertFalse(
            conflicting,
            f"{len(conflicting)} sh:targetClass IRIs are in {twin!r} while "
            f"the context expands terms into {vocab!r}. Examples resolve "
            "through the context, so these shapes can never match a focus "
            "node and the validation silently inspects nothing.\n"
            "  sample: " + ", ".join(conflicting[:5]),
        )

        # And the agreement must be substantial, not incidental: if only a
        # handful of shapes line up with the context, the gate is mostly
        # inert even though no single assertion above would complain.
        self.assertGreater(
            len(agreeing),
            len(targets) // 2,
            f"only {len(agreeing)} of {len(targets)} sh:targetClass IRIs are "
            f"in the context namespace {vocab!r}. The shapes and the "
            "examples have drifted apart; most of the corpus is no longer "
            "being inspected.",
        )


if __name__ == "__main__":
    unittest.main()
