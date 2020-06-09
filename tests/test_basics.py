import unittest
import os
import logging # https://docs.python.org/2/library/logging.html#logging-levels
import sys
sys.path.append( os.getcwd() )
sys.path.insert( 1, 'lib' ) #Pickup libs, rdflib etc., from shipped lib directory
sys.path.insert( 1, 'sdopythonapp' ) #Pickup sdopythonapp functionality
sys.path.insert( 1, 'sdopythonapp/lib' ) #Pickup sdopythonapp libs, rdflib etc., from shipped lib directory
sys.path.insert( 1, 'sdopythonapp/site' ) #Pickup sdopythonapp from shipped site

from testharness import *
#Setup testharness state BEFORE importing sdo libraries
setInTestHarness(True)

from api import extensionsLoaded, extensionLoadErrors
from api import EXAMPLESMAP, Triple
from apirdfterm import VTerm
from apimarkdown import Markdown

from google.appengine.ext import deferred 
from sdoapp import *

schema_path = './data/schema.ttl'
examples_path = './data/examples.txt'

andstr = "\n AND\n  "
TYPECOUNT_UPPERBOUND = 1500
TYPECOUNT_LOWERBOUND = 500

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)



# Tests to probe the health of both schemas and code.
# Note that known failings can be annotated with @unittest.expectedFailure or @skip("reason...")

class BallparkCountTests(unittest.TestCase):
    def test_alltypes(self):

      # ballpark estimates.
      self.assertTrue( len( GetAllTypes() )  > TYPECOUNT_LOWERBOUND , "Should be > %d types. Got %s" % (TYPECOUNT_LOWERBOUND, len (GetAllTypes()) ))
      self.assertTrue( len( GetAllTypes() )  < TYPECOUNT_UPPERBOUND , "Should be < %d types. Got %s" % (TYPECOUNT_UPPERBOUND, len (GetAllTypes()) ))


class SDOBasicsTestCase(unittest.TestCase):

  def test_foundSchema(self):
    self.assertEqual(True, os.path.exists(schema_path), "Expected schema file: "+ schema_path )

  def test_foundExamples(self):
    self.assertEqual(True, os.path.exists(examples_path), "Expected examples file: "+ examples_path )

  def test_ExtractedPlausibleNumberOfExamples(self):

    example_count = len(EXAMPLESMAP)
#    for t in api.EXAMPLESMAP:
#        example_count = example_count + len(t)
    log.info("Extracted %s examples." % example_count )
    self.assertTrue(example_count > 200 and example_count < 600, "Expect that we extracted 200 < x < 600 examples from data/*examples.txt. Found: %s " % example_count)

class SupertypePathsTestCase(unittest.TestCase):
    """
    tRestaurant = VTerm.getTerm("Restaurant")
    tThing = VTerm.getTerm("Thing")
    for path in GetParentPathTo(tRestaurant, tThing ):
      pprint.pprint(', '.join([str(x.id) for x in path ]))"""

    def test_simplePath(self):

      self.assertEqual(  len(
                  GetParentPathTo(VTerm.getTerm("CreativeWork"), VTerm.getTerm("Thing"))
                  ), 1, "1 supertype path from CreativeWork to Thing."  )

    def test_dualPath(self):
      self.assertEqual(  len(
                  GetParentPathTo(VTerm.getTerm("Restaurant"), VTerm.getTerm("Thing"))
                  ), 2, "2 supertype paths from Restaurant to Thing."  )

    def test_inverseDualPath(self):
      self.assertEqual(  len(
                  GetParentPathTo(VTerm.getTerm("Thing"), VTerm.getTerm("Restaurant"))
                  ), 0, "0 supertype paths from Thing to Restaurant."  )

"""class SchemaWellformedTestCase(unittest.TestCase):

  def test_wellformed(self):

    from xml.etree import ElementTree
    tree = ElementTree.parse(schema_path)
    rootElem = tree.getroot()
    log.debug("Root element of schema file: "+ rootElem.tag)
    self.assertEqual("html", rootElem.tag, "Expected root element of schema to be 'html'.")
"""

