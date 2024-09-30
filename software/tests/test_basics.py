#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# Import standard python libraries
import sys
import os
import os
import json
import unittest
import logging

# Import schema.org libraries
if not os.getcwd() in sys.path:
    sys.path.insert(1, os.getcwd())

import software

import software.SchemaTerms.sdotermsource as sdotermsource
import software.SchemaTerms.sdoterm as sdoterm
import software.SchemaTerms.localmarkdown as localmarkdown
import software.SchemaExamples.schemaexamples as schemaexamples

VOCABURI = sdotermsource.SdoTermSource.vocabUri()
TRIPLESFILESGLOB = ["data/*.ttl", "data/ext/*/*.ttl"]
EXAMPLESFILESGLOB = ["data/*examples.txt", "data/ext/*/*examples.txt"]


schema_path = "./data/schema.ttl"
examples_path = "./data/examples.txt"

TYPECOUNT_UPPERBOUND = 1500
TYPECOUNT_LOWERBOUND = 500
CURRENT_CONTEXT_FILE = os.path.join(
    os.getcwd(), "software", "site", "docs", "jsonldcontext.jsonld"
)

log = logging.getLogger(__name__)

sdotermsource.SdoTermSource.loadSourceGraph("default")
schemaexamples.SchemaExamples.loaded()

# Tests to probe the health of both schemas and code.
# Note that known failings can be annotated with @unittest.expectedFailure or @skip("reason...")


class BallparkCountTests(unittest.TestCase):
    def test_alltypes(self):
        # ballpark estimates.
        type_range = range(TYPECOUNT_LOWERBOUND, TYPECOUNT_UPPERBOUND)
        self.assertIn(len(sdotermsource.SdoTermSource.getAllTypes()), type_range)


class SDOBasicsTestCase(unittest.TestCase):
    def test_ExtractedPlausibleNumberOfExamples(self):
        example_count = schemaexamples.SchemaExamples.count()
        log.info("Extracted %s examples." % example_count)
        example_range = range(200, 600)
        self.assertIn(
            example_count,
            example_range,
            msg="Expected extraction of %s examples, found %d"
            % (example_range, example_count),
        )


class SupertypePathsTestCase(unittest.TestCase):
    """
    tRestaurant = VTerm.getTerm("Restaurant")
    tThing = VTerm.getTerm("Thing")
    for path in GetParentPathTo(tRestaurant, tThing ):
      pprint.pprint(', '.join([str(x.id) for x in path ]))"""

    def test_simplePath(self):
        self.assertEqual(
            len(sdotermsource.SdoTermSource.getParentPathTo("CreativeWork", "Thing")),
            1,
            "1 supertype path from CreativeWork to Thing.",
        )

    def test_dualPath(self):
        self.assertEqual(
            len(sdotermsource.SdoTermSource.getParentPathTo("Restaurant", "Thing")),
            2,
            "2 supertype paths from Restaurant to Thing.",
        )

    def test_inverseDualPath(self):
        self.assertEqual(
            len(sdotermsource.SdoTermSource.getParentPathTo("Thing", "Restaurant")),
            0,
            "0 supertype paths from Thing to Restaurant.",
        )


