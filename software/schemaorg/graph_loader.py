#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Module providing GraphLoader to load RDF graphs from Schema.org data files."""

import logging
from pathlib import Path
from typing import Sequence

import rdflib

log: logging.Logger = logging.getLogger(__name__)


class GraphLoader:
    """Parses a set of TTL files into a single RDF graph.

    Deliberately knows nothing about layouts, issues or releases: *which*
    files make up a graph is a selection concern, answered by ``Issues`` for
    the source tree and by ``Releases`` for a published release. Those two
    are not symmetric -- the source tree is a union of many files, a release
    is one chosen file -- so the choice is not hidden in here.
    """

    def load(self, files: Sequence[Path]) -> rdflib.Graph:
        """Loads the given TTL files into one graph.

        Namespace bindings are whatever the files themselves declare; none
        are added here.

        Args:
            files: The turtle files to parse, in order.

        Returns:
            A graph holding the union of all triples.
        """
        graph = rdflib.Graph(bind_namespaces="core")
        for file_path in files:
            try:
                graph.parse(str(file_path), format="turtle")
            except Exception as e:
                log.warning(f"Error parsing TTL file '{file_path}': {e}")
                raise
        return graph