class TriplesBasicAPITestCase(unittest.TestCase):
  """Tests that don't assume the schemas are pre-loaded."""

  def test_checkAddedTriples(self):
     """This test should store a couple of triples and retrieve them for a fictional 'neogeo' extension layer."""

     u_Volcano = Unit.GetUnit("Volcano", createp=True)
     p_name = Unit.GetUnit("name", createp=True)
     Triple.AddTripleText(u_Volcano, p_name, "foo", layer="neogeo") # last arg is 'layer' aka extension
     Triple.AddTripleText(u_Volcano, p_name, "bar", "neogeo") # show both syntax options 

     try:
       v_names = GetTargets( p_name, u_Volcano, "neogeo")
       log.info("Looking for: Volcano's 'name' property values, 'foo' and 'bar'. counted: %s" % len(v_names) )
       for vn in v_names:
           log.debug("Found a Volcano 'name' value: %s " % vn)
     except Exception as e:
       log.info("Failed volcano lookup. %s " % e)

     self.assertTrue ( "foo" in v_names and "bar" in v_names, "should have foo and bar in name list: %s " % ",".join(v_names)   )
     self.assertEqual(len(v_names), 2, "length of list of names of Volcano should be 2. actual: %s " % len(v_names) )


  def test_checkMismatchedLayerTriplesFail(self):
        """This test should store a couple of triples for a fictional 'neogeo' extension layer, and fail to find it when looking in another layer."""
        log.info("test_checkMismatchedLayerTriplesFail bypassed as 'Unit' now redundant")

        return 
      
        u_Volcano = Unit.GetUnit("Volcano", createp=True)
        p_name = Unit.GetUnit("name", createp=True)
        Triple.AddTripleText(u_Volcano, p_name, "foo", "neogeo")#   , "neogeo") # last arg is 'layer' aka extension
        Triple.AddTripleText(u_Volcano, p_name, "bar", "neogeo")#   , "neogeo") # can we add two triples w/ same property?
        try:
            v_names = GetTargets( p_name, u_Volcano, layers='core' )
            log.info("Looking for: Volcano's 'name' property values, 'foo' and 'bar'. counted: %s" % len(v_names) )
            for vn in v_names:
               log.debug("Found a Volcano 'name' value: %s " % vn)
        except Exception as e:
            log.info("Failed volcano lookup. %s " % e)

        self.assertFalse ( "foo" in v_names and "bar" in v_names, "Layer mismatch - should NOT have foo and bar in name list: %s " % ",".join(v_names)   )
        self.assertEqual(len(v_names), 0, "layer mismatch - length of list of names of Volcano should be 0. actual: %s " % len(v_names) )


class SchemaBasicAPITestCase(unittest.TestCase):

  def setUp(self):
     load_schema_definitions()
     self.schemasInitialized = schemasInitialized

  def test_schemasInitialized(self):
     self.assertEqual(self.schemasInitialized,True, "Schemas should be initialized during setup.")
  
  def test_extensionsLoaded(self):
     global extensionsLoaded, extensionLoadErrors

     if not extensionsLoaded: #Will error if called more than once
         read_extensions([ 'admin', 'auto', 'bib' ])
         
     if len(extensionLoadErrors) > 0:
         log.info("Extension load errors:\n%s" % extensionLoadErrors)

     self.assertEqual(len(extensionLoadErrors),0, "Extension schemas reporting errors.")
     
  def test_gotThing(self):

     thing = VTerm.getTerm("Thing")
     if thing is None:
       gotThing = False
     else:
       gotThing = True

     self.assertEqual( gotThing, True, "Thing node should be accessible via GetUnit('Thing').")

  def test_hostInfo(self):