class SchemaBasicAPITestCase(unittest.TestCase):
    def test_gotThing(self):
        self.assertIsNotNone(
            sdotermsource.SdoTermSource.getTerm("Thing"),
            msg="Thing node should be accessible via GetUnit('Thing').",
        )

    def test_gotFooBarThing(self):
        self.assertIsNone(
            sdotermsource.SdoTermSource.getTerm("FooBar"),
            msg="Thing node should NOT be accessible via GetUnit('FooBar').",
        )

    def test_NewsArticleIsType(self):
        # node.isClass
        tNewsArticle = sdotermsource.SdoTermSource.getTerm("NewsArticle")
        self.assertEqual(
            tNewsArticle.termType, sdoterm.SdoTermType.TYPE, "NewsArticle is a class."
        )

    def test_QuantityisClass(self):
        tQuantity = sdotermsource.SdoTermSource.getTerm("Quantity")
        self.assertTrue(
            tQuantity.termType == sdoterm.SdoTermType.TYPE, "Quantity is a class."
        )
        # Note that Quantity is a text type.

    def test_ItemAvailabilityIsEnumeration(self):
        eItemAvailability = sdotermsource.SdoTermSource.getTerm("ItemAvailability")
        self.assertEqual(
            eItemAvailability.termType,
            sdoterm.SdoTermType.ENUMERATION,
            "ItemAvailability is an Enumeration.",
        )

    def test_EnumerationIsEnumeration(self):
        eEnumeration = sdotermsource.SdoTermSource.getTerm("Enumeration")
        self.assertEqual(
            eEnumeration.termType,
            sdoterm.SdoTermType.ENUMERATION,
            "Enumeration is an Enumeration type.",
        )

    def test_ArticleSupertypeNewsArticle(self):
        tArticle = sdotermsource.SdoTermSource.getTerm("Article")
        self.assertTrue(
            "NewsArticle" in tArticle.subs, "NewsArticle is a sub-type of Article"
        )

    def test_NewsArticleSupertypeArticle(self):
        tNewsArticle = sdotermsource.SdoTermSource.getTerm("NewsArticle")
        # tArticle = sdoterm.SdoTermSource.getTerm("Article")
        self.assertNotIn(
            "Article", tNewsArticle.subs, "Article is not a sub-type of NewsArticle"
        )

    def test_ThingSupertypeThing(self):
        tThing = sdotermsource.SdoTermSource.getTerm("Thing")
        self.assertNotIn("Thing", tThing.subs, "Thing subClassOf Thing.")

    def test_DataTypeSupertypeDataType(self):
        tDataType = sdotermsource.SdoTermSource.getTerm("DataType")
        self.assertNotIn("DataType", tDataType.subs, "DataType subClassOf DataType.")

    # TODO: subClassOf() function has "if (self.id == type.id)", investigate how this is used.

    def test_PersonSupertypeThing(self):
        tThing = sdotermsource.SdoTermSource.getTerm("Thing")
        self.assertIn("Person", tThing.subs, "Person subClassOf Thing.")

    def test_ThingNotSupertypePerson(self):
        tPerson = sdotermsource.SdoTermSource.getTerm("Person")
        self.assertNotIn("Thing", tPerson.subs, "Thing not subClassOf Person.")

    def test_StoreSupertypeLocalBusiness(self):
        self.assertTrue(
            sdotermsource.SdoTermSource.subClassOf("Store", "LocalBusiness"),
            "Store subClassOf LocalBusiness.",
        )

    def test_StoresArePlaces(self):
        self.assertTrue(
            sdotermsource.SdoTermSource.subClassOf("Store", "Place"),
            "Store subClassOf Place.",
        )

    def test_StoresAreOrganizations(self):
        self.assertTrue(
            sdotermsource.SdoTermSource.subClassOf("Store", "Organization"),
            "Store subClassOf Organization.",
        )

    def test_PersonNotAttribute(self):
        tPerson = sdotermsource.SdoTermSource.getTerm("Person")
        self.assertFalse(
            tPerson.termType == sdoterm.SdoTermType.PROPERTY,
            "Not true that Person isAttribute().",
        )

    def test_GetImmediateSubtypesOk(self):
        tArticle = sdotermsource.SdoTermSource.getTerm("Article")
        self.assertIn(
            "NewsArticle",
            tArticle.subs,
            "NewsArticle is in immediate subtypes of Article.",
        )

    def test_GetImmediateSubtypesWrong(self):
        tArticle = sdotermsource.SdoTermSource.getTerm("CreativeWork")
        self.assertNotIn(
            "NewsArticle",
            tArticle.subs,
            "CreativeWork is not in immediate subtypes of Article.",
        )


class SchemaPropertyAPITestCase(unittest.TestCase):
    def test_actorSupersedesActors(self):
        p_actor = sdotermsource.SdoTermSource.getTerm("actor")
        self.assertIn("actors", p_actor.supersedes, "actor supersedes actors.")

    def test_actorsSuperseded(self):
        p_actors = sdotermsource.SdoTermSource.getTerm("actors")
        self.assertTrue(
            p_actors.superseded,
            "actors property has been superseded.%s %s"
            % (p_actors.superseded, p_actors.supersededBy),
        )

    def test_actorNotSuperseded(self):
        p_actor = sdotermsource.SdoTermSource.getTerm("actor")
        self.assertFalse(p_actor.superseded, "actor property has not been superseded.")

    def test_offersNotSuperseded(self):
        p_offers = sdotermsource.SdoTermSource.getTerm("offers")
        self.assertFalse(
            p_offers.superseded, "offers property has not been superseded."
        )

    def test_actorNotSupersededByOffers(self):
        p_offers = sdotermsource.SdoTermSource.getTerm("offers")
        self.assertNotIn(
            "actor",
            p_offers.supersedes,
            msg="actor property doesn't supersede offers property.",
        )

    def test_offersNotSupersededByActor(self):
        p_actor = sdotermsource.SdoTermSource.getTerm("actor")
        self.assertNotIn(
            "offers",
            p_actor.supersedes,
            msg="offers property doesn't supersede actors property.",
        )


