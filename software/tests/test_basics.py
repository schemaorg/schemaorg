from __future__ import annotations

import json
import logging
from typing import Any
import unittest

from schemaorg import constants
import SchemaExamples.schemaexamples as schemaexamples
import SchemaTerms.localmarkdown as localmarkdown
import SchemaTerms.sdoterm as sdoterm
import SchemaTerms.sdotermsource as sdotermsource

VOCABURI = sdotermsource.SdoTermSource.vocabUri()

TYPECOUNT_UPPERBOUND = 1500
TYPECOUNT_LOWERBOUND = 500
CURRENT_CONTEXT_FILE = (
    constants.PROJECT_ROOT / "software/site/docs/jsonldcontext.jsonld"
)

log = logging.getLogger(__name__)

EXAMPLES: schemaexamples.SchemaExamples | None = None


def setUpModule() -> None:
    global EXAMPLES
    sdotermsource.SdoTermSource.loadSourceGraph("default")
    EXAMPLES = schemaexamples.SchemaExamples.from_default()


# Tests to probe the health of both schemas and code.
# Note that known failings can be annotated with @unittest.expectedFailure or
# @skip("reason...").


class BallparkCountTests(unittest.TestCase):
    def test_alltypes(self) -> None:
        type_range = range(TYPECOUNT_LOWERBOUND, TYPECOUNT_UPPERBOUND)
        self.assertIn(len(sdotermsource.SdoTermSource.getAllTypes()), type_range)


class SDOBasicsTestCase(unittest.TestCase):
    def test_ExtractedPlausibleNumberOfExamples(self) -> None:
        assert EXAMPLES is not None
        example_count = len(EXAMPLES)
        log.info("Extracted %d examples.", example_count)
        example_range = range(200, 600)
        self.assertIn(
            example_count,
            example_range,
            msg=f"Expected extraction of {example_range} examples, found {example_count}",
        )


class SupertypePathsTestCase(unittest.TestCase):
    def test_simplePath(self) -> None:
        path = sdotermsource.SdoTermSource.getParentPathTo("CreativeWork", "Thing")
        self.assertEqual(len(path), 1, path)

    def test_dualPath(self) -> None:
        path = sdotermsource.SdoTermSource.getParentPathTo("Restaurant", "Thing")
        self.assertEqual(len(path), 2, path)

    def test_inverseDualPath(self) -> None:
        self.assertEqual(
            len(sdotermsource.SdoTermSource.getParentPathTo("Thing", "Restaurant")),
            0,
            "0 supertype paths from Thing to Restaurant.",
        )


