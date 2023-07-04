import sys
if not (sys.version_info.major == 3 and sys.version_info.minor > 5):
    print("Python version %s.%s not supported version 3.6 or above required - exiting" % (sys.version_info.major,sys.version_info.minor))
    sys.exit(1)
import os
import json
import unittest
import logging # https://docs.python.org/2/library/logging.html#logging-levels
for path in [os.getcwd(),"software/util","software/SchemaTerms","software/SchemaExamples"]:
  sys.path.insert( 1, path ) #Pickup libs from local  directories

from sdotermsource import SdoTermSource
from sdoterm import *
from schemaexamples import SchemaExamples

VOCABURI = SdoTermSource.vocabUri()
TRIPLESFILESGLOB = ["data/*.ttl","data/ext/*/*.ttl"]
EXAMPLESFILESGLOB = ["data/*examples.txt","data/ext/*/*examples.txt"]


schema_path = './data/schema.ttl'
examples_path = './data/examples.txt'

andstr = "\n AND\n  "
TYPECOUNT_UPPERBOUND = 1500
TYPECOUNT_LOWERBOUND = 500

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


SdoTermSource.loadSourceGraph("default")
print ("loaded %s triples - %s terms" % (len(SdoTermSource.sourceGraph()),len(SdoTermSource.getAllTerms())) )

print("Loading examples files")
SchemaExamples.loadExamplesFiles("default")
print("Loaded %d examples" % SchemaExamples.count())

# Tests to probe the health of both schemas and code.
# Note that known failings can be annotated with @unittest.expectedFailure or @skip("reason...")

class BallparkCountTests(unittest.TestCase):
    def test_alltypes(self):

      # ballpark estimates.
      self.assertTrue( len( SdoTermSource.getAllTypes() )  > TYPECOUNT_LOWERBOUND , "Should be > %d types. Got %s" % (TYPECOUNT_LOWERBOUND, len (SdoTermSource.getAllTypes()) ))
      self.assertTrue( len( SdoTermSource.getAllTypes() )  < TYPECOUNT_UPPERBOUND , "Should be < %d types. Got %s" % (TYPECOUNT_UPPERBOUND, len (SdoTermSource.getAllTypes()) ))


class SDOBasicsTestCase(unittest.TestCase):

  def test_ExtractedPlausibleNumberOfExamples(self):

    example_count = SchemaExamples.count()
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
                  SdoTermSource.getParentPathTo("CreativeWork","Thing")
                  ), 1, "1 supertype path from CreativeWork to Thing."  )

    def test_dualPath(self):
      self.assertEqual(  len(
                  SdoTermSource.getParentPathTo("Restaurant","Thing")
                  ), 2, "2 supertype paths from Restaurant to Thing."  )

    def test_inverseDualPath(self):
      self.assertEqual(  len(
                  SdoTermSource.getParentPathTo("Thing", "Restaurant")
                  ), 0, "0 supertype paths from Thing to Restaurant."  )