#      Note This test will fail if setInTestHarness(True) has not been called!!!!!

      thing = Unit.GetUnit("Thing")
      u = ShowUnit()
      u.setupHostinfo(thing,"localhost")
      self.assertEqual( getHostExt(), "", "host_ext should be empty for host localhost.")
      self.assertEqual( getBaseHost(), "localhost", "baseHost should be 'schema.org' for host schema.org.")
      self.assertEqual( getHostPort(), "80", "HostPort should be '80' for host localhost.")
      self.assertEqual( makeUrl("tst", full=True), "http://tst.localhost", "URL should be 'http://tst.localhost' for host localhost.")
      
      u.setupHostinfo(thing,"bib.localhost")
      self.assertEqual( getHostExt(), "bib", "host_ext should be 'bib' for host bib.localhost.")
      self.assertEqual( getBaseHost(), "localhost", "baseHost should be 'localhost' for host bib.localhost.")
      self.assertEqual( getHostPort(), "80", "HostPort should be '80' for host localhost.")
      self.assertEqual( makeUrl("tst",full=True), "http://tst.localhost", "URL should be 'http://tst.localhost' for host bib.localhost.")

      u.setupHostinfo(thing,"bib.localhost:8080")
      self.assertEqual( getHostExt(), "bib", "host_ext should be 'bib' for host bib.localhost:8080.")
      self.assertEqual( getBaseHost(), "localhost", "baseHost should be 'localhost' for host bib.localhost:8080.")
      self.assertEqual( getHostPort(), "8080", "HostPort should be '8080' for host bib.localhost:8080.")
      self.assertEqual( makeUrl("tst",full=True), "http://tst.localhost:8080", "URL should be 'http://tst.localhost:8080' for host bib.localhost:8080.")

      u.setupHostinfo(thing,"fred.localhost:8080")
      self.assertEqual( getHostExt(), "", "host_ext should be empty for host fred.localhost:8080.")
      self.assertEqual( getBaseHost(), "localhost", "baseHost should be 'localhost' for host fred.localhost:8080.")
      self.assertEqual( getHostPort(), "8080", "HostPort should be '8080' for host fred.localhost:8080.")
      self.assertEqual( makeUrl("tst",full=True), "http://tst.localhost:8080", "URL should be 'http://tst.localhost:8080' for host fred.localhost:8080.")

      u.setupHostinfo(thing,"schema.org")
      self.assertEqual( getHostExt(), "", "host_ext should be empty for host schema.org.")
      self.assertEqual( getBaseHost(), "schema.org", "baseHost should be 'schema.org' for host schema.org.")
      self.assertEqual( getHostPort(), "80", "HostPort should be '80' for host schema.org.")
      self.assertEqual( makeUrl("tst",full=True), "http://tst.schema.org", "URL should be 'http://tst.schema.org' for host schema.org.")
      
      u.setupHostinfo(thing,"bib.schema.org")
      self.assertEqual( getHostExt(), "bib", "host_ext should be 'bib' for host bib.schema.org.")
      self.assertEqual( getBaseHost(), "schema.org", "baseHost should be 'bib.schema.org' for host schema.org.")
      self.assertEqual( getHostPort(), "80", "HostPort should be '80' for host bib.schema.org.")
      self.assertEqual( makeUrl("tst",full=True), "http://tst.schema.org", "URL should be 'http://tst.schema.org' for host bib.schema.org.")

      u.setupHostinfo(thing,"fred.schema.org:8080")
      self.assertEqual( getHostExt(), "", "host_ext should be empty for host fred.schema.org:8080.")
      self.assertEqual( getBaseHost(), "schema.org", "baseHost should be 'schema.org' for host fred.schema.org:8080.")
      self.assertEqual( getHostPort(), "8080", "HostPort should be '8080' for host fred.schema.org:8080.")
      self.assertEqual( makeUrl("tst",full=True), "http://tst.schema.org:8080", "URL should be 'http://tst.schema.org:8080' for host fred.schema.org:8080.")

      u.setupHostinfo(thing,"webschemas.org")
      self.assertEqual( getHostExt(), "", "host_ext should be empty for host webschemas.org.")
      self.assertEqual( getBaseHost(), "webschemas.org", "baseHost should be 'webschemas.org' for host webschemas.org.")
      self.assertEqual( getHostPort(), "80", "HostPort should be '80' for host webschemas.org.")
      self.assertEqual( makeUrl("tst",full=True), "http://tst.webschemas.org", "URL should be 'http://tst.webschemas.org' for host webschemas.org.")
      
      u.setupHostinfo(thing,"bib.webschemas.org")
      self.assertEqual( getHostExt(), "bib", "host_ext should be 'bib' for host bib.webschemas.org.")
      self.assertEqual( getBaseHost(), "webschemas.org", "baseHost should be 'webschemas.org' for host bib.webschemas.org.")
      self.assertEqual( getHostPort(), "80", "HostPort should be '80' for host bib.webschemas.org.")
      self.assertEqual( makeUrl("tst",full=True), "http://tst.webschemas.org", "URL should be 'http://tst.webschemas.org' for host bib.webschemas.org.")

      u.setupHostinfo(thing,"fred.webschemas.org:8080")
      self.assertEqual( getHostExt(), "", "host_ext should be empty for host fred.webschemas.org:8080.")
      self.assertEqual( getBaseHost(), "webschemas.org", "baseHost should be 'webschemas.org' for host fred.webschemas.org:8080.")
      self.assertEqual( getHostPort(), "8080", "HostPort should be '8080' for host fred.webschemas.org:8080.")
      self.assertEqual( makeUrl("tst",full=True), "http://tst.webschemas.org:8080", "URL should be 'http://tst.webschemas.org:8080' for host fred.webschemas.org:8080.")
      
      u.setupHostinfo(thing,"sdo-ganymede.appspot.com")
      self.assertEqual( getHostExt(), "", "host_ext should be empty for host sdo-ganymede.appspot.com.")
      self.assertEqual( getBaseHost(), "sdo-ganymede.appspot.com", "baseHost should be 'sdo-ganymede.appspot.com' for host sdo-ganymede.appspot.com.")
      self.assertEqual( getHostPort(), "80", "HostPort should be '80' for host sdo-ganymede.appspot.com.")
      self.assertEqual( makeUrl("tst",full=True), "http://tst.sdo-ganymede.appspot.com", "URL should be 'http://tst.sdo-ganymede.appspot.com' for host sdo-ganymede.appspot.com.")
      
      u.setupHostinfo(thing,"bib.sdo-ganymede.appspot.com")
      self.assertEqual( getHostExt(), "bib", "host_ext should be 'bib' for host bib.sdo-ganymede.appspot.com.")
      self.assertEqual( getBaseHost(), "sdo-ganymede.appspot.com", "baseHost should be 'bib.sdo-ganymede.appspot.com' for host sdo-ganymede.appspot.com.")
      self.assertEqual( getHostPort(), "80", "HostPort should be '80' for host bib.sdo-ganymede.appspot.com.")
      self.assertEqual( makeUrl("tst",full=True), "http://tst.sdo-ganymede.appspot.com", "URL should be 'http://tst.sdo-ganymede.appspot.com' for host bib.sdo-ganymede.appspot.com.")

      #As sdo-ganymede.appspot.com is not in the WORKINGHOSTS list, the unenabled 'fred' extension can not be identified as a false extention & therefore not redirected out of path
      u.setupHostinfo(thing,"fred.sdo-ganymede.appspot.com")
      self.assertEqual( getHostExt(), "", "host_ext should be empty for host fred.sdo-ganymede.appspot.com.")
      self.assertEqual( getBaseHost(), "fred.sdo-ganymede.appspot.com", "baseHost should be 'fred.sdo-ganymede.appspot.com' for host fred.sdo-ganymede.appspot.com.")
      self.assertEqual( getHostPort(), "80", "HostPort should be '80' for host fred.sdo-ganymede.appspot.com.")
      self.assertEqual( makeUrl("tst",full=True), "http://tst.fred.sdo-ganymede.appspot.com", "URL should be 'http://tst.fred.sdo-ganymede.appspot.com' for host fred.sdo-ganymede.appspot.com.")
      

  def test_gotFooBarThing(self):

     foobar = VTerm.getTerm("FooBar")
     if foobar is None:
       gotFooBar = False
     else:
       gotFooBar = True

     self.assertEqual( gotFooBar, False, "Thing node should NOT be accessible via GetUnit('FooBar').")

  def test_NewsArticleIsClass(self):
   # node.isClass
   tNewsArticle = VTerm.getTerm("NewsArticle")
   self.assertTrue(tNewsArticle.isClass(), "NewsArticle is a class.")

  def test_FooBarIsNotClass(self):
    tFooBar = VTerm.getTerm("FooBar")
    try:
      tFooBarIsClass = tFooBar.isClass()
      self.assertFalse(tFooBarIsClass, "FooBar is not a class (should be None)")
      log.info("FooBar:" + str(tFooBar) )
    except:
      log.debug("Failed to get FooBar, as expected. So can't ask it if it isClass().")

  def test_QuantityisClass(self):
    tQuantity = VTerm.getTerm("Quantity")
    self.assertTrue(tQuantity.isClass(), "Quantity is a class.")
    # Note that Quantity is a text type.

  def test_ItemAvailabilityIsEnumeration(self):
    eItemAvailability = VTerm.getTerm("ItemAvailability")
    self.assertTrue(eItemAvailability.isEnumeration(), "ItemAvailability is an Enumeration.")

  def test_FooBarIsNotEnumeration(self):
    eFooBar = VTerm.getTerm("FooBar")
    try:
      self.assertFalse(eFooBar.isEnumeration(), "FooBar is not an Enumeration.")
    except:
      log.debug("GetUnit('FooBar') should fail.")

  def test_EnumerationIsEnumeration(self):
    eEnumeration = VTerm.getTerm("Enumeration")
    self.assertTrue(eEnumeration.isEnumeration(), "Enumeration is an Enumeration type.")

  def test_ArticleSupertypeNewsArticle(self):
    tNewsArticle = VTerm.getTerm("NewsArticle")
    tArticle = VTerm.getTerm("Article")
    self.assertTrue(tNewsArticle.subClassOf(tArticle), "NewsArticle is a sub-type of Article")

  def test_NewsArticleSupertypeArticle(self):
    tNewsArticle = VTerm.getTerm("NewsArticle")
    tArticle = VTerm.getTerm("Article")
    self.assertFalse(tArticle.subClassOf(tNewsArticle), "Article is not a sub-type of NewsArticle")

  def test_ThingSupertypeThing(self):
    tThing = VTerm.getTerm("Thing")
    self.assertTrue(tThing.subClassOf(tThing), "Thing subClassOf Thing.")

  def test_DataTypeSupertypeDataType(self):
    tDataType = VTerm.getTerm("DataType")
    self.assertTrue(tDataType.subClassOf(tDataType), "DataType subClassOf DataType.")

  # TODO: subClassOf() function has "if (self.id == type.id)", investigate how this is used.

  def test_PersonSupertypeThing(self):
    tThing = VTerm.getTerm("Thing")
    tPerson = VTerm.getTerm("Person")
    self.assertTrue(tPerson.subClassOf(tThing), "Person subClassOf Thing.")

  def test_ThingNotSupertypePerson(self):
    tThing = VTerm.getTerm("Thing")
    tPerson = VTerm.getTerm("Person")
    self.assertFalse(tThing.subClassOf(tPerson), "Thing not subClassOf Person.")

  def test_StoreSupertypeLocalBusiness(self):
    tStore = VTerm.getTerm("Store")
    tLocalBusiness = VTerm.getTerm("LocalBusiness")
    self.assertTrue(tStore.subClassOf(tLocalBusiness), "Store subClassOf LocalBusiness.")

  def test_StoresArePlaces(self):
    tStore = VTerm.getTerm("Store")
    tPlace =VTerm.getTerm("Place")
    self.assertTrue(tStore.subClassOf(tPlace), "Store subClassOf Place.")

  def test_StoresAreOrganizations(self):
    tStore = VTerm.getTerm("Store")
    tOrganization = VTerm.getTerm("Organization")
    self.assertTrue(tStore.subClassOf(tOrganization), "Store subClassOf Organization.")

  def test_PersonNotAttribute(self):
    tPerson = VTerm.getTerm("Person")
    self.assertFalse(tPerson.isProperty(), "Not true that Person isAttribute().")

  def test_GetImmediateSubtypesOk(self):
    tArticle = VTerm.getTerm("Article")
    self.assertTrue(VTerm.getTerm("NewsArticle") in tArticle.getSubs(), "NewsArticle is in immediate subtypes of Article.")

  def test_GetImmediateSubtypesWrong(self):
    tArticle = VTerm.getTerm("CreativeWork")
    self.assertFalse(VTerm.getTerm("NewsArticle") in tArticle.getSubs(), "CreativeWork is not in immediate subtypes of Article.")


