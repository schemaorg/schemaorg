import unittest
import os
import logging # https://docs.python.org/2/library/logging.html#logging-levels
import sys
for path in [os.getcwd(),"Util","SchemaPages","SchemaExamples"]:
  sys.path.insert( 1, path ) #Pickup libs from local  directories

from sdotermsource import SdoTermSource 
from sdoterm import *

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


tripfiles = []
for g in TRIPLESFILESGLOB:
  tripfiles.extend(glob.glob(g))
if not len(tripfiles):
  print("No triples file(s) to load")
else:
  SdoTermSource.loadSourceGraph(tripfiles)
  print ("loaded %s triples - %s terms" % (len(SdoTermSource.sourceGraph()),len(SdoTermSource.getAllTerms())) )
  
print("Loading examples files")
exfiles = []
for g in EXAMPLESFILESGLOB:
    exfiles.extend(glob.glob(g))
if not len(exfiles):
    print("No examples file(s) to load")
else:
    SchemaExamples.loadExamplesFiles(exfiles)
    print("Loaded %d examples from  %d examples files" % (SchemaExamples.count(),len(exfiles)))


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
                  SdoTermSource.getParentPathTo("Thing"), "Restaurant")
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
    tNewsArticle = SdoTermSource.getTerm("NewsArticle")
    tArticle = SdoTermSource.getTerm("Article")
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