class SchemaBasicAPITestCase(unittest.TestCase):

  def test_gotThing(self):

     thing = SdoTermSource.getTerm("Thing")
     if thing is None:
       gotThing = False
     else:
       gotThing = True

     self.assertEqual( gotThing, True, "Thing node should be accessible via GetUnit('Thing').")

  def test_gotFooBarThing(self):

     foobar = SdoTermSource.getTerm("FooBar")
     if foobar is None:
       gotFooBar = False
     else:
       gotFooBar = True

     self.assertEqual( gotFooBar, False, "Thing node should NOT be accessible via GetUnit('FooBar').")

  def test_NewsArticleIsType(self):
   # node.isClass
   tNewsArticle = SdoTermSource.getTerm("NewsArticle")
   self.assertTrue(tNewsArticle.termType == SdoTerm.TYPE, "NewsArticle is a class.")

  def test_QuantityisClass(self):
    tQuantity = SdoTermSource.getTerm("Quantity")
    self.assertTrue(tQuantity.termType == SdoTerm.TYPE, "Quantity is a class.")
    # Note that Quantity is a text type.

  def test_ItemAvailabilityIsEnumeration(self):
    eItemAvailability = SdoTermSource.getTerm("ItemAvailability")
    self.assertTrue(eItemAvailability.termType == SdoTerm.ENUMERATION, "ItemAvailability is an Enumeration.")

  def test_EnumerationIsEnumeration(self):
    eEnumeration = SdoTermSource.getTerm("Enumeration")
    self.assertTrue(eEnumeration.termType == SdoTerm.ENUMERATION, "Enumeration is an Enumeration type.")

  def test_ArticleSupertypeNewsArticle(self):
    #tNewsArticle = SdoTermSource.getTerm("NewsArticle")
    tArticle = SdoTermSource.getTerm("Article")
    self.assertTrue("NewsArticle" in tArticle.subs, "NewsArticle is a sub-type of Article")

  def test_NewsArticleSupertypeArticle(self):
    tNewsArticle = SdoTermSource.getTerm("NewsArticle")
    #tArticle = SdoTermSource.getTerm("Article")
    self.assertFalse("Article" in tNewsArticle.subs, "Article is not a sub-type of NewsArticle")

  def test_ThingSupertypeThing(self):
    tThing = SdoTermSource.getTerm("Thing")
    self.assertFalse("Thing" in tThing.subs, "Thing subClassOf Thing.")

  def test_DataTypeSupertypeDataType(self):
    tDataType = SdoTermSource.getTerm("DataType")
    self.assertFalse("DataType" in tDataType.subs, "DataType subClassOf DataType.")

  # TODO: subClassOf() function has "if (self.id == type.id)", investigate how this is used.

  def test_PersonSupertypeThing(self):
    tThing = SdoTermSource.getTerm("Thing")
    #tPerson = VTerm.getTerm("Person")
    self.assertTrue("Person" in tThing.subs, "Person subClassOf Thing.")

  def test_ThingNotSupertypePerson(self):
    #tThing = VTerm.getTerm("Thing")
    tPerson = SdoTermSource.getTerm("Person")
    self.assertFalse("Thing" in tPerson.subs, "Thing not subClassOf Person.")

  def test_StoreSupertypeLocalBusiness(self):
    self.assertTrue(SdoTermSource.subClassOf("Store","LocalBusiness"), "Store subClassOf LocalBusiness.")

  def test_StoresArePlaces(self):
     self.assertTrue(SdoTermSource.subClassOf("Store","Place"), "Store subClassOf Place.")

  def test_StoresAreOrganizations(self):
     self.assertTrue(SdoTermSource.subClassOf("Store","Organization"), "Store subClassOf Organization.")

  def test_PersonNotAttribute(self):
    tPerson = SdoTermSource.getTerm("Person")
    self.assertFalse(tPerson.termType == SdoTerm.PROPERTY, "Not true that Person isAttribute().")

  def test_GetImmediateSubtypesOk(self):
    tArticle = SdoTermSource.getTerm("Article")
    self.assertTrue("NewsArticle" in tArticle.subs, "NewsArticle is in immediate subtypes of Article.")

  def test_GetImmediateSubtypesWrong(self):
    tArticle = SdoTermSource.getTerm("CreativeWork")
    self.assertFalse("NewsArticle" in tArticle.subs, "CreativeWork is not in immediate subtypes of Article.")


class SchemaPropertyAPITestCase(unittest.TestCase):

  def test_actorSupersedesActors(self):
    p_actor = SdoTermSource.getTerm("actor")
    self.assertTrue("actors" in p_actor.supersedes, "actor supersedes actors.")

  def test_actorsSuperseded(self):
    p_actors = SdoTermSource.getTerm("actors")
    self.assertTrue(p_actors.superseded, "actors property has been superseded.%s %s" % (p_actors.superseded,p_actors.supersededBy))

  def test_actorNotSuperseded(self):
    p_actor = SdoTermSource.getTerm("actor")
    self.assertFalse(p_actor.superseded, "actor property has not been superseded.")

  def test_offersNotSuperseded(self):
    p_offers = SdoTermSource.getTerm("offers")
    self.assertFalse(p_offers.superseded, "offers property has not been superseded.")

  def test_actorNotSupersededByOffers(self):
    p_offers = SdoTermSource.getTerm("offers")
    self.assertFalse("actor" in p_offers.supersedes, "actor property doesn't supersede offers property.")

  def test_offersNotSupersededByActor(self):
    p_actor = SdoTermSource.getTerm("actor")
    self.assertFalse("offers" in p_actor.supersedes, "offers property doesn't supersede actors property.")

