# -*- coding: utf-8 -*-

import unittest
import os
from os import getenv
from os.path import expanduser
import logging # https://docs.python.org/2/library/logging.html#logging-levels
import glob
import sys

sys.path.append( os.getcwd() )
sys.path.insert( 1, 'lib' ) #Pickup libs, rdflib etc., from shipped lib directory

#sdk_path = getenv('APP_ENGINE',
#                  expanduser("~") + '/google-cloud-sdk/platform/google_appengine/')
#sys.path.insert(0, sdk_path)

from api import *
from parsers import *

#Setup testharness state BEFORE importing sdoapp
setInTestHarness(True)
os.environ["WARMUPSTATE"] = "off"
from sdoapp import *

schema_path = './data/schema.rdfa'
examples_path = './data/examples.txt'
warnings = []

andstr = "\n AND\n  "
TYPECOUNT_UPPERBOUND = 1000
TYPECOUNT_LOWERBOUND = 500

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)
setInTestHarness(True)

# Tests to probe the health of both schemas and code using graph libraries in rdflib
# Note that known failings can be annotated with @unittest.expectedFailure or @skip("reason...")
class SDOGraphSetupTestCase(unittest.TestCase):

  @classmethod
  def loadGraphs(self):
      from rdflib import Graph
      import rdflib
      self.rdflib_data = Graph()
      store = getMasterStore()
      graphs = list(store.graphs())
      log.info("Loading test graph from MasterStore")
      for g in graphs:
          id = str(g.identifier)
          if not id.startswith("http://"):#skip some internal graphs
              continue
          self.rdflib_data += g

  @classmethod
  def setUpClass(self):
    log.info("Graph tests require rdflib.")
    try:
      log.info("Trying to import rdflib...")
      import rdflib
      from rdflib import Graph
    except Exception as e:
      raise unittest.SkipTest("Need rdflib installed to do graph tests: %s" % e)
    SDOGraphSetupTestCase.loadGraphs()

  def test_graphsLoaded(self):
    self.assertTrue(len(self.rdflib_data) > 0,
                     "Graph rdflib_data should have some triples in it.")

  # SPARQLResult http://rdflib.readthedocs.org/en/latest/apidocs/rdflib.plugins.sparql.html
  # "A list of dicts (solution mappings) is returned"

  def test_found_sixplus_inverseOf(self):
    inverseOf_results = self.rdflib_data.query("select ?x ?y where { ?x <http://schema.org/inverseOf> ?y }")
    log.info("inverseOf result count: %s" % len(inverseOf_results ) )
    self.assertTrue(len(inverseOf_results) >= 6,
                    "Six or more inverseOf expected. Found: %s " % len(inverseOf_results ) )

  def test_even_number_inverseOf(self):

    inverseOf_results = self.rdflib_data.query("select ?x ?y where { ?x <http://schema.org/inverseOf> ?y }")
    self.assertTrue(len(inverseOf_results ) % 2 == 0,
                    "Even number of inverseOf triples expected. Found: %s " % len(inverseOf_results ) )

  def test_non_equal_inverseOf(self):
    results = self.rdflib_data.query("select ?x ?y where { ?x <http://schema.org/inverseOf> ?y }")
    for result in results :
      self.assertTrue(result[0] != result[1],
                      "%s should not be equal to %s" % (result[0], result[1]) )

  def test_non_equal_supercededBy(self):
    results = self.rdflib_data.query("select ?x ?y where { ?x <http://schema.org/supercededBy> ?y }")
    for result in results :
      self.assertTrue(result[0] != result[1],
                      "%s should not be equal to %s" % (result[0], result[1]) )

  @unittest.expectedFailure # autos
  def test_needlessDomainIncludes(self):
    global warnings
    # check immediate subtypes don't declare same domainIncludes
    # TODO: could we use property paths here to be more thorough?
    # rdfs:subClassOf+ should work but seems not to.
    ndi1 = ('''SELECT ?prop ?c1 ?c2 
           WHERE { 
           ?prop <http://schema.org/domainIncludes> ?c1 .
           ?prop <http://schema.org/domainIncludes> ?c2 .
           ?c1 rdfs:subClassOf ?c2 .
           FILTER (?c1 != ?c2) .
           FILTER NOT EXISTS { ?term <http://schema.org/isPartOf> <http://attic.schema.org> .}
           }
           ORDER BY ?prop ''')
    ndi1_results = self.rdflib_data.query(ndi1)
    if (len(ndi1_results) > 0):
        for row in ndi1_results:
            warn = "WARNING property %s defining domain, %s, [which is subclassOf] %s unnecessarily" % (row["prop"],row["c1"],row["c2"])
            warnings.append(warn)
            log.info(warn + "\n")
    self.assertEqual(len(ndi1_results), 0,
                     "No subtype need redeclare a domainIncludes of its parents. Found: %s " % len(ndi1_results ) )

  @unittest.expectedFailure
  def test_needlessRangeIncludes(self):
    global warnings
    # as above, but for range. We excuse URL as it is special, not best seen as a Text subtype.
    # check immediate subtypes don't declare same domainIncludes
    # TODO: could we use property paths here to be more thorough?
    nri1= ('''SELECT ?prop ?c1 ?c2 
         WHERE { 
         ?prop <http://schema.org/rangeIncludes> ?c1 .
         ?prop <http://schema.org/rangeIncludes> ?c2 .
         ?c1 rdfs:subClassOf ?c2 .
         FILTER (?c1 != ?c2) .
         FILTER (?c1 != <http://schema.org/URL>) .
        FILTER NOT EXISTS { ?term <http://schema.org/isPartOf> <http://attic.schema.org> .}
             }
             ORDER BY ?prop ''')
    nri1_results = self.rdflib_data.query(nri1)
    if (len(nri1_results)>0):
        for row in nri1_results:
            warn = "WARNING property %s defining range, %s, [which is subclassOf] %s unnecessarily" % (row["prop"],row["c1"],row["c2"])
            warnings.append(warn)
            log.info(warn + "\n")
    self.assertEqual(len(nri1_results), 0, "No subtype need redeclare a rangeIncludes of its parents. Found: %s" % len(nri1_results) )

