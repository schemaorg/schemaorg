import unittest
import os
import logging

from headers import *
from api import *
from parsers import *

schema_path = './data/schema.rdfa'
examples_path = './data/examples.txt'

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


class SDOBasicsTestCase(unittest.TestCase):

  def test_foundSchema(self):
    self.assertEqual(True, os.path.exists(schema_path), "Expected schema file: "+ schema_path )

  def test_foundExamples(self):
    self.assertEqual(True, os.path.exists(examples_path), "Expected examples file: "+ examples_path )


class SchemaWellformedTestCase(unittest.TestCase):

  def test_wellformed(self):

    from xml.etree import ElementTree
    tree = ElementTree.parse(schema_path)
    rootElem = tree.getroot()
    log.info("Root element of schema file: "+ rootElem.tag)
    self.assertEqual("html", rootElem.tag, "Expected root element of schema to be 'html'.")


class SchemaBasicAPITestCase(unittest.TestCase):

  def setUp(self):
     read_schemas()
     self.schemasInitialized = schemasInitialized

  def test_schemasInitialized(self):
     self.assertEqual(self.schemasInitialized,True, "Schemas should be initialized during setup.")

  def test_gotThing(self):

     thing = Unit.GetUnit("Thing")
     if thing is None:
       gotThing = False
     else:
       gotThing = True

     self.assertEqual( gotThing, True, "Thing node should be accessible via GetUnit('Thing').")

  def test_gotFooBarThing(self):

     thing = Unit.GetUnit("FooBar")
     if thing is None:
       gotThing = False
     else:
       gotThing = True

     self.assertEqual( gotThing, False, "Thing node should NOT be accessible via GetUnit('FooBar').")

if __name__ == "__main__": 
  unittest.main()
