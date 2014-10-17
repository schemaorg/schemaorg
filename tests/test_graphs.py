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
      final publication, a single schema file is used."""
      
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