class SchemaBasicAPITestCase(unittest.TestCase):
    def test_gotThing(self) -> None:
        self.assertIsNotNone(
            sdotermsource.SdoTermSource.getTerm("Thing"),
            msg="Thing node should be accessible via getTerm('Thing').",
        )

    def test_gotFooBarThing(self) -> None:
        self.assertIsNone(
            sdotermsource.SdoTermSource.getTerm("FooBar"),
            msg="FooBar node should NOT be accessible via getTerm('FooBar').",
        )

    def test_NewsArticleIsType(self) -> None:
        t_news_article = sdotermsource.SdoTermSource.getTerm("NewsArticle")
        self.assertEqual(
            t_news_article.termType, sdoterm.SdoTermType.TYPE, "NewsArticle is a class."
        )

    def test_QuantityisDataType(self) -> None:
        # Quantity is a text-ish DataType.
        t_quantity = sdotermsource.SdoTermSource.getTerm("Quantity")
        self.assertEqual(
            t_quantity.termType,
            sdoterm.SdoTermType.DATATYPE,
            "Quantity is a DataType.",
        )

    def test_ItemAvailabilityIsEnumeration(self) -> None:
        e_item_availability = sdotermsource.SdoTermSource.getTerm("ItemAvailability")
        self.assertEqual(
            e_item_availability.termType,
            sdoterm.SdoTermType.ENUMERATION,
            "ItemAvailability is an Enumeration.",
        )

    def test_EnumerationIsEnumeration(self) -> None:
        e_enumeration = sdotermsource.SdoTermSource.getTerm("Enumeration")
        self.assertEqual(
            e_enumeration.termType,
            sdoterm.SdoTermType.ENUMERATION,
            "Enumeration is an Enumeration type.",
        )

    def test_ArticleSupertypeNewsArticle(self) -> None:
        t_article = sdotermsource.SdoTermSource.getTerm("Article")
        self.assertIn(
            "NewsArticle", t_article.subs.ids, "NewsArticle is a sub-type of Article"
        )

    def test_NewsArticleSupertypeArticle(self) -> None:
        t_news_article = sdotermsource.SdoTermSource.getTerm("NewsArticle")
        self.assertNotIn(
            "Article",
            t_news_article.subs.ids,
            "Article is not a sub-type of NewsArticle",
        )

    def test_ThingSupertypeThing(self) -> None:
        t_thing = sdotermsource.SdoTermSource.getTerm("Thing")
        self.assertNotIn("Thing", t_thing.subs.ids, "Thing subClassOf Thing.")

    def test_DataTypeSupertypeDataType(self) -> None:
        t_datatype = sdotermsource.SdoTermSource.getTerm("DataType")
        self.assertNotIn(
            "DataType", t_datatype.subs.ids, "DataType subClassOf DataType."
        )

    def test_PersonSupertypeThing(self) -> None:
        t_thing = sdotermsource.SdoTermSource.getTerm("Thing")
        self.assertIn("Person", t_thing.subs.ids, "Person subClassOf Thing.")

    def test_ThingNotSupertypePerson(self) -> None:
        t_person = sdotermsource.SdoTermSource.getTerm("Person")
        self.assertNotIn("Thing", t_person.subs.ids, "Thing not subClassOf Person.")

    def test_StoreSupertypeLocalBusiness(self) -> None:
        self.assertTrue(
            sdotermsource.SdoTermSource.subClassOf("Store", "LocalBusiness"),
            "Store subClassOf LocalBusiness.",
        )

    def test_StoresArePlaces(self) -> None:
        self.assertTrue(
            sdotermsource.SdoTermSource.subClassOf("Store", "Place"),
            "Store subClassOf Place.",
        )

    def test_StoresAreOrganizations(self) -> None:
        self.assertTrue(
            sdotermsource.SdoTermSource.subClassOf("Store", "Organization"),
            "Store subClassOf Organization.",
        )

    def test_PersonNotAttribute(self) -> None:
        t_person = sdotermsource.SdoTermSource.getTerm("Person")
        self.assertNotEqual(
            t_person.termType,
            sdoterm.SdoTermType.PROPERTY,
            "Not true that Person is a Property.",
        )

    def test_GetImmediateSubtypesOk(self) -> None:
        t_article = sdotermsource.SdoTermSource.getTerm("Article")
        self.assertIn(
            "NewsArticle",
            t_article.subs.ids,
            "NewsArticle is in immediate subtypes of Article.",
        )

    def test_GetImmediateSubtypesWrong(self) -> None:
        t_creative_work = sdotermsource.SdoTermSource.getTerm("CreativeWork")
        self.assertNotIn(
            "NewsArticle",
            t_creative_work.subs.ids,
            "NewsArticle is not in immediate subtypes of CreativeWork.",
        )