# acceptedAnswer subPropertyOf suggestedAnswer .
class SchemaPropertyMetadataTestCase(unittest.TestCase):
    def test_suggestedAnswerSuperproperties(self):
        p_acceptedAnswer = sdotermsource.SdoTermSource.getTerm("acceptedAnswer")
        self.assertIn(
            "suggestedAnswer",
            p_acceptedAnswer.supers[0],
            msg="acceptedAnswer superproperties(), suggestedAnswer in 0th element of array.",
        )

    def test_acceptedAnswerSuperpropertiesArrayLen(self):
        p_acceptedAnswer = sdotermsource.SdoTermSource.getTerm("acceptedAnswer")
        aa_supers = p_acceptedAnswer.supers
        # for f in aa_supers:
        # log.info("acceptedAnswer's subproperties(): %s" % f)
        self.assertEqual(
            len(aa_supers),
            1,
            msg="acceptedAnswer subproperties() gives array of len 1. Actual: %s ."
            % len(aa_supers),
        )

    def test_answerSubproperty(self):
        p_suggestedAnswer = sdotermsource.SdoTermSource.getTerm("suggestedAnswer")
        self.assertIn(
            "acceptedAnswer",
            p_suggestedAnswer.subs,
            msg="acceptedAnswer is a subPropertyOf suggestedAanswer.",
        )

    def test_answerSubproperties(self):
        p_suggestedAnswer = sdotermsource.SdoTermSource.getTerm("suggestedAnswer")
        self.assertEqual(
            "acceptedAnswer",
            p_suggestedAnswer.subs[0],
            msg="suggestedAnswer subproperties(), acceptedAnswer in 0th element of array.",
        )

    def test_answerSubpropertiesArrayLen(self):
        p_suggestedAnswer = sdotermsource.SdoTermSource.getTerm("suggestedAnswer")
        log.info("suggestedAnswer array: " + str(p_suggestedAnswer.subs))
        self.assertEqual(
            p_suggestedAnswer.subs, 0, "answer subproperties() gives array of len 1."
        )

    def test_answerSubpropertiesArrayLen(self):
        p_offers = sdotermsource.SdoTermSource.getTerm("offers")
        self.assertEqual(
            len(p_offers.subs), 0, "offers subproperties() gives array of len 0."
        )

    def test_alumniSuperproperty(self):
        p_alumni = sdotermsource.SdoTermSource.getTerm("alumni")
        p_suggestedAnswer = sdotermsource.SdoTermSource.getTerm("suggestedAnswer")
        self.assertNotIn(
            "alumni",
            p_suggestedAnswer.supers,
            msg="not suggestedAnswer subPropertyOf alumni.",
        )
        self.assertNotIn(
            "suggestedAnswer",
            p_alumni.supers,
            msg="not alumni subPropertyOf suggestedAnswer.",
        )
        self.assertNotIn(
            "alumni", p_alumni.supers, msg="not alumni subPropertyOf alumni."
        )
        self.assertNotIn(
            "alumniOf", p_alumni.supers, msg="not alumni subPropertyOf alumniOf."
        )
        self.assertNotIn(
            "suggestedAnswer",
            p_suggestedAnswer.supers,
            msg="not suggestedAnswer subPropertyOf suggestedAnswer.",
        )

    def test_alumniInverse(self):
        p_alumni = sdotermsource.SdoTermSource.getTerm("alumni")
        p_alumniOf = sdotermsource.SdoTermSource.getTerm("alumniOf")
        p_suggestedAnswer = sdotermsource.SdoTermSource.getTerm("suggestedAnswer")

        # log.info("alumni: " + str(p_alumniOf.getInverseOf() ))

        self.assertEqual("alumni", p_alumniOf.inverse, msg="alumniOf inverseOf alumni.")
        self.assertEqual("alumniOf", p_alumni.inverse, msg="alumni inverseOf alumniOf.")

        self.assertNotEqual(
            "alumni", p_alumni.inverse, msg="Not alumni inverseOf alumni."
        )
        self.assertNotEqual(
            "alumniOf", p_alumniOf.inverse, msg="Not alumniOf inverseOf alumniOf."
        )
        self.assertNotEqual(
            "alumni", p_suggestedAnswer.inverse, msg="Not answer inverseOf alumni."
        )
        # Confirmed informally that the direction asserted doesn't matter currently.
        # Need to add tests that read in custom test-specific schema markup samples to verify this.
        # It is probably best to have redundant inverseOf in the RDFS so that information is visible locally.

        # TODO: http://schema.org/ReserveAction
        # has scheduledTime from apparently two parent types. how can we test against the html ui?


