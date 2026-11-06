"""Module providing GraphLoader to load RDF graphs from Schema.org data files."""

from collections.abc import Iterable
import logging
from pathlib import Path

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

    @staticmethod
    def load(files: Iterable[Path]) -> rdflib.Graph:
        """Loads the given TTL files into one graph.

        Namespace bindings are whatever the files themselves declare; none
        are added here.
        """
        graph = rdflib.Graph(bind_namespaces="none")
        for file_path in files:
            try:
                graph.parse(file_path, format="turtle")
            except Exception as e:
                log.warning("Error parsing TTL file '%s': %s", file_path, e)
                raise
        return graph