class SchemaPropertyAPITestCase(unittest.TestCase):

  def test_actorSupersedesActors(self):
    p_actor = VTerm.getTerm("actor")
    p_actors = VTerm.getTerm("actors")
    self.assertTrue(p_actors in p_actor.getSupersedes(), "actor supersedes actors.")

  def test_actorsSuperseded(self):
    p_actors = VTerm.getTerm("actors")
    self.assertTrue(p_actors.superseded(), "actors property has been superseded.")

  def test_actorNotSuperseded(self):
    p_actor = VTerm.getTerm("actor")
    self.assertFalse(p_actor.superseded(), "actor property has not been superseded.")

  def test_offersNotSuperseded(self):
    p_offers = VTerm.getTerm("offers")
    self.assertFalse(p_offers.superseded(), "offers property has not been superseded.")

  def test_actorNotSupersededByOffers(self):
    p_actor = VTerm.getTerm("actor")
    p_offers = VTerm.getTerm("offers")
    self.assertFalse(p_actor in p_offers.getSupersedes(), "actor property doesn't supersede offers property.")

  def test_offersNotSupersededByActor(self):
    p_actor = VTerm.getTerm("actor")
    p_offers = VTerm.getTerm("offers")
    self.assertFalse(p_offers in p_actor.getSupersedes(), "offers property doesn't supersede actors property.")

