#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import sys
import os
import logging
import glob
import sys
import unittest
import rdflib

# Import schema.org libraries
if not os.getcwd() in sys.path:
    sys.path.insert(1, os.getcwd())

import software

import software.SchemaTerms.sdotermsource as sdotermsource

warnings = []

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

    # SPARQLResult http://rdflib.readthedocs.org/en/latest/apidocs/rdflib.plugins.sparql.html
    # "A list of dicts (solution mappings) is returned"

    def test_found_sixplus_inverseOf(self):
        inverseOf_results = self.rdflib_data.query(
            "select ?x ?y where { ?x <https://schema.org/inverseOf> ?y }"
        )
        log.info("inverseOf result count: %s" % len(inverseOf_results))
        self.assertTrue(
            len(inverseOf_results) >= 6,
            "Six or more inverseOf expected. Found: %s " % len(inverseOf_results),
        )

    def test_even_number_inverseOf(self):
        inverseOf_results = self.rdflib_data.query(
            "select ?x ?y where { ?x <https://schema.org/inverseOf> ?y }"
        )
        self.assertTrue(
            len(inverseOf_results) % 2 == 0,
            "Even number of inverseOf triples expected. Found: %s "
            % len(inverseOf_results),
        )

    def test_non_equal_inverseOf(self):
        results = self.rdflib_data.query(
            "select ?x ?y where { ?x <https://schema.org/inverseOf> ?y }"
        )
        for result in results:
            self.assertTrue(
                result[0] != result[1],
                "%s should not be equal to %s" % (result[0], result[1]),
            )

    def test_non_equal_supercededBy(self):
        results = self.rdflib_data.query(
            "select ?x ?y where { ?x <https://schema.org/supercededBy> ?y }"
        )
        for result in results:
            self.assertTrue(
                result[0] != result[1],
                "%s should not be equal to %s" % (result[0], result[1]),
            )

    @unittest.expectedFailure  # autos
    def test_needlessDomainIncludes(self):
        global warnings
        # check immediate subtypes don't declare same domainIncludes
        # TODO: could we use property paths here to be more thorough?
        # rdfs:subClassOf+ should work but seems not to.
        ndi1 = """SELECT ?prop ?c1 ?c2
           WHERE {
           ?prop <https://schema.org/domainIncludes> ?c1 .
           ?prop <https://schema.org/domainIncludes> ?c2 .
           ?c1 rdfs:subClassOf ?c2 .
           FILTER (?c1 != ?c2) .
           FILTER NOT EXISTS { ?prop <https://schema.org/isPartOf> <http://attic.schema.org> .}
           FILTER NOT EXISTS { ?c1 <https://schema.org/isPartOf> <http://attic.schema.org> .}
           FILTER NOT EXISTS { ?c2 <https://schema.org/isPartOf> <http://attic.schema.org> .}
           }
           ORDER BY ?prop """
        ndi1_results = self.rdflib_data.query(ndi1)
        if len(ndi1_results) > 0:
            for row in ndi1_results:
                warn = (
                    "Property %s defining domain, %s, [which is subclassOf] %s unnecessarily"
                    % (row["prop"], row["c1"], row["c2"])
                )
                # warnings.append(warn)
                log.warning(warn)
        self.assertEqual(
            len(ndi1_results),
            0,
            "No subtype need redeclare a domainIncludes of its parents. Found: %s "
            % len(ndi1_results),
        )

    @unittest.expectedFailure
    def test_needlessRangeIncludes(self):
        global warnings
        # as above, but for range. We excuse URL as it is special, not best seen as a Text subtype.
        # check immediate subtypes don't declare same domainIncludes
        # TODO: could we use property paths here to be more thorough?
        nri1 = """SELECT ?prop ?c1 ?c2
         WHERE {
         ?prop <https://schema.org/rangeIncludes> ?c1 .
         ?prop <https://schema.org/rangeIncludes> ?c2 .
         ?c1 rdfs:subClassOf ?c2 .
         FILTER (?c1 != ?c2) .
         FILTER (?c1 != <https://schema.org/URL>) .
         FILTER NOT EXISTS { ?prop <https://schema.org/isPartOf> <http://attic.schema.org> .}
         FILTER NOT EXISTS { ?c1 <https://schema.org/isPartOf> <http://attic.schema.org> .}
         FILTER NOT EXISTS { ?c2 <https://schema.org/isPartOf> <http://attic.schema.org> .}
             }
             ORDER BY ?prop """
        nri1_results = self.rdflib_data.query(nri1)
        if len(nri1_results) > 0:
            for row in nri1_results:
                warn = (
                    "Property %s defining range, %s, [which is subclassOf] %s unnecessarily"
                    % (row["prop"], row["c1"], row["c2"])
                )
                log.warning(warn)
        self.assertEqual(
            len(nri1_results),
            0,
            "No subtype need redeclare a rangeIncludes of its parents. Found: %s"
            % len(nri1_results),
        )

    #  def test_supersededByAreLabelled(self):
    #    supersededByAreLabelled_results = self.rdflib_data.query("select ?x ?y ?z where { ?x <https://schema.org/supersededBy> ?y . ?y <https://schema.org/name> ?z }")
    #    self.assertEqual(len(inverseOf_results ) % 2 == 0, True, "Even number of inverseOf triples expected. Found: %s " % len(inverseOf_results ) )

    def test_validRangeIncludes(self):
        nri1 = """SELECT ?prop ?c1
     WHERE {
         ?prop <https://schema.org/rangeIncludes> ?c1 .
         OPTIONAL{
            ?c1 rdf:type ?c2 .
            ?c1 rdf:type rdfs:Class .
         }.
         FILTER (!BOUND(?c2))
        FILTER NOT EXISTS { ?prop <https://schema.org/isPartOf> <http://attic.schema.org> .}
                 }
                 ORDER BY ?prop """
        nri1_results = self.rdflib_data.query(nri1)
        for row in nri1_results:
            log.info(
                "Property %s invalid rangeIncludes value: %s\n"
                % (row["prop"], row["c1"])
            )
        self.assertEqual(
            len(nri1_results),
            0,
            "RangeIncludes should define valid type. Found: %s" % len(nri1_results),
        )

    def test_validDomainIncludes(self):
        nri1 = """SELECT ?prop ?c1
     WHERE {
         ?prop <https://schema.org/domainIncludes> ?c1 .
         OPTIONAL{
            ?c1 rdf:type ?c2 .
            ?c1 rdf:type rdfs:Class .
         }.
         FILTER (!BOUND(?c2))
        FILTER NOT EXISTS { ?prop <https://schema.org/isPartOf> <http://attic.schema.org> .}
                 }
                 ORDER BY ?prop """
        nri1_results = self.rdflib_data.query(nri1)
        for row in nri1_results:
            log.info(
                "Property %s invalid domainIncludes value: %s\n"
                % (row["prop"], row["c1"])
            )
        self.assertEqual(
            len(nri1_results),
            0,
            "DomainIncludes should define valid type. Found: %s" % len(nri1_results),
        )

    # These are place-holders for more sophisticated SPARQL-expressed checks.
    @unittest.expectedFailure
    def test_readSchemaFromRDFa(self):
        self.assertTrue(
            True,
            False,
            "We should know how to locally get /docs/schema_org_rdfa.html but this requires fixes to api.py.",
        )

    # @unittest.expectedFailure
    def test_simpleLabels(self):
        s = ""
        complexLabels = self.rdflib_data.query(
            "select distinct ?term ?label where { ?term rdfs:label ?label  FILTER regex(?label,'[^a-zA-Z0-9_ ]','i'). } "
        )
        for row in complexLabels:
            s += " term %s has complex label: %s\n" % (row["term"], row["label"])
        self.assertTrue(
            len(complexLabels) == 0,
            "No complex term labels expected; alphanumeric only please. Found: %s Details: %s\n"
            % (len(complexLabels), s),
        )
        # Whitespace is tolerated, for now.
        # we don't deal well with non definitional uses of rdfs:label yet - non terms are flagged up.
        # https://github.com/schemaorg/schemaorg/issues/1136

    #
    # TODO: https://github.com/schemaorg/schemaorg/issues/662
    #
    # self.assertEqual(len(ndi1_results), 0, "No domainIncludes or rangeIncludes value should lack a type. Found: %s " % len(ndi1_results ) )

    def test_labelMatchesTermId(self):
        nri1 = """select ?term ?label where {
       ?term rdfs:label ?label.
       BIND(STR(?term) AS ?strVal)
       FILTER(STRLEN(?strVal) >= 19 && SUBSTR(?strVal, 1, 19) = "https://schema.org/")
       FILTER(SUBSTR(?strVal, 20) != STR(?label))
    }
    ORDER BY ?term  """
        nri1_results = self.rdflib_data.query(nri1)
        if len(nri1_results):
            log.info("Label matching errors:")
            for row in nri1_results:
                log.info(
                    "Term '%s' has none-matching label: '%s'"
                    % (row["term"], row["label"])
                )
        self.assertEqual(
            len(nri1_results),
            0,
            "Term should have matching rdfs:label. Found: %s" % len(nri1_results),
        )

    def test_superTypesExist(self):
        nri1 = """select ?term ?super where {
       ?term rdfs:subClassOf ?super.
       ?term rdf:type rdfs:Class.
       FILTER NOT EXISTS { ?super rdf:type rdfs:Class }

       BIND(STR(?term) AS ?strVal)
       FILTER(STRLEN(?strVal) >= 19 && SUBSTR(?strVal, 1, 19) = "https://schema.org/")

       BIND(STR(?super) AS ?superStrVal)
       FILTER(STRLEN(?superStrVal) >= 19 && SUBSTR(?superStrVal, 1, 19) = "https://schema.org/")
        FILTER NOT EXISTS { ?term <https://schema.org/isPartOf> <http://attic.schema.org> .}
    }
    ORDER BY ?term  """
        nri1_results = self.rdflib_data.query(nri1)
        if len(nri1_results):
            log.info("Invalid SuperType errors!!!\n")
            for row in nri1_results:
                log.info(
                    "Term '%s' has nonexistent supertype: '%s'"
                    % (row["term"], row["super"])
                )
        self.assertEqual(
            len(nri1_results),
            0,
            "Types with nonexistent SuperTypes. Found: %s" % len(nri1_results),
        )

        def test_propswitoutdomain(self):
            nri1 = """ select ?term where {
            ?term a rdf:Property.
            FILTER NOT EXISTS { ?term <https://schema.org/domainIncludes> ?o .}
        }
         """
            nri1_results = self.rdflib_data.query(nri1)
            if len(nri1_results):
                log.info("Property without domain errors!!!\n")
                for row in nri1_results:
                    log.info("Term '%s' has no domainIncludes value(s)" % (row["term"]))
            self.assertEqual(
                len(nri1_results),
                0,
                "Property without domain extensions  Found: %s" % len(nri1_results),
            )

        def test_propswitoutrange(self):
            nri1 = """ select ?term where {
            ?term a rdf:Property.
            FILTER NOT EXISTS { ?term <https://schema.org/rangeIncludes> ?o .}
        }
         """
            nri1_results = self.rdflib_data.query(nri1)
            if len(nri1_results):
                log.info("Property without domain errors!!!\n")
                for row in nri1_results:
                    log.info("Term '%s' has no rangeIncludes value(s)" % (row["term"]))
            self.assertEqual(
                len(nri1_results),
                0,
                "Property without range extensions  Found: %s" % len(nri1_results),
            )

    def test_superPropertiesExist(self):
        nri1 = """select ?term ?super where {
       ?term rdf:type rdf:Property.
       ?term rdfs:subPropertyOf ?super.
       FILTER NOT EXISTS { ?super rdf:type rdf:Property }

       BIND(STR(?term) AS ?strVal)
       FILTER(STRLEN(?strVal) >= 19 && SUBSTR(?strVal, 1, 19) = "https://schema.org/")

       BIND(STR(?super) AS ?superStrVal)
       FILTER(STRLEN(?superStrVal) >= 19 && SUBSTR(?superStrVal, 1, 19) = "https://schema.org/")
        FILTER NOT EXISTS { ?term <https://schema.org/isPartOf> <http://attic.schema.org> .}
    }
    ORDER BY ?term  """
        nri1_results = self.rdflib_data.query(nri1)
        if len(nri1_results):
            log.info("Invalid Super-Property errors!!!\n")
            for row in nri1_results:
                log.info(
                    "Term '%s' has nonexistent super-property: '%s'"
                    % (row["term"], row["super"])
                )
        self.assertEqual(
            len(nri1_results),
            0,
            "Properties with nonexistent SuperProperties. Found: %s"
            % len(nri1_results),
        )

    def test_selfReferencingInverse(self):
        nri1 = """select ?term ?inverse where {
       ?term rdf:type rdf:Property.
       ?term <https://schema.org/inverseOf> ?inverse.

       BIND(STR(?term) AS ?strVal)
       FILTER(STRLEN(?strVal) >= 19 && SUBSTR(?strVal, 1, 19) = "https://schema.org/")

       FILTER(str(?term) = str(?inverse))
        FILTER NOT EXISTS { ?term <https://schema.org/isPartOf> <http://attic.schema.org> .}

    }
    ORDER BY ?term  """
        nri1_results = self.rdflib_data.query(nri1)
        if len(nri1_results):
            log.info("Self referencing inverseOf errors!!!\n")
            for row in nri1_results:
                log.info("Term '%s' is defined as inverseOf self" % (row["term"]))
        self.assertEqual(
            len(nri1_results),
            0,
            "Types with self referencing inverseOf Found: %s" % len(nri1_results),
        )

    def test_sameInverseAndSupercededByTarget(self):
        nri1 = """select ?term ?inverse ?super where {
       ?term rdf:type rdf:Property.
       ?term <https://schema.org/inverseOf> ?inverse.
       ?term <https://schema.org/supercededBy> ?super.

       BIND(STR(?term) AS ?strVal)
       FILTER(STRLEN(?strVal) >= 18 && SUBSTR(?strVal, 1, 18) = "https://schema.org/")

       FILTER(str(?inverse) = str(?super))
        FILTER NOT EXISTS { ?term <https://schema.org/isPartOf> <http://attic.schema.org> .}

    }
    ORDER BY ?term  """
        nri1_results = self.rdflib_data.query(nri1)
        if len(nri1_results):
            log.info("InverseOf supercededBy shared target errors!!!\n")
            for row in nri1_results:
                log.info(
                    "Term '%s' defined ase inverseOf AND supercededBy %s"
                    % (row["term"], row["inverse"])
                )
        self.assertEqual(
            len(nri1_results),
            0,
            "Types with inverseOf supercededBy shared target Found: %s"
            % len(nri1_results),
        )

    def test_commentEndWithPeriod(self):
        """Validate that class and property RDF comments end with a punctuation."""
        nri1 = """select ?term ?com where {
       ?term rdfs:comment ?com.

       BIND(STR(?term) AS ?strVal)
       FILTER(STRLEN(?strVal) >= 19 && SUBSTR(?strVal, 1, 19) = "https://schema.org/")

       FILTER (!(regex(str(?com), '[\\\\.\\\\)\\\\?]\\\\s*$') || regex(str(?com), 'n\\\\* .*')))
    }
    ORDER BY ?term  """
        nri1_results = tuple(map(str, self.rdflib_data.query(nri1)))
        self.assertFalse(
            nri1_results,
            "Comment without ending '.', ')' or '?' Found: %s"
            % "\n".join(nri1_results),
        )

    def test_typeLabelCase(self):
        nri1 = """select ?term ?label where {
       ?term rdf:type rdfs:Class.
       ?term rdfs:label ?label.

       BIND(STR(?term) AS ?strVal)
       FILTER(STRLEN(?strVal) >= 19 && SUBSTR(?strVal, 1, 19) = "https://schema.org/")

       FILTER (!regex(str(?label), '^[0-9]*[A-Z].*'))
    }
    ORDER BY ?term  """
        nri1_results = self.rdflib_data.query(nri1)
        if len(nri1_results):
            log.info("Type label [A-Z] errors!!!\n")
            for row in nri1_results:
                log.info(
                    "Type '%s' has a label without upper case 1st character"
                    % (row["term"])
                )
        self.assertEqual(
            len(nri1_results),
            0,
            "Type label not [A-Z] 1st non-numeric char Found: %s" % len(nri1_results),
        )

    def test_propertyLabelCase(self):
        nri1 = """select ?term ?label where {
       ?term rdf:type rdf:Property.
       ?term rdfs:label ?label.

       BIND(STR(?term) AS ?strVal)
       FILTER(STRLEN(?strVal) >= 19 && SUBSTR(?strVal, 1, 19) = "https://schema.org/")

       FILTER (!regex(str(?label), '^[0-9]*[a-z].*'))
    }
    ORDER BY ?term  """
        nri1_results = self.rdflib_data.query(nri1)
        if len(nri1_results):
            log.info("Property label [a-z] errors!!!\n")
            for row in nri1_results:
                log.info(
                    "Property '%s' has a label without lower case 1st non-numeric character"
                    % (row["term"])
                )
        self.assertEqual(
            len(nri1_results),
            0,
            "Property label not [a-z] 1st char Found: %s" % len(nri1_results),
        )

    def test_superTypeInAttic(self):
        nri1 = """select ?term ?super where {
       {
           ?term rdfs:subClassOf ?super.
       }
       UNION
       {
           ?term rdfs:subPropertyOf ?super.
       }
       ?super <https://schema.org/isPartOf> <http://attic.schema.org> .
       FILTER NOT EXISTS { ?term <https://schema.org/isPartOf> <http://attic.schema.org> .}
    }
    ORDER BY ?term  """
        nri1_results = self.rdflib_data.query(nri1)
        if len(nri1_results):
            log.info("Super-term in attic errors!!!\n")
            for row in nri1_results:
                log.info(
                    "Term '%s' is sub-term of %s a term in attic"
                    % (row["term"], row["super"])
                )
        self.assertEqual(
            len(nri1_results), 0, "Super-term in attic  Found: %s" % len(nri1_results)
        )

    def test_referenceTermInAttic(self):
        nri1 = """select ?term ?rel ?ref where {
       {
           ?term <https://schema.org/domainIncludes> ?ref.
           ?term ?rel ?ref.
       }
       UNION
       {
           ?term <https://schema.org/rangeIncludes> ?ref.
           ?term ?rel ?ref.
       }
       UNION
       {
           ?term <https://schema.org/inverseOf> ?ref.
           ?term ?rel ?ref.
       }
       UNION
       {
           ?term <https://schema.org/supercededBy> ?ref.
           ?term ?rel ?ref.
       }
       ?ref <https://schema.org/isPartOf> <http://attic.schema.org> .
       FILTER NOT EXISTS { ?term <https://schema.org/isPartOf> <http://attic.schema.org> .}
    }
    ORDER BY ?term  """
        nri1_results = self.rdflib_data.query(nri1)
        if len(nri1_results):
            log.info("Reference to attic term errors!!!\n")
            for row in nri1_results:
                log.info(
                    "Term '%s' makes a %s reference to %s a term in attic"
                    % (row["term"], row["rel"], row["ref"])
                )
        self.assertEqual(
            len(nri1_results),
            0,
            "Reference to attic term  Found: %s" % len(nri1_results),
        )

    def test_termIn2PlusExtensions(self):
        nri1 = """select ?term (count(?part) as ?count) where {
        ?term <https://schema.org/isPartOf> ?part.
    }
    GROUP BY ?term
    HAVING (count(?part) > 1)
    ORDER BY ?term
     """
        nri1_results = self.rdflib_data.query(nri1)
        if len(nri1_results):
            log.info("Term in +1 extensions errors!!!\n")
            for row in nri1_results:
                log.info(
                    "Term '%s' isPartOf %s extensions" % (row["term"], row["count"])
                )
        self.assertEqual(
            len(nri1_results), 0, "Term in +1 extensions  Found: %s" % len(nri1_results)
        )

    def test_termNothttps(self):
        nri1 = """select distinct ?term where {
      ?term ?p ?o.
      FILTER strstarts(str(?term),"http://schema.org")
    }
    ORDER BY ?term
     """
        nri1_results = self.rdflib_data.query(nri1)
        if len(nri1_results):
            log.info("Term defined as http errors!!!\n")
            for row in nri1_results:
                log.info("Term '%s' is defined as http " % (row["term"]))
        self.assertEqual(
            len(nri1_results), 0, "Term defined as http  Found: %s" % len(nri1_results)
        )

    def test_targetNothttps(self):
        nri1 = """prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    prefix schema: <https://schema.org/>
    select ?term ?target where {

      ?term schema:domainIncludes |
            schema:rangeIncludes |
            rdfs:subClassOf |
            rdfs:subPropertyOf |
            schema:supercededBy |
            schema:inverseOf ?target.
      filter strstarts(str(?target),"http://schema.org")
    }
    ORDER BY ?term
     """
        nri1_results = self.rdflib_data.query(nri1)
        if len(nri1_results):
            log.info("Target defined as https errors!!!\n")
            for row in nri1_results:
                log.info(
                    "Term '%s' references term %s  as https "
                    % (row["term"], row["target"])
                )
        self.assertEqual(
            len(nri1_results), 0, "Term defined as https  Found: %s" % len(nri1_results)
        )

    def test_isPartOf(self):
        nri1 = """prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    prefix schema: <https://schema.org/>
    select ?term  ?partof where {
      ?term schema:isPartOf ?partof .
      MINUS{
        ?term schema:isPartOf <https://attic.schema.org>
      }
      MINUS{
        ?term schema:isPartOf <https://auto.schema.org>
      }
      MINUS{
        ?term schema:isPartOf <https://bib.schema.org>
      }
      MINUS{
        ?term schema:isPartOf <https://health-lifesci.schema.org>
      }
      MINUS{
        ?term schema:isPartOf <https://meta.schema.org>
      }
      MINUS{
        ?term schema:isPartOf <https://pending.schema.org>
      }
    }
    ORDER BY ?term
      """
        nri1_results = self.rdflib_data.query(nri1)
        if len(nri1_results):
            log.info("Invalid isPartOf value errors!!!\n")
            for row in nri1_results:
                log.info(
                    "Term '%s' has invalid isPartOf value '%s'"
                    % (row["term"], row["partof"])
                )
        self.assertEqual(
            len(nri1_results),
            0,
            "Invalid isPartOf value errors  Found: %s" % len(nri1_results),
        )

    @unittest.expectedFailure
    def test_EnumerationWithoutEnums(self):
        nri1 = """select ?term where {
        ?term a rdfs:subClassOf+ <https://schema.org/Enumeration> .
        FILTER NOT EXISTS { ?enum a ?term. }
        FILTER NOT EXISTS { ?term <https://schema.org/isPartOf> <http://attic.schema.org> .}
    }
    ORDER BY ?term  """
        nri1_results = self.rdflib_data.query(nri1)
        if len(nri1_results):
            log.info("Enumeration Type without Enumeration value(s) errors!!!\n")
            for row in nri1_results:
                log.info(
                    "Enumeration Type '%s' has no matching enum values" % (row["term"])
                )
        self.assertEqual(
            len(nri1_results),
            0,
            "Enumeration Type without Enumeration value(s)    Found: %s"
            % len(nri1_results),
        )


def tearDownModule():
    global warnings
    if len(warnings) > 0:
        log.info("\nWarnings (%s):\n" % len(warnings))
    for warn in warnings:
        log.info("%s" % warn)


# TODO: Unwritten tests (from basics; easier here?)
#
# * different terms should not have identical comments
# * rdflib and internal parsers should have same number of triples
# * if x and y are inverseOf each other, the rangeIncludes types on x should be domainIncludes on y, and vice-versa.
# * need a few supporting functions e.g. all terms, all types, all properties, all enum values; candidates for api later but just use here first.

if __name__ == "__main__":
    unittest.main()
