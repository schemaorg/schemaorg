#!/usr/bin/env python
# -*- coding: utf-8 -*-

from rdflib import Graph, URIRef
from rdflib import RDF, RDFS

# On-off utility to help QA the migration of terms from core (v2.2)
# into health-lifesci hosted extension (v2.3 anticipated). Specifically,
# we want to check which terms in the extension existed previously.


def typesInGraph(g):
    """terms that are defined as types, stringified."""
    _types = []
    for s, p, o in g.triples((None, RDF.type, RDFS.Class)):
        if s not in _types:
            _types.append(str(s))
    return _types


def propertiesInGraph(g):
    """terms that are defined as properties, stringified."""
    _terms = []
    for s, p, o in g.triples((None, RDF.type, RDF.Property)):
        if s not in _terms:
            _terms.append(str(s))
    return _terms


def enumeratedValuesInGraph(g):
    """terms that are defined as enumerated values, stringified."""
    med_enumeration = URIRef("http://schema.org/MedicalEnumeration")
    _enums = []
    _terms = []
    for s, p, o in g.triples((None, RDFS.subClassOf, med_enumeration)):
        if s not in _enums:
            _enums.append(s)
    # print "Enumeration types are:"
    for e in _enums:
        # print "EnumType: ", e
        for s, p, o in g.triples((None, RDF.type, e)):
            # print "instance: ", s
            _terms.append(str(s))
    return _terms


if __name__ == "__main__":
    # we'll work with simple string URIs to keep a clear notion of identity.

    # relative to scripts/ directory.
    #    med_rdfa = '../data/ext/health-lifesci/health_core-0.3.rdfa'
    med_rdfa = "../data/ext/health-lifesci/med-health-core.rdfa"  # ignores activities .rdfa file in same dir
    sdo_core_rdfa = "../data/releases/2.2/schema.rdfa"

    newhealth_g = Graph()
    sdo_corev22_g = Graph()
    parse_errors = Graph()  # re-used for all files now

    # load RDFa/RDFS from disk.
    newhealth_g.parse(med_rdfa, format="rdfa", pgraph=parse_errors)  # , charset="utf8")
    sdo_corev22_g.parse(
        sdo_core_rdfa, format="rdfa", pgraph=parse_errors
    )  # , charset="utf8")

    # get term lists from loaded data
    new_health_types = set(typesInGraph(newhealth_g))
    new_health_props = set(propertiesInGraph(newhealth_g))
    new_health_enumvals = set(enumeratedValuesInGraph(newhealth_g))
    core_types = set(typesInGraph(sdo_corev22_g))
    core_props = set(propertiesInGraph(sdo_corev22_g))
    core_enumvals = set(enumeratedValuesInGraph(sdo_corev22_g))

    print("Comparing ext/health-lifesci and v2.2 core.\n\n")
    #    print "Type terms that are in 2.2 core and 2.3 ext/health-lifesci: %s \n\n" % core_types.intersection(new_health_types)
    #    print "Type terms in the ext/health-lifesci but not 2.2 core: %s \n\n" % new_health_types.difference(core_types)
    print("\n\n")

    print(
        "Property terms that are in 2.2 core and 2.3 ext/health-lifesci: %s \n\n"
        % core_props.intersection(new_health_props)
    )
    print(
        "Property terms in the ext/health-lifesci but not 2.2 core: %s \n\n"
        % new_health_props.difference(core_props)
    )
    print(
        "Property terms in 2.2 core but not in ext/health-lifesci: %s \n\n"
        % core_props.difference(new_health_props)
    )
    print("\n\n")

    #    print "Enumuerated Value terms that are in 2.2 core and 2.3 ext/health-lifesci: %s \n\n" % core_enumvals.intersection(new_health_enumvals)
    #    print "Enumerated Value in the ext/health-lifesci but not 2.2 core: %s \n\n" % new_health_enumvals.difference(new_health_enumvals)
    print("\n\n")

    # print sdo_corev22_g.serialize(format="nt", encoding="utf-8")

# note: breastfeedingWarning was dropped between 2.2 and 3.0 ext