# acceptedAnswer subPropertyOf suggestedAnswer .
class SchemaPropertyMetadataTestCase(unittest.TestCase):

  def test_suggestedAnswerSuperproperties(self):
    p_suggestedAnswer = VTerm.getTerm("suggestedAnswer")
    p_acceptedAnswer = VTerm.getTerm("acceptedAnswer")
    self.assertTrue(p_suggestedAnswer == p_acceptedAnswer.getSupers()[0], "acceptedAnswer superproperties(), suggestedAnswer in 0th element of array.")

  def test_acceptedAnswerSuperpropertiesArrayLen(self):
    p_acceptedAnswer = VTerm.getTerm("acceptedAnswer")
    aa_supers = p_acceptedAnswer.getSupers()
    for f in aa_supers:
        log.info("acceptedAnswer's subproperties(): %s" % f.id)
    self.assertTrue( len(aa_supers) == 1, "acceptedAnswer subproperties() gives array of len 1. Actual: %s ." % len(aa_supers) )

  def test_answerSubproperty(self):
    p_suggestedAnswer = VTerm.getTerm("suggestedAnswer")
    p_acceptedAnswer = VTerm.getTerm("acceptedAnswer")
    subs = p_suggestedAnswer.getSubs()
    self.assertTrue(p_acceptedAnswer in subs, "acceptedAnswer is a subPropertyOf suggestedAanswer.")

  def test_answerSubproperties(self):
    p_suggestedAnswer = VTerm.getTerm("suggestedAnswer")
    p_acceptedAnswer = VTerm.getTerm("acceptedAnswer")
    self.assertTrue(p_acceptedAnswer == p_suggestedAnswer.getSubs()[0], "suggestedAnswer subproperties(), acceptedAnswer in 0th element of array.")

  def test_answerSubpropertiesArrayLen(self):
    p_suggestedAnswer = VTerm.getTerm("suggestedAnswer")
    log.info("suggestedAnswer array: "+ str(p_suggestedAnswer.getSubs() ))
    self.assertEqual(p_suggestedAnswer.getSubs(), 0, "answer subproperties() gives array of len 1.")

  def test_answerSubpropertiesArrayLen(self):
    p_offers = VTerm.getTerm("offers")
    self.assertEqual(len(p_offers.getSubs()), 0, "offers subproperties() gives array of len 0.")

  def test_alumniSuperproperty(self):
    p_alumni = VTerm.getTerm("alumni")
    p_alumniOf = VTerm.getTerm("alumniOf")
    p_suggestedAnswer = VTerm.getTerm("suggestedAnswer")
    self.assertFalse(p_alumni in p_suggestedAnswer.getSupers(), "not suggestedAnswer subPropertyOf alumni.")
    self.assertFalse(p_suggestedAnswer in p_alumni.getSupers(), "not alumni subPropertyOf suggestedAnswer.")
    self.assertFalse(p_alumni in p_alumni.getSupers(), "not alumni subPropertyOf alumni.")
    self.assertFalse(p_alumniOf in p_alumni.getSupers(), "not alumni subPropertyOf alumniOf.")
    self.assertFalse(p_suggestedAnswer in p_suggestedAnswer.getSupers(), "not suggestedAnswer subPropertyOf suggestedAnswer.")

  def test_alumniInverse(self):
    p_alumni = VTerm.getTerm("alumni")
    p_alumniOf = VTerm.getTerm("alumniOf")
    p_suggestedAnswer = VTerm.getTerm("suggestedAnswer")

    #log.info("alumni: " + str(p_alumniOf.getInverseOf() ))

    self.assertTrue(p_alumni == p_alumniOf.getInverseOf(), "alumniOf inverseOf alumni." )
    self.assertTrue(p_alumniOf == p_alumni.getInverseOf(), "alumni inverseOf alumniOf." )

    self.assertFalse(p_alumni == p_alumni.getInverseOf(), "Not alumni inverseOf alumni." )
    self.assertFalse(p_alumniOf == p_alumniOf.getInverseOf(), "Not alumniOf inverseOf alumniOf." )
    self.assertFalse(p_alumni == p_suggestedAnswer.getInverseOf(), "Not answer inverseOf alumni." )
    # Confirmed informally that the direction asserted doesn't matter currently.
    # Need to add tests that read in custom test-specific schema markup samples to verify this.
    # It is probably best to have redundant inverseOf in the RDFS so that information is visible locally.


    # TODO: http://schema.org/ReserveAction
    # has scheduledTime from apparently two parent types. how can we test against the html ui?

