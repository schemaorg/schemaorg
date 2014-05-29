import unittest
import os
import logging # https://docs.python.org/2/library/logging.html#logging-levels

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
    log.debug("Root element of schema file: "+ rootElem.tag)
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

     foobar = Unit.GetUnit("FooBar")
     if foobar is None:
       gotFooBar = False
     else:
       gotFooBar = True

     self.assertEqual( gotFooBar, False, "Thing node should NOT be accessible via GetUnit('FooBar').")

  def test_NewsArticleIsClass(self):
   # node.isClass
   tNewsArticle = Unit.GetUnit("NewsArticle")
   self.assertTrue(tNewsArticle.isClass(), "NewsArticle is a class.")

  def test_FooBarIsNotClass(self):
    tFooBar = Unit.GetUnit("FooBar")
    try:
      tFooBarIsClass = tFooBar.isClass()
      self.assertFalse(tFooBarIsClass, "FooBar is not a class (should be None)")
      log.info("FooBar:" + str(tFooBar) )
    except:
      log.debug("Failed to get FooBar, as expected. So can't ask it if it isClass().")

  def test_QuantityisClass(self):
    tQuantity = Unit.GetUnit("Quantity")
    self.assertTrue(tQuantity.isClass(), "Quantity is a class.")
    # Note that Quantity is a text type.

  def test_ItemAvailabilityIsEnumeration(self):
    eItemAvailability = Unit.GetUnit("ItemAvailability")
    self.assertTrue(eItemAvailability.isEnumeration(), "ItemAvailability is an Enumeration.")

  def test_FooBarIsNotEnumeration(self):
    eFooBar = Unit.GetUnit("FooBar")
    try:
      self.assertFalse(eFooBar.isEnumeration(), "FooBar is not an Enumeration.")
    except:
      log.debug("GetUnit('FooBar') should fail.")

  def test_EnumerationIsEnumeration(self):
    eEnumeration = Unit.GetUnit("Enumeration")
    self.assertTrue(eEnumeration.isEnumeration(), "Enumeration is an Enumeration type.")

  def test_ArticleSupertypeNewsArticle(self):
    tNewsArticle = Unit.GetUnit("NewsArticle")
    tArticle = Unit.GetUnit("Article")
    self.assertTrue(tNewsArticle.subClassOf(tArticle), "NewsArticle is a sub-type of Article")

  def test_NewsArticleSupertypeArticle(self):
    tNewsArticle = Unit.GetUnit("NewsArticle")
    tArticle = Unit.GetUnit("Article")
    self.assertFalse(tArticle.subClassOf(tNewsArticle), "Article is not a sub-type of NewsArticle")

  def test_ThingSupertypeThing(self):
    tThing = Unit.GetUnit("Thing")
    self.assertTrue(tThing.subClassOf(tThing), "Thing subClassOf Thing.")

  def test_DataTypeSupertypeDataType(self):
    tDataType = Unit.GetUnit("DataType")
    self.assertTrue(tDataType.subClassOf(tDataType), "DataType subClassOf DataType.")

  def test_PersonSupertypeThing(self):
    tThing = Unit.GetUnit("Thing")
    tPerson = Unit.GetUnit("Person")
    self.assertTrue(tPerson.subClassOf(tThing), "Person subClassOf Thing.")

  def test_ThingNotSupertypePerson(self):
    tThing = Unit.GetUnit("Thing")
    tPerson = Unit.GetUnit("Person")
    self.assertFalse(tThing.subClassOf(tPerson), "Thing not subClassOf Person.")

  def test_StoreSupertypeLocalBusiness(self):
    tStore = Unit.GetUnit("Store")
    tLocalBusiness = Unit.GetUnit("LocalBusiness")
    self.assertTrue(tStore.subClassOf(tLocalBusiness), "Store subClassOf LocalBusiness.")

  def test_StoresArePlaces(self):
    tStore = Unit.GetUnit("Store")
    tPlace = Unit.GetUnit("Place")
    self.assertTrue(tStore.subClassOf(tPlace), "Store subClassOf Place.")

  def test_StoresAreOrganizations(self):
    tStore = Unit.GetUnit("Store")
    tOrganization = Unit.GetUnit("Organization")
    self.assertTrue(tStore.subClassOf(tOrganization), "Store subClassOf Organization.")

  def test_PersonNotAttribute(self):
    tPerson = Unit.GetUnit("Person")
    self.assertFalse(tPerson.isAttribute(), "Not true that Person isAttribute().")