# acceptedAnswer subPropertyOf suggestedAnswer .
class SchemaPropertyMetadataTestCase(unittest.TestCase):

  def test_suggestedAnswerSuperproperties(self):
    p_acceptedAnswer = SdoTermSource.getTerm("acceptedAnswer")
    self.assertTrue("suggestedAnswer" in p_acceptedAnswer.supers[0], "acceptedAnswer superproperties(), suggestedAnswer in 0th element of array.")

  def test_acceptedAnswerSuperpropertiesArrayLen(self):
    p_acceptedAnswer = SdoTermSource.getTerm("acceptedAnswer")
    aa_supers = p_acceptedAnswer.supers
    #for f in aa_supers:
        #log.info("acceptedAnswer's subproperties(): %s" % f)
    self.assertTrue( len(aa_supers) == 1, "acceptedAnswer subproperties() gives array of len 1. Actual: %s ." % len(aa_supers) )

  def test_answerSubproperty(self):
    p_suggestedAnswer = SdoTermSource.getTerm("suggestedAnswer")
    self.assertTrue("acceptedAnswer" in p_suggestedAnswer.subs, "acceptedAnswer is a subPropertyOf suggestedAanswer.")

  def test_answerSubproperties(self):
    p_suggestedAnswer = SdoTermSource.getTerm("suggestedAnswer")
    self.assertTrue("acceptedAnswer" == p_suggestedAnswer.subs[0], "suggestedAnswer subproperties(), acceptedAnswer in 0th element of array.")

  def test_answerSubpropertiesArrayLen(self):
    p_suggestedAnswer = SdoTermSource.getTerm("suggestedAnswer")
    log.info("suggestedAnswer array: "+ str(p_suggestedAnswer.subs ))
    self.assertEqual(p_suggestedAnswer.subs, 0, "answer subproperties() gives array of len 1.")

  def test_answerSubpropertiesArrayLen(self):
    p_offers = SdoTermSource.getTerm("offers")
    self.assertEqual(len(p_offers.subs), 0, "offers subproperties() gives array of len 0.")

  def test_alumniSuperproperty(self):
    p_alumni = SdoTermSource.getTerm("alumni")
    p_suggestedAnswer = SdoTermSource.getTerm("suggestedAnswer")
    self.assertFalse("alumni" in p_suggestedAnswer.supers, "not suggestedAnswer subPropertyOf alumni.")
    self.assertFalse("suggestedAnswer" in p_alumni.supers, "not alumni subPropertyOf suggestedAnswer.")
    self.assertFalse("alumni" in p_alumni.supers, "not alumni subPropertyOf alumni.")
    self.assertFalse("alumniOf" in p_alumni.supers, "not alumni subPropertyOf alumniOf.")
    self.assertFalse("suggestedAnswer" in p_suggestedAnswer.supers, "not suggestedAnswer subPropertyOf suggestedAnswer.")

  def test_alumniInverse(self):
    p_alumni = SdoTermSource.getTerm("alumni")
    p_alumniOf = SdoTermSource.getTerm("alumniOf")
    p_suggestedAnswer = SdoTermSource.getTerm("suggestedAnswer")

    #log.info("alumni: " + str(p_alumniOf.getInverseOf() ))

    self.assertTrue("alumni" == p_alumniOf.inverse, "alumniOf inverseOf alumni." )
    self.assertTrue("alumniOf" == p_alumni.inverse, "alumni inverseOf alumniOf." )

    self.assertFalse("alumni" == p_alumni.inverse, "Not alumni inverseOf alumni." )
    self.assertFalse("alumniOf" == p_alumniOf.inverse, "Not alumniOf inverseOf alumniOf." )
    self.assertFalse("alumni" == p_suggestedAnswer.inverse, "Not answer inverseOf alumni." )
    # Confirmed informally that the direction asserted doesn't matter currently.
    # Need to add tests that read in custom test-specific schema markup samples to verify this.
    # It is probably best to have redundant inverseOf in the RDFS so that information is visible locally.


    # TODO: http://schema.org/ReserveAction
    # has scheduledTime from apparently two parent types. how can we test against the html ui?

# Simple checks that the schema is not mis-shapen.
# We could do more with SPARQL, but would require rdflib, e.g. sanity check rangeIncludes/domainIncludes with inverseOf

class EnumerationValueTests(unittest.TestCase):

  def test_EventStatusTypeIsEnumeration(self):
    eEventStatusType = SdoTermSource.getTerm("EventStatusType")
    self.assertTrue(eEventStatusType.termType == SdoTerm.ENUMERATION, "EventStatusType is an Enumeration.")

  def test_EventStatusTypeIsntEnumerationValue(self):
    eEventStatusType = SdoTermSource.getTerm("EventStatusType")
    self.assertFalse(eEventStatusType.termType == SdoTerm.ENUMERATIONVALUE, "EventStatusType is not an Enumeration value.")

  def test_EventCancelledIsEnumerationValue(self):
    eEventCancelled = SdoTermSource.getTerm("EventCancelled")
    self.assertTrue(eEventCancelled.termType == SdoTerm.ENUMERATIONVALUE, "EventCancelled is an Enumeration value.")

class DataTypeTests(unittest.TestCase):
    def test_booleanDataType(self):
      self.assertTrue(SdoTermSource.getTerm("Boolean").termType == SdoTerm.DATATYPE )
      self.assertTrue(SdoTermSource.getTerm("DataType").termType == SdoTerm.DATATYPE)
      self.assertFalse(SdoTermSource.getTerm("Thing").termType == SdoTerm.DATATYPE)
      self.assertFalse(SdoTermSource.getTerm("Duration").termType == SdoTerm.DATATYPE)