# Simple checks that the schema is not mis-shapen.
# We could do more with SPARQL, but would require rdflib, e.g. sanity check rangeIncludes/domainIncludes with inverseOf

class EnumerationValueTests(unittest.TestCase):

  def test_EventStatusTypeIsEnumeration(self):
    eEventStatusType = VTerm.getTerm("EventStatusType")
    self.assertTrue(eEventStatusType.isEnumeration(), "EventStatusType is an Enumeration.")

  def test_EventStatusTypeIsntEnumerationValue(self):
    eEventStatusType = VTerm.getTerm("EventStatusType")
    self.assertFalse(eEventStatusType.isEnumerationValue(), "EventStatusType is not an Enumeration value.")

  def test_EventCancelledIsEnumerationValue(self):
    eEventCancelled = VTerm.getTerm("EventCancelled")
    self.assertTrue(eEventCancelled.isEnumerationValue(), "EventCancelled is an Enumeration value.")

  def test_EventTotallyFooBarIsntEnumerationValue(self):
    eEventCancelledFB = VTerm.getTerm("EventTotallyFooBar")
    if eEventCancelledFB is not None:
      self.assertFalse(eEventCancelledFB.isEnumerationValue(), "EventTotallyFooBar is not an Enumeration value, not even a node.")
    self.assertTrue(eEventCancelledFB is None, "EventTotallyFooBar should not resolve to a node.")