# Simple checks that the schema is not mis-shapen.
# We could do more with SPARQL, but would require rdflib, e.g. sanity check rangeIncludes/domainIncludes with inverseOf


class EnumerationValueTests(unittest.TestCase):
    def test_EventStatusTypeIsEnumeration(self):
        eEventStatusType = sdotermsource.SdoTermSource.getTerm("EventStatusType")
        self.assertEqual(
            eEventStatusType.termType,
            sdoterm.SdoTermType.ENUMERATION,
            msg="EventStatusType is an Enumeration.",
        )

    def test_EventStatusTypeIsntEnumerationValue(self):
        eEventStatusType = sdotermsource.SdoTermSource.getTerm("EventStatusType")
        self.assertNotEqual(
            eEventStatusType.termType,
            sdoterm.SdoTermType.ENUMERATIONVALUE,
            msg="EventStatusType is not an Enumeration value.",
        )

    def test_EventCancelledIsEnumerationValue(self):
        eEventCancelled = sdotermsource.SdoTermSource.getTerm("EventCancelled")
        self.assertEqual(
            eEventCancelled.termType,
            sdoterm.SdoTermType.ENUMERATIONVALUE,
            msg="EventCancelled is an Enumeration value.",
        )


class DataTypeTests(unittest.TestCase):
    def test_booleanDataType(self):
        self.assertEqual(
            sdotermsource.SdoTermSource.getTerm("Boolean").termType,
            sdoterm.SdoTermType.DATATYPE,
        )
        self.assertEqual(
            sdotermsource.SdoTermSource.getTerm("DataType").termType,
            sdoterm.SdoTermType.DATATYPE,
        )
        self.assertNotEqual(
            sdotermsource.SdoTermSource.getTerm("Thing").termType,
            sdoterm.SdoTermType.DATATYPE,
        )
        self.assertNotEqual(
            sdotermsource.SdoTermSource.getTerm("Duration").termType,
            sdoterm.SdoTermType.DATATYPE,
        )


class MarkDownTest(unittest.TestCase):
    def test_emph(self):
        markstring = "This is _em_, __strong__, ___strong em___"
        html = localmarkdown.Markdown.parse(markstring, True)
        self.assertMultiLineEqual(
            html,
            "<p>This is <em>em</em>, <strong>strong</strong>, <strong><em>strong em</em></strong></p>\n",
            "Markdown string not formatted correctly",
        )


class HasMultipleBaseTypesTests(unittest.TestCase):
    def test_localbusiness2supertypes(self):
        fred = sdotermsource.SdoTermSource.getTerm("LocalBusiness")
        self.assertGreater(
            len(fred.supers), 1, msg="LocalBusiness is subClassOf Place + Organization."
        )

    def test_restaurant_non_multiple_supertypes(self):
        fred = sdotermsource.SdoTermSource.getTerm("Restaurant")
        self.assertEqual(
            len(fred.supers), 1, msg="Restaurant only has one *direct* supertype."
        )

    def test_article_non_multiple_supertypes(self):
        fred = sdotermsource.SdoTermSource.getTerm("Article")
        self.assertEqual(
            len(fred.supers), 1, msg="Article only has one direct supertype."
        )