class SchemaPropertyAPITestCase(unittest.TestCase):

  def test_actorSupercedesActors(self):
    p_actor = Unit.GetUnit("actor")
    p_actors = Unit.GetUnit("actors")
    self.assertTrue(p_actors == p_actor.supercedes(), "actor supercedes actors.")

  def test_actorsSuperceded(self):
    p_actors = Unit.GetUnit("actors")
    self.assertTrue(p_actors.superceded(), "actors property has been superceded.")

  def test_actorNotSuperceded(self):
    p_actor = Unit.GetUnit("actor")
    self.assertFalse(p_actor.superceded(), "actor property has not been superceded.")

  def test_offersNotSuperceded(self):
    p_offers = Unit.GetUnit("offers")
    self.assertFalse(p_offers.superceded(), "offers property has not been superceded.")

  def test_actorNotSupercededByOffers(self):
    p_actor = Unit.GetUnit("actor")
    p_offers = Unit.GetUnit("offers")
    self.assertFalse(p_actor == p_offers.supercedes(), "actor property doesn't supercede offers property.")

  def test_offersNotSupercededByActor(self):
    p_actor = Unit.GetUnit("actor")
    p_offers = Unit.GetUnit("offers")
    self.assertFalse(p_offers == p_actor.supercedes(), "offers property doesn't supercede actors property.")

class SchemaPropertyMetadataTestCase(unittest.TestCase):

  # suggestedAnswer subPropertyOf answer .

  def test_suggestedAnswerSuperproperty(self):
    p_answer = Unit.GetUnit("answer")
    p_suggestedAnswer = Unit.GetUnit("suggestedAnswer")
    self.assertTrue(p_answer == p_suggestedAnswer.superproperty(), "suggestedAnswer subPropertyOf answer.")

  def test_answerSubproperty(self):
    p_answer = Unit.GetUnit("answer")
    p_suggestedAnswer = Unit.GetUnit("suggestedAnswer")
    self.assertTrue(p_suggestedAnswer == p_answer.subproperty(), "suggestedAnswer subPropertyOf answer.")

  def test_alumniSuperproperty(self):
    p_alumni = Unit.GetUnit("alumni")
    p_alumniOf = Unit.GetUnit("alumniOf")
    p_suggestedAnswer = Unit.GetUnit("suggestedAnswer")
    self.assertFalse(p_alumni == p_suggestedAnswer.superproperty(), "not suggestedAnswer subPropertyOf alumni.")
    self.assertFalse(p_suggestedAnswer == p_alumni.superproperty(), "not alumni subPropertyOf suggestedAnswer.")
    self.assertFalse(p_alumni == p_alumni.superproperty(), "not alumni subPropertyOf alumni.")
    self.assertFalse(p_alumniOf == p_alumni.superproperty(), "not alumni subPropertyOf alumniOf.")
    self.assertFalse(p_suggestedAnswer == p_suggestedAnswer.superproperty(), "not suggestedAnswer subPropertyOf suggestedAnswer.")

  def test_alumniInverse(self):
    p_alumni = Unit.GetUnit("alumni")
    p_alumniOf = Unit.GetUnit("alumniOf")
    p_answer = Unit.GetUnit("answer")

    log.info("alumni: " + str(p_alumniOf.inverseproperty() ))

    self.assertTrue(p_alumni == p_alumniOf.inverseproperty(), "alumniOf inverseOf alumni." )
    self.assertTrue(p_alumniOf == p_alumni.inverseproperty(), "alumni inverseOf alumniOf." )

    self.assertFalse(p_alumni == p_alumni.inverseproperty(), "Not alumni inverseOf alumni." )
    self.assertFalse(p_alumniOf == p_alumniOf.inverseproperty(), "Not alumniOf inverseOf alumniOf." )
    self.assertFalse(p_alumni == p_answer.inverseproperty(), "Not answer inverseOf alumni." )
    # Confirmed informally that the direction asserted doesn't matter currently.
    # Need to add tests that read in custom test-specific schema markup samples to verify this.
    # It is probably best to have redundant inverseOf in the RDFS so that information is visible locally.


if __name__ == "__main__":
  unittest.main()