class SimpleSchemaIntegrityTests(unittest.TestCase):

    #@unittest.expectedFailure # "member and acceptsReservations need work"
    def test_propCommentCount(self):
      prop_comment_errors=[]
      for p in VTerm.getAllProperties():
        comments = p.getComments()
        log.debug("property %s props %s" % (p.getId(), str(len(comments)) ))
        if len(comments) != 1:
          prop_comment_errors.append ("property '%s': Expected 1 rdfs:comment, found: %s.\n %s" % (p.getId(), len(comments), andstr.join(comments) ) )
      log.debug("property comment count: %s\n" % str(len(prop_comment_errors)))
      self.assertEqual(len(prop_comment_errors), 0, "Comment count property errors. Aggregated: \n\n" + " \n\n".join(prop_comment_errors))

    def test_typeCommentCount(self):
      type_comment_errors=[]
      for t in VTerm.getAllTypes():
        comments = t.getComments()
        log.debug(t.getId() + " " + str(len(comments)))
        if len(comments) != 1:
         type_comment_errors.append ("type '%s': Expected 1 rdfs:comment, found: %s.\n %s" % (t.getId(), len(comments), andstr.join(comments) ) )
      log.debug("type comment count: "+ str(len(type_comment_errors)))
      self.assertTrue(len(type_comment_errors)==0, "Comment count type errors. Aggregated: \n" + " \n\n".join(type_comment_errors))

    def test_enumCommentCount(self):
      enum_comment_errors=[]
      for ev in VTerm.getAllEnumerations():
        comments = ev.getGetComments()
        log.debug("enumeration '%s': Expected 1 rdfs:comment, found: %s.\n" % ( ev.getId(), str(len(comments)  )) )
        if len(comments) != 1:
         enum_comment_errors.append ("enumerated value %s: Expected 1 rdfs:comment, found: %s.\n %s" % (e.id, len(comments), andstr.join(comments) ) )
      log.debug("enum comment count: "+ str(len(enum_comment_errors)))
      self.assertTrue(len(enum_comment_errors)==0, "Comment count enumeration errors. Aggregated: \n\n" + " \n".join(enum_comment_errors))