#  def test_supersededByAreLabelled(self):
#    supersededByAreLabelled_results = self.rdflib_data.query("select ?x ?y ?z where { ?x <http://schema.org/supersededBy> ?y . ?y <http://schema.org/name> ?z }")
#    self.assertEqual(len(inverseOf_results ) % 2 == 0, True, "Even number of inverseOf triples expected. Found: %s " % len(inverseOf_results ) )


  def test_validRangeIncludes(self):
    nri1= ('''SELECT ?prop ?c1
     WHERE {
         ?prop <http://schema.org/rangeIncludes> ?c1 .
         OPTIONAL{
            ?c1 rdf:type ?c2 .
            ?c1 rdf:type rdfs:Class .
         }.
         FILTER (!BOUND(?c2))
        FILTER NOT EXISTS { ?prop <http://schema.org/isPartOf> <http://attic.schema.org> .}
                 }
                 ORDER BY ?prop ''')
    nri1_results = self.rdflib_data.query(nri1)
    for row in nri1_results:
        log.info("Property %s invalid rangeIncludes value: %s\n" % (row["prop"],row["c1"]))
    self.assertEqual(len(nri1_results), 0, "RangeIncludes should define valid type. Found: %s" % len(nri1_results))

  def test_validDomainIncludes(self):
    nri1= ('''SELECT ?prop ?c1
     WHERE {
         ?prop <http://schema.org/domainIncludes> ?c1 .
         OPTIONAL{
            ?c1 rdf:type ?c2 .
            ?c1 rdf:type rdfs:Class .
         }.
         FILTER (!BOUND(?c2))
        FILTER NOT EXISTS { ?prop <http://schema.org/isPartOf> <http://attic.schema.org> .}
                 }
                 ORDER BY ?prop ''')
    nri1_results = self.rdflib_data.query(nri1)
    for row in nri1_results:
        log.info("Property %s invalid domainIncludes value: %s\n" % (row["prop"],row["c1"]))
    self.assertEqual(len(nri1_results), 0, "DomainIncludes should define valid type. Found: %s" % len(nri1_results))

  # These are place-holders for more sophisticated SPARQL-expressed checks.
  @unittest.expectedFailure
  def test_readSchemaFromRDFa(self):
    self.assertTrue(True, False, "We should know how to locally get /docs/schema_org_rdfa.html but this requires fixes to api.py.")

  #@unittest.expectedFailure
  def test_simpleLabels(self):
     s = ""
     complexLabels = self.rdflib_data.query(
        "select distinct ?term ?label where { ?term rdfs:label ?label  FILTER regex(?label,'[^a-zA-Z0-9_ ]','i'). } " )
     for row in complexLabels:
       s += (" term %s has complex label: %s\n" % (row["term"],row["label"]))
     self.assertTrue(len(complexLabels ) == 0,
       "No complex term labels expected; alphanumeric only please. Found: %s Details: %s\n"% (len(complexLabels), s) )
     # Whitespace is tolerated, for now.
     # we don't deal well with non definitional uses of rdfs:label yet - non terms are flagged up.
     # https://github.com/schemaorg/schemaorg/issues/1136

    #
    # TODO: https://github.com/schemaorg/schemaorg/issues/662
    #
    # self.assertEqual(len(ndi1_results), 0, "No domainIncludes or rangeIncludes value should lack a type. Found: %s " % len(ndi1_results ) )

  def test_labelMatchesTermId(self):
    nri1= ('''select ?term ?label where { 
       ?term rdfs:label ?label.
       BIND(STR(?term) AS ?strVal)
       FILTER(STRLEN(?strVal) >= 18 && SUBSTR(?strVal, 1, 18) = "http://schema.org/")
       FILTER(SUBSTR(?strVal, 19) != STR(?label))
    }
    ORDER BY ?term  ''')
    nri1_results = self.rdflib_data.query(nri1)
    if len(nri1_results):
        log.info("Label matching errors:")
        for row in nri1_results:
            log.info("Term '%s' has none-matching label: '%s'" % (row["term"],row["label"]))
    self.assertEqual(len(nri1_results), 0, "Term should have matching rdfs:label. Found: %s" % len(nri1_results))

  def test_superTypesExist(self):
    nri1= ('''select ?term ?super where { 
       ?term rdfs:subClassOf ?super.
       ?term rdf:type rdfs:Class.
       FILTER NOT EXISTS { ?super rdf:type rdfs:Class }
       
       BIND(STR(?term) AS ?strVal)
       FILTER(STRLEN(?strVal) >= 18 && SUBSTR(?strVal, 1, 18) = "http://schema.org/")
       
       BIND(STR(?super) AS ?superStrVal)
       FILTER(STRLEN(?superStrVal) >= 18 && SUBSTR(?superStrVal, 1, 18) = "http://schema.org/")
        FILTER NOT EXISTS { ?term <http://schema.org/isPartOf> <http://attic.schema.org> .}
    }
    ORDER BY ?term  ''')
    nri1_results = self.rdflib_data.query(nri1)
    if len(nri1_results):
        log.info("Invalid SuperType errors!!!\n")
        for row in nri1_results:
            log.info("Term '%s' has nonexistent supertype: '%s'" % (row["term"],row["super"]))
    self.assertEqual(len(nri1_results), 0, "Types with nonexistent SuperTypes. Found: %s" % len(nri1_results))

  def test_superPropertiesExist(self):
    nri1= ('''select ?term ?super where { 
       ?term rdf:type rdf:Property.
       ?term rdfs:subPropertyOf ?super.
       FILTER NOT EXISTS { ?super rdf:type rdf:Property }
       
       BIND(STR(?term) AS ?strVal)
       FILTER(STRLEN(?strVal) >= 18 && SUBSTR(?strVal, 1, 18) = "http://schema.org/")

       BIND(STR(?super) AS ?superStrVal)
       FILTER(STRLEN(?superStrVal) >= 18 && SUBSTR(?superStrVal, 1, 18) = "http://schema.org/")
        FILTER NOT EXISTS { ?term <http://schema.org/isPartOf> <http://attic.schema.org> .}
    }
    ORDER BY ?term  ''')
    nri1_results = self.rdflib_data.query(nri1)
    if len(nri1_results):
        log.info("Invalid Super-Property errors!!!\n")
        for row in nri1_results:
            log.info("Term '%s' has nonexistent super-property: '%s'" % (row["term"],row["super"]))
    self.assertEqual(len(nri1_results), 0, "Properties with nonexistent SuperProperties. Found: %s" % len(nri1_results))

  def test_selfReferencingInverse(self):
    nri1= ('''select ?term ?inverse where { 
       ?term rdf:type rdf:Property.
       ?term <http://schema.org/inverseOf> ?inverse.
       
       BIND(STR(?term) AS ?strVal)
       FILTER(STRLEN(?strVal) >= 18 && SUBSTR(?strVal, 1, 18) = "http://schema.org/")
       
       FILTER(str(?term) = str(?inverse))
        FILTER NOT EXISTS { ?term <http://schema.org/isPartOf> <http://attic.schema.org> .}

    }
    ORDER BY ?term  ''')
    nri1_results = self.rdflib_data.query(nri1)
    if len(nri1_results):
        log.info("Self referencing inverseOf errors!!!\n")
        for row in nri1_results:
            log.info("Term '%s' is defined as inverseOf self" % (row["term"]))
    self.assertEqual(len(nri1_results), 0, "Types with self referencing inverseOf Found: %s" % len(nri1_results))

  def test_sameInverseAndSupercededByTarget(self):
    nri1= ('''select ?term ?inverse ?super where { 
       ?term rdf:type rdf:Property.
       ?term <http://schema.org/inverseOf> ?inverse.
       ?term <http://schema.org/supercededBy> ?super.
       
       BIND(STR(?term) AS ?strVal)
       FILTER(STRLEN(?strVal) >= 18 && SUBSTR(?strVal, 1, 18) = "http://schema.org/")
       
       FILTER(str(?inverse) = str(?super))
        FILTER NOT EXISTS { ?term <http://schema.org/isPartOf> <http://attic.schema.org> .}

    }
    ORDER BY ?term  ''')
    nri1_results = self.rdflib_data.query(nri1)
    if len(nri1_results):
        log.info("InverseOf supercededBy shared target errors!!!\n")
        for row in nri1_results:
            log.info("Term '%s' defined ase inverseOf AND supercededBy %s" % (row["term"], row["inverse"]))
    self.assertEqual(len(nri1_results), 0, "Types with inverseOf supercededBy shared target Found: %s" % len(nri1_results))

  @unittest.expectedFailure 
  def test_commentEndWithPeriod(self):
    nri1= ('''select ?term ?com where { 
       ?term rdfs:comment ?com.
       
       BIND(STR(?term) AS ?strVal)
       FILTER(STRLEN(?strVal) >= 18 && SUBSTR(?strVal, 1, 18) = "http://schema.org/")

       FILTER regex(str(?com), '[^.]$')
    }
    ORDER BY ?term  ''')
    nri1_results = self.rdflib_data.query(nri1)
    if len(nri1_results):
        log.info("Coment without ending '.' errors!!!\n")
        for row in nri1_results:
            log.info("Term '%s' has a comment without an ending '.'" % (row["term"]))
    self.assertEqual(len(nri1_results), 0, "Coment without ending '.' Found: %s" % len(nri1_results))

  def test_typeLabelCase(self):
    nri1= ('''select ?term ?label where { 
       ?term rdf:type rdfs:Class.
       ?term rdfs:label ?label.
       
       BIND(STR(?term) AS ?strVal)
       FILTER(STRLEN(?strVal) >= 18 && SUBSTR(?strVal, 1, 18) = "http://schema.org/")

       FILTER regex(str(?label), '^[^A-Z]')
    }
    ORDER BY ?term  ''')
    nri1_results = self.rdflib_data.query(nri1)
    if len(nri1_results):
        log.info("Type label [A-Z] errors!!!\n")
        for row in nri1_results:
            log.info("Type '%s' has a label without upper case 1st character" % (row["term"]))
    self.assertEqual(len(nri1_results), 0, "Type label not [A-Z] 1st char Found: %s" % len(nri1_results))
    
  def test_propertyLabelCase(self):
    nri1= ('''select ?term ?label where { 
       ?term rdf:type rdf:Property.
       ?term rdfs:label ?label.
       
       BIND(STR(?term) AS ?strVal)
       FILTER(STRLEN(?strVal) >= 18 && SUBSTR(?strVal, 1, 18) = "http://schema.org/")

       FILTER regex(str(?label), '^[^a-z]')
    }
    ORDER BY ?term  ''')
    nri1_results = self.rdflib_data.query(nri1)
    if len(nri1_results):
        log.info("Property label [a-z] errors!!!\n")
        for row in nri1_results:
            log.info("Property '%s' has a label without lower case 1st character" % (row["term"]))
    self.assertEqual(len(nri1_results), 0, "Property label not [a-z] 1st char Found: %s" % len(nri1_results))

  def test_superTypeInAttic(self):
    nri1= ('''select ?term ?super where { 
       {
           ?term rdfs:subClassOf ?super.
       }
       UNION
       {
           ?term rdfs:subPropertyOf ?super.
       }
       ?super <http://schema.org/isPartOf> <http://attic.schema.org> .
       FILTER NOT EXISTS { ?term <http://schema.org/isPartOf> <http://attic.schema.org> .}
    }
    ORDER BY ?term  ''')
    nri1_results = self.rdflib_data.query(nri1)
    if len(nri1_results):
        log.info("Super-term in attic errors!!!\n")
        for row in nri1_results:
            log.info("Term '%s' is sub-term of %s a term in attic" % (row["term"],row["super"]))
    self.assertEqual(len(nri1_results), 0, "Super-term in attic  Found: %s" % len(nri1_results))

  def test_referenceTermInAttic(self):
    nri1= ('''select ?term ?rel ?ref where { 
       {
           ?term <http://schema.org/domainIncludes> ?ref.
           ?term ?rel ?ref.
       }
       UNION
       {
           ?term <http://schema.org/rangeIncludes> ?ref.
           ?term ?rel ?ref.
       }
       UNION
       {
           ?term <http://schema.org/inverseOf> ?ref.
           ?term ?rel ?ref.
       }
       UNION
       {
           ?term <http://schema.org/supercededBy> ?ref.
           ?term ?rel ?ref.
       }
       ?ref <http://schema.org/isPartOf> <http://attic.schema.org> .
       FILTER NOT EXISTS { ?term <http://schema.org/isPartOf> <http://attic.schema.org> .}
    }
    ORDER BY ?term  ''')
    nri1_results = self.rdflib_data.query(nri1)
    if len(nri1_results):
        log.info("Reference to attic term errors!!!\n")
        for row in nri1_results:
            log.info("Term '%s' makes a %s reference to %s a term in attic" % (row["term"],row["rel"],row["ref"]))
    self.assertEqual(len(nri1_results), 0, "Reference to attic term  Found: %s" % len(nri1_results))

  def test_termIn2PlusExtensions(self):
    nri1= ('''select ?term (count(?part) as ?count) where { 
        ?term <http://schema.org/isPartOf> ?part.
    }
    GROUP BY ?term
    HAVING (count(?part) > 1)
    ORDER BY ?term
     ''')
    nri1_results = self.rdflib_data.query(nri1)
    if len(nri1_results):
        log.info("Term in +1 extensions errors!!!\n")
        for row in nri1_results:
            log.info("Term '%s' isPartOf %s extensions" % (row["term"],row["count"]))
    self.assertEqual(len(nri1_results), 0, "Term in +1 extensions  Found: %s" % len(nri1_results))

  @unittest.expectedFailure
  def test_EnumerationWithoutEnums(self):
    nri1= ('''select ?term where { 
        ?term rdfs:subClassOf/rdfs:subClassOf* <http://schema.org/Enumeration> .
        FILTER NOT EXISTS { ?enum a ?term. }
        FILTER NOT EXISTS { ?term <http://schema.org/isPartOf> <http://attic.schema.org> .}
    } 
    ORDER BY ?term  ''')
    nri1_results = self.rdflib_data.query(nri1)
    if len(nri1_results):
        log.info("Enumeration Type without Enumeration value(s) errors!!!\n")
        for row in nri1_results:
            log.info("Enumeration Type '%s' has no matching enum values" % (row["term"]))
    self.assertEqual(len(nri1_results), 0, "Enumeration Type without Enumeration value(s)    Found: %s" % len(nri1_results))


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
