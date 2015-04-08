import unittest
import os
import logging # https://docs.python.org/2/library/logging.html#logging-levels
import glob

from headers import *
from api import *
from parsers import *

schema_path = './data/schema.rdfa'
examples_path = './data/examples.txt'

andstr = "\n AND\n  "
TYPECOUNT_UPPERBOUND = 1000
TYPECOUNT_LOWERBOUND = 500

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

# Tests to probe the health of both schemas and code using graph libraries in rdflib
# Note that known failings can be annotated with @unittest.expectedFailure or @skip("reason...")


class SDOGraphSetupTestCase(unittest.TestCase):


  @classmethod
  def parseRDFaFilesWithRDFLib(self):
      """Parse data/*rdfa into a data object and an error object with rdflib.
      We glob so that work-in-progress schemas can be stored separately. For
      final publication, a single schema file is used. Note that this does 
      not yet load or test any extension schemas beneath data/ext/*."""

      from rdflib import Graph
      files = glob.glob("data/*.rdfa")
      log.info("Found %s files via data/*rdfa." % len(files))
      self.rdflib_errors = Graph()
      self.rdflib_data = Graph()
      for f in files:
        log.info("Files to parse: %s" % f )
        log.info("Parsing URL %s with rdflib RDFa parser. " % f)
        self.rdflib_data.parse(f, format='rdfa', pgraph=self.rdflib_errors)
        # log.info(self.rdflib_errors.serialize(format="nt"))

  @classmethod
  def setUpClass(self):
    log.info("Graph tests require rdflib.")
    import unittest
    try:
      import rdflib
      from rdflib import Graph
    except:
      raise unittest.SkipTest("Need rdflib installed to do graph tests.")

    read_schemas() # built-in parsers.
    self.schemasInitialized = schemasInitialized
    log.info("SDOGraphSetupTestCase reading schemas using built-in parsers.")

    log.info("Attempting to parse data/*rdfa with rdflib.")
    SDOGraphSetupTestCase.parseRDFaFilesWithRDFLib()

  def test_schemasInitializedForGraph(self):
    self.assertEqual(self.schemasInitialized,True, "Schemas should be initialized during setup, so we can load them into a graph for testing.")

  def test_rdflib_happy(self):
    self.assertEqual(len(self.rdflib_errors)==0, True, "rdflib should have zero errors. %s" % self.rdflib_errors.serialize(format="nt"))

  # SPARQLResult http://rdflib.readthedocs.org/en/latest/apidocs/rdflib.plugins.sparql.html
  # "A list of dicts (solution mappings) is returned"

  def test_found_sixplus_inverseOf(self):
    inverseOf_results = self.rdflib_data.query("select ?x ?y where { ?x <http://schema.org/inverseOf> ?y }")
    log.info("inverseOf result count: %s" % len(inverseOf_results ) )
    self.assertEqual(len(inverseOf_results ) >= 6, True, "Six or more inverseOf expected. Found: %s " % len(inverseOf_results ) )

  def test_even_number_inverseOf(self):
    inverseOf_results = self.rdflib_data.query("select ?x ?y where { ?x <http://schema.org/inverseOf> ?y }")
    self.assertEqual(len(inverseOf_results ) % 2 == 0, True, "Even number of inverseOf triples expected. Found: %s " % len(inverseOf_results ) )

  def test_needlessDomainIncludes(self):
    # check immediate subtypes don't declare same domainIncludes
    # TODO: could we use property paths here to be more thorough?
    # rdfs:subClassOf+ should work but seems not to.
    ndi1= ("SELECT ?prop ?c1 ?c2 "
           "WHERE { "
           "?prop <http://schema.org/domainIncludes> ?c1 ."
           "?prop <http://schema.org/domainIncludes> ?c2 ."
           "?c1 rdfs:subClassOf ?c2 ."
           "FILTER (?c1 != ?c2) ."
           "}"
           "ORDER BY ?prop ")
    ndi1_results = self.rdflib_data.query(ndi1)
    if (len(ndi1_results)>0):
        for row in ndi1_results:
            log.info(row)
    self.assertEqual(len(ndi1_results), 0, "No subtype need redeclare a domainIncludes of its parents. Found: %s " % len(ndi1_results ) )

  def test_needlessRangeIncludes(self):
    # as above, but for range. We excuse URL as it is special, not best seen as a Text subtype.
    # check immediate subtypes don't declare same domainIncludes
    # TODO: could we use property paths here to be more thorough?
    nri1= ("SELECT ?prop ?c1 ?c2 "
             "WHERE { "
             "?prop <http://schema.org/rangeIncludes> ?c1 ."
             "?prop <http://schema.org/rangeIncludes> ?c2 ."
             "?c1 rdfs:subClassOf ?c2 ."
             "FILTER (?c1 != ?c2) ."
             "FILTER (?c1 != <http://schema.org/URL>) ." 
             "}"
             "ORDER BY ?prop ")
    nri1_results = self.rdflib_data.query(nri1)
    if (len(nri1_results)>0):
      for row in nri1_results:
        log.info(row)
    self.assertEqual(len(nri1_results), 0, "No subtype need redeclare a rangeIncludes of its parents. Found: %s " % len(nri1_results ) )

  # These are place-holders for more sophisticated SPARQL-expressed checks.

  @unittest.expectedFailure
  def test_readSchemaFromRDFa(self):
    self.assertTrue(True, False, "We should know how to locally get /docs/schema_org_rdfa.html but this requires fixes to api.py.")

# TODO: Unwritten tests (from basics; easier here?)
#
# * different terms should not have identical comments
# * rdflib and internal parsers should have same number of triples
# * if x and y are inverseOf each other, the rangeIncludes types on x should be domainIncludes on y, and vice-versa.
# * need a few supporting functions e.g. all terms, all types, all properties, all enum values; candidates for api later but just use here first.

if __name__ == "__main__":
  unittest.main()
