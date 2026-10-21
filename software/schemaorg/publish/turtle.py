#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Deterministic Turtle serialisation.

rdflib's stock Turtle serialiser orders subjects by reference count, which
is stable for a given graph but says nothing useful to a human reading a
diff. ``CustomTurtleSerializer`` emits classes first, then properties, each
lexicographically sorted, then everything else. That ordering is what makes
the hand-maintained vocabulary files reviewable: a one-term change produces
a one-term diff.

Registration is **explicit**. The previous incarnation of this code called
``register()`` at import time, silently replacing rdflib's global ``turtle``
serialiser for every graph in the process — including graphs that had
nothing to do with schema.org. A caller that wants deterministic Turtle now
says so.
"""

from typing import List

from rdflib import BNode, RDF, RDFS
from rdflib.plugin import register, Serializer
from rdflib.plugins.serializers.turtle import TurtleSerializer
import rdflib.term


class CustomTurtleSerializer(TurtleSerializer):
    """Turtle serialiser with a human-reviewable subject order."""

    topClasses = [RDFS.Class, RDF.Property]

    def orderSubjects(self) -> List[rdflib.term.Node]:
        seen = {}
        subjects = []

        # 1. Process topClasses (Classes and Properties)
        for classURI in self.topClasses:
            members = list(self.store.subjects(RDF.type, classURI))
            members.sort()  # Sort lexicographically
            subjects.extend(members)
            for member in members:
                self._topLevels[member] = True
                seen[member] = True

        # 2. Process everything else (ignoring reference count for sorting)
        recursable = [
            (isinstance(subject, BNode), subject)
            for subject in self._subjects
            if subject not in seen
        ]
        recursable.sort()  # Sort by isbnode, then subject
        subjects.extend([subject for (isbnode, subject) in recursable])

        return subjects


def register_as_turtle() -> None:
    """Makes ``format="turtle"`` deterministic for the whole process.

    This is global and irreversible within a process: it replaces rdflib's
    registered ``turtle`` serialiser. Call it from a CLI entry point, never
    from library code.
    """
    register("turtle", Serializer, __name__, CustomTurtleSerializer.__name__)
