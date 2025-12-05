#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import collections
import glob
import logging
import os
import rdflib
import sys
import typing
import unittest

# Import schema.org libraries
if not os.getcwd() in sys.path:
    sys.path.insert(1, os.getcwd())

import software
import software.SchemaTerms.sdotermsource as sdotermsource

TYPECOUNT_UPPERBOUND = 1000
TYPECOUNT_LOWERBOUND = 500

log = logging.getLogger(__name__)

VOCABURI = sdotermsource.SdoTermSource.vocabUri()


# Tests to probe the health of both schemas and code using graph libraries in rdflib
# Note that known failings can be annotated with @unittest.expectedFailure or @skip("reason...")
class SDOGraphSetupTestCase(unittest.TestCase):
    @classmethod
    def loadGraphs(self):
        sdotermsource.SdoTermSource.loadSourceGraph("default")
        self.rdflib_data = sdotermsource.SdoTermSource.sourceGraph()

    @classmethod
    def setUpClass(self):
        SDOGraphSetupTestCase.loadGraphs()

    def test_graphsLoaded(self):
        self.assertTrue(
            len(self.rdflib_data) > 0,
            "Graph rdflib_data should have some triples in it.",
        )

    # Supporting functions to streamline tests and make their error
    # messages as informative as possible.
    def getResults(self, query: str, varnames: tuple[str] = ()) -> list[dict]:
        """Runs the SparQL query and returns the results as an array of dict,
           with keys limited to the 'varname' set if provided.
        """
        results = self.rdflib_data.query(query.strip())
        return [dict([(key, row[key])
                      for key in varnames or row.asdict().keys()])
                for row in results]

    @staticmethod
    def formatResults(results, pattern: str = "", varnames: tuple[str] = (),
                      separator: str = " => ", row_separator: str = "\n\t") -> str:
        """Formatting results to make a human-readable list in one step."""
        def formatLines():
            yield f"Found {len(results)} item{'' if len(results)==1 else 's'}:"
            for row in results:
                if pattern:
                    yield pattern % row
                else:
                    yield separator.join([row[key] for key in varnames or row.keys()])

        return row_separator.join(formatLines())


    def assertNoMatch(self, results: typing.Union[str, list[dict]],
                      error_message: str = "List should be empty", row_pattern: str = None):
        if isinstance(results, str):
            # Resolve the SPARQL query into results
            results = self.getResults(results)
        self.assertEqual(
            len(results), 0,
            f"{error_message}! {self.formatResults(results, pattern=row_pattern)}")


    # SPARQLResult http://rdflib.readthedocs.org/en/latest/apidocs/rdflib.plugins.sparql.html
    # "A list of dicts (solution mappings) is returned"

    def test_BaseTypeIsUnique(self):
        a_maps = self.getResults("SELECT ?term ?type WHERE { ?term a ?type . }")
        defined_types = collections.defaultdict(set)

        CLASS = rdflib.term.URIRef('http://www.w3.org/2000/01/rdf-schema#Class')
        DATATYPE = rdflib.term.URIRef('http://www.w3.org/2000/01/rdf-schema#DataType')
        for a in a_maps:
            if a["type"] not in [CLASS, DATATYPE]:
                defined_types[a["term"]].add(a["type"])

        double_bases = filter(lambda x: len(defined_types[x]) > 1, defined_types.keys())

        # Remove the single instance of (known) multiple inheritance.
        double_bases = list(filter(lambda x: x != rdflib.term.URIRef('https://schema.org/Radiography'), double_bases))

        message = '\n' + '\n\t'.join(["%s [%d bases: %s]" % (e, len(defined_types[e]), ", ".join(defined_types[e]))
                                      for e in double_bases])
        self.assertEqual(len(double_bases), 0, f"Types with multiple base types: {message}")


    def test_BaseTypeExists(self):
        a_maps = self.getResults("SELECT ?term ?type WHERE { ?term a ?type . }")
        defined_types = collections.defaultdict(set)
        for a in a_maps:
            defined_types[a["term"]].add(a["type"])
        # Add some well-known types that we accept, and so establish the root of the tree at DATATYPE.
        PROPERTY = rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#Property')
        CLASS = rdflib.term.URIRef('http://www.w3.org/2000/01/rdf-schema#Class')
        DATATYPE = rdflib.term.URIRef('http://www.w3.org/2000/01/rdf-schema#DataType')
        defined_types[CLASS].add(DATATYPE)
        defined_types[PROPERTY].add(DATATYPE)

        def findRoot(t):
            while t in defined_types:
                t = next(iter((defined_types[t])))
            return t

        non_datatype_derived = ["%s => %s" % (k, findRoot(k))
                                for k in filter(lambda x: findRoot(x) != DATATYPE, defined_types.keys())]
        message = '\n' + '\n\t'.join(non_datatype_derived)
        self.assertEqual(len(non_datatype_derived), 0, f"Types that have an invalid base type: {message}")


    def test_foundSixPlusInverseOf(self):
        results = self.getResults(
            "SELECT ?x ?y WHERE { ?x <https://schema.org/inverseOf> ?y }"
        )
        self.assertGreaterEqual(len(results), 6,
                                f"Six or more inverseOf expected. Found: {len(results)}")

    def test_evenNumberOfInverseOf(self):
        results = self.getResults(
            "SELECT ?x ?y WHERE { ?x <https://schema.org/inverseOf> ?y }"
        )
        self.assertTrue(
            len(results) % 2 == 0,
            f"Even number of inverseOf triples expected. Found: {len(results)}")

    def test_noSelfInverseOf(self):
        self.assertNoMatch("""
            SELECT ?x ?y WHERE {
                ?x <https://schema.org/inverseOf> ?y .
                FILTER (?x = ?y) .
            }
        """,
        error_message="inverseOf same property as itself")

    def test_noSelfSupersededBy(self):
        self.assertNoMatch("""
            SELECT ?x ?y WHERE {
                ?x <https://schema.org/supersededBy> ?y .
                FILTER (?x = ?y) .
            }
        """,
        error_message="Type should not be supersededBy itself")

    @unittest.expectedFailure  # autos
    def test_needlessDomainIncludes(self):
        # check immediate subtypes don't declare same domainIncludes
        # TODO: could we use property paths here to be more thorough?
        # rdfs:subClassOf+ should work but seems not to.
        self.assertNoMatch("""
             SELECT ?prop ?c1 ?c2 WHERE {
                 ?prop <https://schema.org/domainIncludes> ?c1 .
                 ?prop <https://schema.org/domainIncludes> ?c2 .
                 ?c1 rdfs:subClassOf ?c2 .

                 FILTER (?c1 != ?c2) .
                 FILTER NOT EXISTS { ?prop <https://schema.org/isPartOf> <http://attic.schema.org> .}
                 FILTER NOT EXISTS { ?c1 <https://schema.org/isPartOf> <http://attic.schema.org> .}
                 FILTER NOT EXISTS { ?c2 <https://schema.org/isPartOf> <http://attic.schema.org> .}
             }
             ORDER BY ?prop
        """,
        error_message="Subtype should not redeclare a domainIncludes of its parents",
        row_pattern="Property %(prop)s defining domain, %(c1)s, [which is subClassOf] %(c2)s unnecessarily")

    @unittest.expectedFailure
    def test_needlessRangeIncludes(self):
        # as above, but for range. We excuse URL as it is special, not best seen as a Text subtype.
        # check immediate subtypes don't declare same domainIncludes
        # TODO: could we use property paths here to be more thorough?
        self.assertNoMatch("""
            SELECT ?prop ?c1 ?c2 WHERE {
                ?prop <https://schema.org/rangeIncludes> ?c1 .
                ?prop <https://schema.org/rangeIncludes> ?c2 .
                ?c1 rdfs:subClassOf ?c2 .

                FILTER (?c1 != ?c2) .
                FILTER (?c1 != <https://schema.org/URL>) .
                FILTER NOT EXISTS { ?prop <https://schema.org/isPartOf> <http://attic.schema.org> .}
                FILTER NOT EXISTS { ?c1 <https://schema.org/isPartOf> <http://attic.schema.org> .}
                FILTER NOT EXISTS { ?c2 <https://schema.org/isPartOf> <http://attic.schema.org> .}
            }
            ORDER BY ?prop
        """,
        error_message="No subtype need redeclare a rangeIncludes of its parents",
        row_pattern="Property %(prop)s defining range, %(c1)s, [which is subclassOf] %(c2)s unnecessarily")

    #  def test_supersededByAreLabelled(self):
    #    supersededByAreLabelled_results = self.rdflib_data.query("select ?x ?y ?z where { ?x <https://schema.org/supersededBy> ?y . ?y <https://schema.org/name> ?z }")
    #    self.assertEqual(len(inverseOf_results ) % 2 == 0, True, "Even number of inverseOf triples expected. Found: %s " % len(inverseOf_results ) )

    def test_validRangeIncludes(self):
        self.assertNoMatch("""
            SELECT ?prop ?c1 WHERE {
                ?prop <https://schema.org/rangeIncludes> ?c1 .
                OPTIONAL {
                    ?c1 rdf:type ?c2 .
                    ?c1 rdf:type rdfs:Class .
                } .

                FILTER (!bound(?c2))
                FILTER NOT EXISTS { ?prop <https://schema.org/isPartOf> <http://attic.schema.org> .}
            }
            ORDER BY ?prop
        """,
        error_message="RangeIncludes should define valid type",
        row_pattern="Property %(prop)s invalid rangeIncludes value: %(c1)s")

    def test_validDomainIncludes(self):
        self.assertNoMatch("""
            SELECT ?prop ?c1 WHERE {
                ?prop <https://schema.org/domainIncludes> ?c1 .
                OPTIONAL {
                    ?c1 rdf:type ?c2 .
                    ?c1 rdf:type rdfs:Class .
                } .

                FILTER (!BOUND(?c2))
                FILTER NOT EXISTS { ?prop <https://schema.org/isPartOf> <http://attic.schema.org> .}
            }
            ORDER BY ?prop
        """,
        error_message="DomainIncludes should define valid type",
        row_pattern="Property %(prop)s invalid domainIncludes value: %(c1)s")


    # @unittest.expectedFailure
    def test_simpleLabels(self):
        self.assertNoMatch("""
            SELECT DISTINCT ?term ?label WHERE {
                ?term rdfs:label ?label
                FILTER REGEX(?label, '[^a-zA-Z0-9_ ]','i') .
            }
            ORDER BY ?term
        """,
        error_message="Some terms have complex labels (alphanumeric only please!)",
        row_pattern="term %(term)s has complex label: %(label)s")
        # Whitespace is tolerated, for now.
        # we don't deal well with non definitional uses of rdfs:label yet - non terms are flagged up.
        # https://github.com/schemaorg/schemaorg/issues/1136

    #
    # TODO: https://github.com/schemaorg/schemaorg/issues/662
    #
    # self.assertEqual(len(ndi1_results), 0, "No domainIncludes or rangeIncludes value should lack a type. Found: %s " % len(ndi1_results ) )

    def test_labelMatchesTermId(self):
        self.assertNoMatch("""
            SELECT ?term ?label WHERE {
                ?term rdfs:label ?label .

                FILTER STRSTARTS(STR(?term), "https://schema.org/")
                FILTER (!STRENDS(STR(?term), STR(?label)))
            }
            ORDER BY ?term
        """,
        error_message="Term should have matching rdfs:label",
        row_pattern="Term '%(term)s' has non-matching label: '%(label)s'")

    def test_superTypesExist(self):
        self.assertNoMatch("""
            SELECT ?term ?super WHERE {
                ?term rdfs:subClassOf ?super .
                ?term rdf:type rdfs:Class .

                FILTER NOT EXISTS { ?super rdf:type rdfs:Class }

                FILTER STRSTARTS(STR(?term), "https://schema.org/")
                FILTER STRSTARTS(STR(?super), "https://schema.org/")

                FILTER NOT EXISTS { ?term <https://schema.org/isPartOf> <http://attic.schema.org> .}
            }
            ORDER BY ?term
            """,
            error_message="Types with nonexistent SuperTypes",
            row_pattern="Term '%(term)s' has nonexistent supertype: '%(super)s'")

    def test_propsWithoutDomain(self):
        self.assertNoMatch("""
            SELECT ?term WHERE {
                ?term a rdf:Property .
                FILTER NOT EXISTS { ?term <https://schema.org/domainIncludes> ?o .}
                FILTER NOT EXISTS { ?term <https://schema.org/supersededBy> ?o .}
            }
            ORDER BY ?term
        """,
        error_message="Property without domain extensions",
        row_pattern="Term '%(term)s' has no domainIncludes values")

    def test_propsWithoutRange(self):
        self.assertNoMatch("""
           SELECT ?term WHERE {
             ?term a rdf:Property .
             FILTER NOT EXISTS { ?term <https://schema.org/rangeIncludes> ?o .}
             FILTER NOT EXISTS { ?term <https://schema.org/supersededBy> ?o .}
           }
           ORDER BY ?term
        """,
        error_message="Property without range extensions",
        row_pattern="Term '%(term)s' has no rangeIncludes values")

    def test_superPropertiesExist(self):
        self.assertNoMatch("""
          SELECT ?term ?super WHERE {
            ?term rdf:type rdf:Property .
            ?term rdfs:subPropertyOf ?super .

            FILTER NOT EXISTS { ?super rdf:type rdf:Property }

            FILTER STRSTARTS(STR(?term), "https://schema.org/")
            FILTER STRSTARTS(STR(?super), "https://schema.org/")

            FILTER NOT EXISTS { ?term <https://schema.org/isPartOf> <http://attic.schema.org> .}
          }
          ORDER BY ?term
        """,
        error_message="Property with non-existent SuperProperties",
        row_pattern="Term '%(term)s' has nonexistent super-property: '%(super)s'")

    def test_selfReferencingInverse(self):
        self.assertNoMatch("""
          SELECT ?term ?inverse WHERE {
            ?term rdf:type rdf:Property .
            ?term <https://schema.org/inverseOf> ?inverse .

            FILTER STRSTARTS(STR(?term), "https://schema.org/")

            FILTER(STR(?term) = STR(?inverse))
            FILTER NOT EXISTS { ?term <https://schema.org/isPartOf> <http://attic.schema.org> .}
          }
          ORDER BY ?term
        """,
        error_message="Types with self-referencing inverseOf",
        row_pattern="Term '%(term)s' is defined as inverseOf self")

    def test_sameInverseAndSupersededByTarget(self):
        self.assertNoMatch("""
          SELECT ?term ?inverse ?super WHERE {
            ?term rdf:type rdf:Property .
            ?term <https://schema.org/inverseOf> ?inverse .
            ?term <https://schema.org/supersededBy> ?super .

            FILTER STRSTARTS(STR(?term), "https://schema.org/")
            FILTER(STR(?inverse) = STR(?super))
            FILTER NOT EXISTS { ?term <https://schema.org/isPartOf> <http://attic.schema.org> .}
          }
          ORDER BY ?term
        """,
        error_message="Types with inverseOf supersededBy shared target",
        row_pattern="Term '%(term)s' defined ase inverseOf AND supersededBy %(inverse)s")

    def test_commentEndWithPeriod(self):
        """Validate that class and property RDF comments end with a punctuation."""
        self.assertNoMatch("""
          SELECT ?term ?com WHERE {
            ?term rdfs:comment ?com .

            FILTER STRSTARTS(STR(?term), "https://schema.org/")
            FILTER (!(REGEX(STR(?com), '[\\\\.\\\\)\\\\?]\\\\s*$') || REGEX(STR(?com), 'n\\\\* .*')))
          }
          ORDER BY ?term
        """,
        error_message="Comment without ending '.', ')' or '?' ")

    def test_typeLabelCase(self):
        self.assertNoMatch("""
          SELECT ?term ?label WHERE {
            ?term rdf:type rdfs:Class .
            ?term rdfs:label ?label .

            FILTER STRSTARTS(STR(?term), "https://schema.org/")
            FILTER (!REGEX(STR(?label), '^[0-9]*[A-Z].*'))
          }
          ORDER BY ?term
        """,
        error_message="Type label does not start with [A-Z] char")

    def test_propertyLabelCase(self):
        self.assertNoMatch("""
          SELECT ?term ?label WHERE {
            ?term rdf:type rdf:Property .
            ?term rdfs:label ?label .

            FILTER STRSTARTS(STR(?term), "https://schema.org/")
            FILTER (!REGEX(STR(?label), '^[0-9]*[a-z].*'))
          }
          ORDER BY ?term
        """,
        error_message="Property label not starting with [a-z] char")

    def test_superTypeInAttic(self):
        self.assertNoMatch("""
          SELECT ?term ?super WHERE {
            {
              ?term rdfs:subClassOf ?super .
            }
            UNION
            {
              ?term rdfs:subPropertyOf ?super .
            }
            ?super <https://schema.org/isPartOf> <http://attic.schema.org> .

            FILTER NOT EXISTS { ?term <https://schema.org/isPartOf> <http://attic.schema.org> .}
          }
          ORDER BY ?term
        """,
        error_message="Super-term in attic!",
        row_pattern="Term '%(term)s' is sub-term of %(super)s a term in attic")

    def test_referenceTermInAttic(self):
        self.assertNoMatch("""
          SELECT ?term ?rel ?ref WHERE {
            {
                ?term <https://schema.org/domainIncludes> ?ref .
                ?term ?rel ?ref.
            }
            UNION
            {
                ?term <https://schema.org/rangeIncludes> ?ref .
                ?term ?rel ?ref.
            }
            UNION
            {
                ?term <https://schema.org/inverseOf> ?ref .
                ?term ?rel ?ref.
            }
            UNION
            {
                ?term <https://schema.org/supersededBy> ?ref .
                ?term ?rel ?ref.
            }
            ?ref <https://schema.org/isPartOf> <http://attic.schema.org> .

            FILTER NOT EXISTS { ?term <https://schema.org/isPartOf> <http://attic.schema.org> .}
          }
          ORDER BY ?term
        """,
        error_message="Reference to attic term!",
        row_pattern="Term '%(term)s' makes a %(rel)s reference to %(ref)s, a term in attic")

    def test_termIn2PlusExtensions(self):
        self.assertNoMatch("""
          SELECT ?term (COUNT(?part) as ?count) WHERE {
            ?term <https://schema.org/isPartOf> ?part .
          }
          GROUP BY ?term
          HAVING (COUNT(?part) > 1)
          ORDER BY ?term
        """,
        error_message="Term partOf multiple extensions",
        row_pattern="Term %(term)s isPartOf %(count)s extensions")

    def test_termIsHttps(self):
        self.assertNoMatch("""
          SELECT DISTINCT ?term WHERE {
            ?term ?p ?o .

            FILTER STRSTARTS(STR(?term), "http://schema.org")
          }
          ORDER BY ?term
        """,
        error_message="Term defined as http instead of https")

    def test_targetNotHttps(self):
        self.assertNoMatch("""
          PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
          PREFIX schema: <https://schema.org/>

          SELECT ?term ?target WHERE {
            ?term schema:domainIncludes |
                  schema:rangeIncludes |
                  rdfs:subClassOf |
                  rdfs:subPropertyOf |
                  schema:supersededBy |
                  schema:inverseOf          ?target .
            FILTER STRSTARTS(STR(?target), "http://schema.org")
          }
          ORDER BY ?term
        """,
        error_message="Term not defined as https://",
        row_pattern="Term '%(term)s' references term %(target)s as https")

    def test_isPartOf(self):
        self.assertNoMatch("""
          PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
          PREFIX schema: <https://schema.org/>

          SELECT ?term ?partof WHERE {
            ?term schema:isPartOf ?partof .
            MINUS {
              ?term schema:isPartOf <https://attic.schema.org>
            }
            MINUS {
              ?term schema:isPartOf <https://auto.schema.org>
            }
            MINUS {
              ?term schema:isPartOf <https://bib.schema.org>
            }
            MINUS {
              ?term schema:isPartOf <https://health-lifesci.schema.org>
            }
            MINUS {
              ?term schema:isPartOf <https://meta.schema.org>
            }
            MINUS {
              ?term schema:isPartOf <https://pending.schema.org>
            }
          }
          ORDER BY ?term
        """,
        error_message="Invalid isPartOf value errors",
        row_pattern="Term '%(term)s' has invalid isPartOf value '%(partof)s'")

    @unittest.expectedFailure
    def test_EnumerationWithoutEnums(self):
        self.assertNoMatch("""
          SELECT ?term WHERE {
              ?term a rdfs:subClassOf+ <https://schema.org/Enumeration> .

              FILTER NOT EXISTS { ?enum a ?term .}
              FILTER NOT EXISTS { ?term <https://schema.org/isPartOf> <http://attic.schema.org> .}
          }
          ORDER BY ?term
        """,
        error_message="Enumeration Type without Enumeration value")

    def test_illegalOwlClassPropertyMixup(self):
        self.assertNoMatch("""
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        SELECT ?term ?equivType WHERE {
            ?term owl:equivalentClass ?equivType .
            ?term owl:equivalentProperty ?equivType .
          }
          ORDER BY ?term
        """,
        error_message="Equivalence cannot hold for both Class and Property!",
        row_pattern="Term '%(term)s' is both equivalent Class and Property of %(equivType)s")

        self.assertNoMatch("""
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        SELECT ?cls ?prop ?equivType WHERE {
            ?cls owl:equivalentClass ?equivType .
            ?prop owl:equivalentProperty ?equivType .
          }
          ORDER BY ?cls
        """,
        error_message="A type cannot be both equivalentClass and equivalentProperty!",
        row_pattern="Type '%(equivType)s' cannot be both an equivalent Class (with %(cls)s) and Property of (with %(prop)s)")

    def test_properClassPropertyStructuring(self):
        self.assertNoMatch("""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
         PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
         PREFIX owl: <http://www.w3.org/2002/07/owl#>

         SELECT ?term ?predicate ?target WHERE {
           # Define the combinations of type and predicate to look for
           VALUES (?type ?predicate) {
             (rdfs:Class    rdfs:subPropertyOf)
             (rdfs:Class    owl:equivalentProperty)
             (rdfs:Property rdfs:subClassOf)
             (rdfs:Property owl:equivalentClass)
           }

           {
             # ?term must be of the right type for the predicate
             ?term a ?type .
             ?term ?predicate ?target .
           }
           UNION
           {
             # ?target must be of the right type for the predicate
             ?target a ?type .
             ?term ?predicate ?target .
           }
         } ORDER BY ?term
        """,
        error_message="A type cannot be a Class (Property) and also be a subPropertyOf (subClassOf) or something!",
        row_pattern="'%(term)s' is %(predicate)s of %(target)s")


# TODO: Unwritten tests (from basics; easier here?)
#
# * different terms should not have identical comments
# * rdflib and internal parsers should have same number of triples
# * if x and y are inverseOf each other, the rangeIncludes types on x should be domainIncludes on y, and vice-versa.
# * need a few supporting functions e.g. all terms, all types, all properties, all enum values; candidates for api later but just use here first.

if __name__ == "__main__":
    unittest.main()