class SchemaPropertyAPITestCase(unittest.TestCase):
    def test_actorSupersedesActors(self) -> None:
        p_actor = sdotermsource.SdoTermSource.getTerm("actor")
        self.assertIn("actors", p_actor.supersedes, "actor supersedes actors.")

    def test_actorsSuperseded(self) -> None:
        p_actors = sdotermsource.SdoTermSource.getTerm("actors")
        self.assertTrue(
            p_actors.superseded,
            f"actors property has been superseded. {p_actors.superseded} {p_actors.supersededBy}",
        )

    def test_actorNotSuperseded(self) -> None:
        p_actor = sdotermsource.SdoTermSource.getTerm("actor")
        self.assertFalse(p_actor.superseded, "actor property has not been superseded.")

    def test_offersNotSuperseded(self) -> None:
        p_offers = sdotermsource.SdoTermSource.getTerm("offers")
        self.assertFalse(
            p_offers.superseded, "offers property has not been superseded."
        )

    def test_actorNotSupersededByOffers(self) -> None:
        p_offers = sdotermsource.SdoTermSource.getTerm("offers")
        self.assertNotIn(
            "actor",
            p_offers.supersedes,
            msg="actor property doesn't supersede offers property.",
        )

    def test_offersNotSupersededByActor(self) -> None:
        p_actor = sdotermsource.SdoTermSource.getTerm("actor")
        self.assertNotIn(
            "offers",
            p_actor.supersedes,
            msg="offers property doesn't supersede actors property.",
        )


# acceptedAnswer subPropertyOf suggestedAnswer.
class SchemaPropertyMetadataTestCase(unittest.TestCase):
    def test_suggestedAnswerSuperproperties(self) -> None:
        p_accepted_answer = sdotermsource.SdoTermSource.getTerm("acceptedAnswer")
        self.assertIn(
            "suggestedAnswer",
            p_accepted_answer.supers.ids,
            msg="suggestedAnswer should be in acceptedAnswer superproperties.",
        )

    def test_acceptedAnswerSuperpropertiesArrayLen(self) -> None:
        p_accepted_answer = sdotermsource.SdoTermSource.getTerm("acceptedAnswer")
        aa_supers = p_accepted_answer.supers
        self.assertEqual(
            len(aa_supers),
            1,
            msg=f"acceptedAnswer superproperties should have len 1. Actual: {len(aa_supers)}.",
        )

    def test_answerSubproperty(self) -> None:
        p_suggested_answer = sdotermsource.SdoTermSource.getTerm("suggestedAnswer")
        self.assertIn(
            "acceptedAnswer",
            p_suggested_answer.subs.ids,
            msg="acceptedAnswer is a subPropertyOf suggestedAnswer.",
        )

    def test_answerSubproperties(self) -> None:
        p_suggested_answer = sdotermsource.SdoTermSource.getTerm("suggestedAnswer")
        self.assertEqual(
            tuple(p_suggested_answer.subs.ids),
            ("acceptedAnswer",),
            msg="suggestedAnswer subproperties should be ('acceptedAnswer',).",
        )

    def test_offerSubpropertiesArrayLen(self) -> None:
        p_offers = sdotermsource.SdoTermSource.getTerm("offers")
        self.assertEqual(
            len(p_offers.subs), 0, "offers subproperties() gives array of len 0."
        )

    def test_alumniSuperproperty(self) -> None:
        p_alumni = sdotermsource.SdoTermSource.getTerm("alumni")
        p_suggested_answer = sdotermsource.SdoTermSource.getTerm("suggestedAnswer")
        self.assertNotIn(
            "alumni",
            p_suggested_answer.supers.ids,
            msg="not suggestedAnswer subPropertyOf alumni.",
        )
        self.assertNotIn(
            "suggestedAnswer",
            p_alumni.supers.ids,
            msg="not alumni subPropertyOf suggestedAnswer.",
        )
        self.assertNotIn(
            "alumni", p_alumni.supers.ids, msg="not alumni subPropertyOf alumni."
        )
        self.assertNotIn(
            "alumniOf", p_alumni.supers.ids, msg="not alumni subPropertyOf alumniOf."
        )
        self.assertNotIn(
            "suggestedAnswer",
            p_suggested_answer.supers.ids,
            msg="not suggestedAnswer subPropertyOf suggestedAnswer.",
        )

    def test_alumniInverse(self) -> None:
        p_alumni = sdotermsource.SdoTermSource.getTerm("alumni")
        p_alumni_of = sdotermsource.SdoTermSource.getTerm("alumniOf")
        p_suggested_answer = sdotermsource.SdoTermSource.getTerm("suggestedAnswer")

        self.assertEqual(
            "alumni", p_alumni_of.inverse.id, msg="alumniOf inverseOf alumni."
        )
        self.assertEqual(
            "alumniOf", p_alumni.inverse.id, msg="alumni inverseOf alumniOf."
        )

        self.assertNotEqual(
            "alumni", p_alumni.inverse.id, msg="Not alumni inverseOf alumni."
        )
        self.assertNotEqual(
            "alumniOf", p_alumni_of.inverse.id, msg="Not alumniOf inverseOf alumniOf."
        )
        self.assertNotEqual(
            "alumni", p_suggested_answer.inverse.id, msg="Not answer inverseOf alumni."
        )


