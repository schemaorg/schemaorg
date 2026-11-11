#!/usr/bin/env python3
"""QA utility comparing health-lifesci extension terms against v2.2 core."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
import logging
from pathlib import Path

from rdflib import Graph, RDF, RDFS, URIRef

from schemaorg import constants
from schemaorg.sdo_uri import SdoUri


def typesInGraph(g: Graph) -> set[str]:
    """Return canonicalized type URIs defined in `g`."""
    return {
        str(SdoUri(s))
        for s in g.subjects(RDF.type, RDFS.Class)
        if isinstance(s, URIRef)
    }


def propertiesInGraph(g: Graph) -> set[str]:
    """Return canonicalized property URIs defined in `g`."""
    return {
        str(SdoUri(s))
        for s in g.subjects(RDF.type, RDF.Property)
        if isinstance(s, URIRef)
    }


def enumeratedValuesInGraph(g: Graph) -> set[str]:
    """Return canonicalized MedicalEnumeration member URIs defined in `g`."""
    med_enum = SdoUri("MedicalEnumeration")
    enum_classes = {
        s
        for s, o in g.subject_objects(RDFS.subClassOf)
        if isinstance(s, URIRef) and SdoUri(o) == med_enum
    }
    return {
        str(SdoUri(s))
        for enum_cls in enum_classes
        for s in g.subjects(RDF.type, enum_cls)
        if isinstance(s, URIRef)
    }


def main(argv: Sequence[str] | None = None) -> None:
    # v2.2 predates HTTPS; suppress per-URI upgrade chatter from SdoUri.
    logging.getLogger("schemaorg.sdo_uri").setLevel(logging.ERROR)

    default_health = (
        constants.PROJECT_ROOT / "data/ext/health-lifesci/med-health-core.ttl"
    )
    default_core = constants.PROJECT_ROOT / "data/releases/2.2/schema.nt"

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--health",
        type=Path,
        default=default_health,
        help="Path to health-lifesci RDF file",
    )
    parser.add_argument(
        "--core",
        type=Path,
        default=default_core,
        help="Path to v2.2 core RDF file",
    )
    args = parser.parse_args(argv)

    newhealth_g = Graph().parse(args.health)
    sdo_corev22_g = Graph().parse(args.core)

    new_health_types = typesInGraph(newhealth_g)
    new_health_props = propertiesInGraph(newhealth_g)
    new_health_enumvals = enumeratedValuesInGraph(newhealth_g)
    core_types = typesInGraph(sdo_corev22_g)
    core_props = propertiesInGraph(sdo_corev22_g)
    core_enumvals = enumeratedValuesInGraph(sdo_corev22_g)

    print("Comparing ext/health-lifesci and v2.2 core.\n")
    print(
        f"Types — shared: {len(core_types & new_health_types)}, "
        f"health-only: {len(new_health_types - core_types)}, "
        f"core-only: {len(core_types - new_health_types)}"
    )
    print(
        f"MedicalEnumeration values — shared: {len(core_enumvals & new_health_enumvals)}, "
        f"health-only: {len(new_health_enumvals - core_enumvals)}, "
        f"core-only: {len(core_enumvals - new_health_enumvals)}\n"
    )
    print(
        "Property terms in both 2.2 core and ext/health-lifesci: "
        f"{sorted(core_props & new_health_props)}\n"
    )
    print(
        "Property terms in ext/health-lifesci but not 2.2 core: "
        f"{sorted(new_health_props - core_props)}\n"
    )
    print(
        "Property terms in 2.2 core but not ext/health-lifesci: "
        f"{sorted(core_props - new_health_props)}"
    )


if __name__ == "__main__":
    main()