class SimpleCommentCountTests(unittest.TestCase):
    def test_zeroCommentCount(self):
        query = (
            """
    SELECT  ?term ?comment WHERE {
            ?term a ?type.
            FILTER NOT EXISTS { ?term rdfs:comment ?comment. }
            FILTER (strStarts(str(?term),"%s"))
      }
      ORDER BY ?term"""
            % VOCABURI
        )

        ndi1_results = sdotermsource.SdoTermSource.query(query)
        if len(ndi1_results) > 0:
            for row in ndi1_results:
                log.warning("Term %s has no rdfs:comment value" % (row["term"]))
        self.assertEqual(
            len(ndi1_results),
            0,
            "Found: %s term(s) without comment value" % len(ndi1_results),
        )

    def test_multiCommentCount(self):
        query = (
            """
    SELECT  ?term ?comment WHERE {
            ?term a ?type;
              rdfs:comment ?comment.
              FILTER (strStarts(str(?term),"%s"))
    }
    GROUP BY ?term
    HAVING (count(DISTINCT ?comment) > 1)
    ORDER BY ?term"""
            % VOCABURI
        )
        ndi1_results = sdotermsource.SdoTermSource.query(query)
        if len(ndi1_results) > 0:
            log.info("Query was: %s" % query)
            for row in ndi1_results:
                log.warning(
                    "Term %s has  rdfs:comment value %s" % (row["term"], row["comment"])
                )
        self.assertEqual(
            len(ndi1_results),
            0,
            "Found: %s term(s) without multiple comment values" % len(ndi1_results),
        )


class BasicJSONLDTests(unittest.TestCase):
    def setUp(self):
        self.ctx = None
        try:
            with open(CURRENT_CONTEXT_FILE) as json_file:
                self.ctx = json.load(json_file)
        except IOError:
            raise unittest.SkipTest(
                "jsonldcontext.json file not loaded - bypassing tests"
            )

    #    @skip("Need to think about this.")
    #    def test_jsonld_basic_jsonld_context_available(self):
    #      if self.ctx:
    #        self.assertEqual( self.ctx["@context"]["@vocab"], "https://schema.org/", "Context file should declare schema.org url.")

    def test_issuedBy_jsonld(self):
        if not self.ctx:
            raise unittest.SkipTest(
                "%s file not loaded - bypassing tests" % CURRENT_CONTEXT_FILE
            )
        self.assertTrue(
            "issuedBy" in self.ctx["@context"], "issuedBy should be defined."
        )

    def test_dateModified_jsonld(self):
        if not self.ctx:
            raise unittest.SkipTest(
                "%s file not loaded - bypassing tests" % CURRENT_CONTEXT_FILE
            )
        self.assertTrue(
            "dateModified" in self.ctx["@context"], "dateModified should be defined."
        )
        self.assertTrue(
            self.ctx["@context"]["dateModified"]["@type"] == "Date",
            "dateModified should have Date type.",
        )

    def test_sameas_jsonld(self):
        if not self.ctx:
            raise unittest.SkipTest(
                "jsonldcontext.json file not loaded - bypassing tests"
            )
        self.assertIn("sameAs", self.ctx["@context"], msg="sameAs should be defined.")


class JsonExampleTests(unittest.TestCase):
    def testAllExamples(self):
        for example in schemaexamples.SchemaExamples.allExamples():
            source_filename = example.getMeta("file")
            with self.subTest(key=example.getKey(), file=source_filename):
                if not example.hasJsonld():
                    continue
                json_source = example.getJsonldRaw()
                try:
                    parsed = json.loads(json_source)
                except json.decoder.JSONDecodeError as json_error:
                    # Display a helpful error message showing where the JSON error is.
                    lines = json_error.doc.split("\n")
                    snippet = (
                        lines[json_error.lineno - 1]
                        + "\n"
                        + "^".rjust(json_error.colno)
                    )
                    # Show up to three lines above the error, often the problem is a missing comma above.
                    if json_error.lineno > 2:
                        for i in range(2, min(json_error.lineno, 5)):
                            snippet = lines[json_error.lineno - i] + "\n" + snippet
                    # Adjust by the offset inside the example file.
                    lineno = json_error.lineno + (example.jsonld_offset or 0)
                    self.fail(
                        "JSON parsing error: '%s' in file %s:%d:%d \n%s"
                        % (
                            json_error.msg,
                            source_filename,
                            lineno,
                            json_error.colno,
                            snippet,
                        )
                    )
                except Exception as exception:
                    self.fail(
                        "Could not parse JSON '%s' error: %s file: %s"
                        % (json_source, exception, source_filename)
                    )


# TODO: Unwritten tests
#
# * different terms should not have identical comments
# * if x and y are inverseOf each other, the rangeIncludes types on x should be domainIncludes on y, and vice-versa.
# * need a few supporting functions e.g. all terms, all types, all properties, all enum values; candidates for api later but just use here first.
# * make sure terms match their labels (e.g. priceRange), with or without whitespace?
# * check we don't assign more than one example to the same ID

if __name__ == "__main__":
    unittest.main()