class MarkDownTest(unittest.TestCase):
    def test_emph(self):
      from localmarkdown import Markdown
      markstring = "This is _em_, __strong__, ___strong em___"
      html = Markdown.parse(markstring,True)
      self.assertFalse(html != "<p>This is <em>em</em>, <strong>strong</strong>, <strong><em>strong em</em></strong></p>\n", "Markdown string not formatted correctly")

class HasMultipleBaseTypesTests(unittest.TestCase):

    def test_localbusiness2supertypes(self):
        fred = SdoTermSource.getTerm("LocalBusiness")
        self.assertTrue( len(fred.supers) > 1 , "LocalBusiness is subClassOf Place + Organization." )

    def test_restaurant_non_multiple_supertypes(self):
        fred = SdoTermSource.getTerm("Restaurant")
        self.assertFalse( len(fred.supers) > 1 , "Restaurant only has one *direct* supertype.")

    def test_article_non_multiple_supertypes(self):
        fred = SdoTermSource.getTerm("Article")
        self.assertFalse( len(fred.supers) > 1  , "Article only has one direct supertype.")

class SimpleCommentCountTests(unittest.TestCase):

  def test_zeroCommentCount(self):
    query = """
    SELECT  ?term ?comment WHERE {
            ?term a ?type.
            FILTER NOT EXISTS { ?term rdfs:comment ?comment. }
            FILTER (strStarts(str(?term),"%s"))
      }
      ORDER BY ?term""" % VOCABURI

    ndi1_results = SdoTermSource.query(query)
    if (len(ndi1_results) > 0):
        for row in ndi1_results:
            log.info("WARNING term %s has no rdfs:comment value" % (row["term"]))
    self.assertEqual(len(ndi1_results), 0,
                    "Found: %s term(s) without comment value" % len(ndi1_results ) )

  def test_multiCommentCount(self):
    query = """
    SELECT  ?term ?comment WHERE {
            ?term a ?type;
              rdfs:comment ?comment.
              FILTER (strStarts(str(?term),"%s"))
    }
    GROUP BY ?term
    HAVING (count(DISTINCT ?comment) > 1)
    ORDER BY ?term""" % VOCABURI
    ndi1_results = SdoTermSource.query(query)
    if (len(ndi1_results) > 0):
          log.info("Query was: %s" % query)
          for row in ndi1_results:
              log.info("WARNING term %s has  rdfs:comment value %s" % (row["term"],row["comment"]))
    self.assertEqual(len(ndi1_results), 0,
        "Found: %s term(s) without multiple comment values" % len(ndi1_results ) )


class BasicJSONLDTests(unittest.TestCase):

    def setUp(self):
      self.ctx = None
      try:
        with open('site/docs/jsonldcontext.json') as json_file:
          self.ctx = json.load(json_file)
      except:
        print("jsonldcontext.json file not loaded - bypassing tests")

#    @skip("Need to think about this.")
#    def test_jsonld_basic_jsonld_context_available(self):
#      if self.ctx:
#        self.assertEqual( self.ctx["@context"]["@vocab"], "https://schema.org/", "Context file should declare schema.org url.")

    def test_issuedBy_jsonld(self):
      if self.ctx:
        self.assertTrue( "issuedBy" in self.ctx["@context"] , "issuedBy should be defined." )

    def test_dateModified_jsonld(self):
      if self.ctx:
        self.assertTrue( "dateModified" in self.ctx["@context"] , "dateModified should be defined." )
        self.assertTrue( self.ctx["@context"]["dateModified"]["@type"] == "Date" , "dateModified should have Date type." )

    def test_sameas_jsonld(self):
       if self.ctx:
        self.assertTrue( "sameAs" in self.ctx["@context"] , "sameAs should be defined." )

#      self.assertTrue( HasMultipleBaseTypes( Unit.GetUnit("LocalBusiness") ) , "LocalBusiness is subClassOf Place + Organization." )


class JsonExampleTests(unittest.TestCase):

  def testAllExamples(self):
    for example in SchemaExamples.allExamples():
      with self.subTest(key=example.getKey(), file=example.getMeta("file")):
        if not example.hasJsonld():
          continue
        json_source = example.getJsonldRaw()
        if 'microdata only' in json_source:
          continue
        if 'No JSON-LD' in json_source:
          continue
        try:
          parsed = json.loads(json_source)
        except Exception as exception:
          self.fail("Could not parse JSON '%s' error: %s file: %s" % (json_source, exception, example.getMeta("file")))

# TODO: Unwritten tests
#
# * different terms should not have identical comments
# * if x and y are inverseOf each other, the rangeIncludes types on x should be domainIncludes on y, and vice-versa.
# * need a few supporting functions e.g. all terms, all types, all properties, all enum values; candidates for api later but just use here first.
# * make sure terms match their labels (e.g. priceRange), with or without whitespace?
# * check we don't assign more than one example to the same ID

if __name__ == "__main__":
    unittest.main()