class EnumerationValueTests(unittest.TestCase):
    def test_EventStatusTypeIsEnumeration(self) -> None:
        e_event_status_type = sdotermsource.SdoTermSource.getTerm("EventStatusType")
        self.assertEqual(
            e_event_status_type.termType,
            sdoterm.SdoTermType.ENUMERATION,
            msg="EventStatusType is an Enumeration.",
        )

    def test_EventStatusTypeIsntEnumerationValue(self) -> None:
        e_event_status_type = sdotermsource.SdoTermSource.getTerm("EventStatusType")
        self.assertNotEqual(
            e_event_status_type.termType,
            sdoterm.SdoTermType.ENUMERATIONVALUE,
            msg="EventStatusType is not an Enumeration value.",
        )

    def test_EventCancelledIsEnumerationValue(self) -> None:
        e_event_cancelled = sdotermsource.SdoTermSource.getTerm("EventCancelled")
        self.assertEqual(
            e_event_cancelled.termType,
            sdoterm.SdoTermType.ENUMERATIONVALUE,
            msg="EventCancelled is an Enumeration value.",
        )


class DataTypeTests(unittest.TestCase):
    def test_booleanDataType(self) -> None:
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
    def test_emph(self) -> None:
        markstring = "This is _em_, __strong__, ___strong em___"
        html = localmarkdown.Markdown.parse(markstring, True)
        self.assertMultiLineEqual(
            html,
            "<p>This is <em>em</em>, <strong>strong</strong>, <em><strong>strong em</strong></em></p>\n",
            "Markdown string not formatted correctly",
        )

    def test_wikilink_wpre_override(self) -> None:
        html = localmarkdown.Markdown.parse(
            "See [[Thing]].", wpre="https://schema.org/"
        )
        self.assertEqual(
            html, 'See <a class="localLink" href="https://schema.org/Thing">Thing</a>.'
        )
        self.assertEqual(
            localmarkdown.Markdown.parse("See [[Thing]]."),
            'See <a class="localLink" href="/Thing">Thing</a>.',
        )


class HasMultipleBaseTypesTests(unittest.TestCase):
    def test_localbusiness2supertypes(self) -> None:
        term = sdotermsource.SdoTermSource.getTerm("LocalBusiness")
        self.assertGreater(
            len(term.supers), 1, msg="LocalBusiness is subClassOf Place + Organization."
        )

    def test_restaurant_non_multiple_supertypes(self) -> None:
        term = sdotermsource.SdoTermSource.getTerm("Restaurant")
        self.assertEqual(
            len(term.supers), 1, msg="Restaurant only has one *direct* supertype."
        )

    def test_article_non_multiple_supertypes(self) -> None:
        term = sdotermsource.SdoTermSource.getTerm("Article")
        self.assertEqual(
            len(term.supers), 1, msg="Article only has one direct supertype."
        )


