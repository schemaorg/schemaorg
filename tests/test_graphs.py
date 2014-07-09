import unittest
import os
import logging # https://docs.python.org/2/library/logging.html#logging-levels

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

  def setUp(self):
    log.info("Graph tests require rdflib.")
    import unittest
    try:
      import rdflib
    except:
      raise unittest.SkipTest("Need rdflib installed to do graph tests.")

    read_schemas()
    self.schemasInitialized = schemasInitialized
    log.info("SDOGraphSetupTestCase reading schemas. TODO: Load into a graph.")

  def test_schemasInitializedForGraph(self):
    self.assertEqual(self.schemasInitialized,True, "Schemas should be initialized during setup, so we can load them into a graph for testing.")


  @unittest.expectedFailure
  def test_readSchemaFromRDFa(self):
    self.assertTrue(True, False, "We should know how to locally get /docs/schema_org_rdfa.html but this requires fixes to api.py.")

# TODO: Unwritten tests (from basics; easier here?)
#
# * different terms should not have identical comments
# * if x and y are inverseOf each other, the rangeIncludes types on x should be domainIncludes on y, and vice-versa.
# * need a few supporting functions e.g. all terms, all types, all properties, all enum values; candidates for api later but just use here first.

if __name__ == "__main__":
  unittest.main()