class DataTypeTests(unittest.TestCase):
    def test_booleanDataType(self):
      self.assertTrue(VTerm.getTerm("Boolean").isDataType())
      self.assertTrue(VTerm.getTerm("DataType").isDataType())
      self.assertFalse(VTerm.getTerm("Thing").isDataType())
      self.assertFalse(VTerm.getTerm("Duration").isDataType())

class MarkDownTest(unittest.TestCase):
    def test_emph(self):
        markstring = "This is _em_, __strong__, ___strong em___"
        html = Markdown.parse(markstring,True)
        self.assertFalse(html != "<p>This is <em>em</em>, <strong>strong</strong>, <strong><em>strong em</em></strong></p>\n", "Markdown string not formatted correctly")

class HasMultipleBaseTypesTests(unittest.TestCase):

    def test_localbusiness2supertypes(self):
        fred = "LocalBusiness" 
        self.assertTrue( HasMultipleBaseTypes( fred ) , "LocalBusiness is subClassOf Place + Organization." )

    def test_restaurant_non_multiple_supertypes(self):
        fred = "Restaurant" 
        self.assertFalse( HasMultipleBaseTypes( fred ) , "Restaurant only has one *direct* supertype.")

    def test_article_non_multiple_supertypes(self):
        fred = "Article"
        self.assertFalse( HasMultipleBaseTypes( fred ) , "Article only has one direct supertype.")

class BasicJSONLDTests(unittest.TestCase):

    def test_jsonld_basic_jsonld_context_available(self):
       import json
       ctx = json.loads(GetJsonLdContext())
       self.assertEqual( ctx["@context"]["@vocab"], "http://schema.org/", "Context file should declare schema.org url.")

    def test_issuedBy_jsonld(self):
       import json
       ctx = json.loads(GetJsonLdContext())
       self.assertTrue( "issuedBy" in ctx["@context"] , "issuedBy should be defined." )

    def test_dateModified_jsonld(self):
       import json
       ctx = json.loads(GetJsonLdContext())
       
       self.assertTrue( "dateModified" in ctx["@context"] , "dateModified should be defined." )
       self.assertTrue( ctx["@context"]["dateModified"]["@type"] == "Date" , "dateModified should have Date type." )

class AdvancedJSONLDTests(unittest.TestCase):

    def test_sameas_jsonld(self):
       import json
       ctx = json.loads(GetJsonLdContext())
       self.assertTrue( "sameAs" in ctx["@context"] , "sameAs should be defined." )

#      self.assertTrue( HasMultipleBaseTypes( Unit.GetUnit("LocalBusiness") ) , "LocalBusiness is subClassOf Place + Organization." )


class TraverseTreeTests(unittest.TestCase):
    
    def test_html_tree(self):
        uThing = VTerm.getTerm("Thing")
        mainroot = TypeHierarchyTree("local_label")
        mainroot.traverseForHTML(uThing, layers="core", idprefix="C.")
        html = mainroot.toHTML()
        self.assertTrue( html != None and len(html) > 0, "traverseForHTML should return content")

    def test_jsonld_tree(self):
        uThing = VTerm.getTerm("Thing")
        mainroot = TypeHierarchyTree()
        mainroot.traverseForJSONLD(uThing, layers="core")
        thing_tree = mainroot.toJSON()
        self.assertTrue( thing_tree != None and len(thing_tree) > 0, "traverseForJSONLD should return content")


# TODO: Unwritten tests
#
# * different terms should not have identical comments
# * if x and y are inverseOf each other, the rangeIncludes types on x should be domainIncludes on y, and vice-versa.
# * need a few supporting functions e.g. all terms, all types, all properties, all enum values; candidates for api later but just use here first.
# * make sure terms match their labels (e.g. priceRange), with or without whitespace?
# * check we don't assign more than one example to the same ID

if __name__ == "__main__":
    unittest.main()