class SimpleCommentCountTests(unittest.TestCase):
    def test_zeroCommentCount(self) -> None:
        query = f"""
            SELECT ?term ?comment WHERE {{
                ?term a ?type.
                FILTER NOT EXISTS {{ ?term rdfs:comment ?comment. }}
                FILTER (strStarts(str(?term), "{VOCABURI}"))
            }}
            ORDER BY ?term
        """
        ndi1_results = sdotermsource.SdoTermSource.query(query)
        for row in ndi1_results:
            log.warning("Term %s has no rdfs:comment value", row["term"])
        self.assertEqual(
            len(ndi1_results),
            0,
            f"Found: {len(ndi1_results)} term(s) without comment value",
        )

    def test_multiCommentCount(self) -> None:
        query = f"""
            SELECT ?term ?comment WHERE {{
                ?term a ?type;
                  rdfs:comment ?comment.
                FILTER (strStarts(str(?term), "{VOCABURI}"))
            }}
            GROUP BY ?term
            HAVING (count(DISTINCT ?comment) > 1)
            ORDER BY ?term
        """
        ndi1_results = sdotermsource.SdoTermSource.query(query)
        if ndi1_results:
            log.warning("Query was: %s", query)
            for row in ndi1_results:
                log.warning(
                    "Term %s has rdfs:comment value %s", row["term"], row["comment"]
                )
        msg = "\n\t".join(f"{row['term']}: {row['comment']}" for row in ndi1_results)
        self.assertEqual(
            len(ndi1_results),
            0,
            f"Found: {len(ndi1_results)} term(s) with multiple comment values:\n{msg}",
        )


class BasicJSONLDTests(unittest.TestCase):
    ctx: dict[str, Any]

    @classmethod
    def setUpClass(cls) -> None:
        try:
            cls.ctx = json.loads(CURRENT_CONTEXT_FILE.read_text(encoding="utf-8"))
        except OSError as exc:
            raise unittest.SkipTest(
                "jsonldcontext.jsonld file not loaded - bypassing tests"
            ) from exc

    def test_issuedBy_jsonld(self) -> None:
        self.assertIn(
            "issuedBy", self.ctx["@context"], "issuedBy should be defined."
        )

    def test_dateModified_jsonld(self) -> None:
        self.assertIn(
            "dateModified", self.ctx["@context"], "dateModified should be defined."
        )

    def test_sameas_jsonld(self) -> None:
        self.assertIn("sameAs", self.ctx["@context"], msg="sameAs should be defined.")


class JsonExampleTests(unittest.TestCase):
    def testAllExamples(self) -> None:
        assert EXAMPLES is not None
        for example in EXAMPLES.allExamples():
            source_filename = example.getMeta("file")
            with self.subTest(key=example.getKey(), file=source_filename):
                if not example.hasJsonld():
                    continue
                json_source = example.getJsonldRaw()
                try:
                    json.loads(json_source)
                except json.decoder.JSONDecodeError as json_error:
                    lines = json_error.doc.split("\n")
                    snippet = (
                        lines[json_error.lineno - 1]
                        + "\n"
                        + "^".rjust(json_error.colno)
                    )
                    # Show up to three lines above the error; often a missing comma above.
                    if json_error.lineno > 2:
                        for i in range(2, min(json_error.lineno, 5)):
                            snippet = lines[json_error.lineno - i] + "\n" + snippet
                    lineno = json_error.lineno + (example.jsonld_offset or 0)
                    self.fail(
                        f"JSON parsing error: '{json_error.msg}' in file "
                        f"{source_filename}:{lineno}:{json_error.colno} \n{snippet}"
                    )
                except Exception as exception:
                    self.fail(
                        f"Could not parse JSON '{json_source}' error: "
                        f"{exception} file: {source_filename}"
                    )


# TODO: Unwritten tests
#
# * different terms should not have identical comments
# * if x and y are inverseOf each other, the rangeIncludes types on x should be
#   domainIncludes on y, and vice-versa.
# * need a few supporting functions e.g. all terms, all types, all properties,
#   all enum values; candidates for api later but just use here first.
# * make sure terms match their labels (e.g. priceRange), with or without
#   whitespace?
# * check we don't assign more than one example to the same ID

if __name__ == "__main__":
    unittest.main()
