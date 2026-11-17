from __future__ import annotations

import json
import logging
from typing import Any
import unittest

import rdflib

from schemaorg import constants, markdown
from schemaorg.graph_loader import GraphLoader
from schemaorg.layout import InputLayout, Issues, Releases
from schemaorg.model import Vocabulary, VocabularyLoader
from schemaorg.term_view import TermKind, TermView, TermViewCatalog
import SchemaExamples.schemaexamples as schemaexamples
import util.paths as paths
import util.schema as schema

VOCABURI = constants.SCHEMA_URI

TYPECOUNT_UPPERBOUND = 1500
TYPECOUNT_LOWERBOUND = 500

log = logging.getLogger(__name__)

GRAPH: rdflib.Graph | None = None
VOCAB: Vocabulary | None = None
CATALOG: TermViewCatalog | None = None
EXAMPLES: schemaexamples.SchemaExamples | None = None


def setUpModule() -> None:
    global GRAPH, VOCAB, CATALOG, EXAMPLES
    files = Issues(InputLayout(constants.PROJECT_ROOT)).get_ttl_files()
    GRAPH = GraphLoader.load(files)
    VOCAB = VocabularyLoader(GRAPH).load()
    CATALOG = TermViewCatalog.from_graph(GRAPH, VOCAB)
    EXAMPLES = schemaexamples.SchemaExamples.from_default()


def _term(term_id: str) -> TermView:
    assert CATALOG is not None
    view = CATALOG.get(term_id)
    assert view is not None, f"Missing term {term_id}"
    return view


class BallparkCountTests(unittest.TestCase):
    def test_alltypes(self) -> None:
        assert VOCAB is not None
        type_range = range(TYPECOUNT_LOWERBOUND, TYPECOUNT_UPPERBOUND)
        self.assertIn(len(VOCAB.types), type_range)


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
        assert CATALOG is not None
        path = CATALOG.parent_paths_to("CreativeWork", "Thing")
        self.assertEqual(len(path), 1, path)

    def test_dualPath(self) -> None:
        assert CATALOG is not None
        path = CATALOG.parent_paths_to("Restaurant", "Thing")
        self.assertEqual(len(path), 2, path)

    def test_inverseDualPath(self) -> None:
        assert CATALOG is not None
        self.assertEqual(
            len(CATALOG.parent_paths_to("Thing", "Restaurant")),
            0,
            "0 supertype paths from Thing to Restaurant.",
        )


class SchemaBasicAPITestCase(unittest.TestCase):
    def test_gotThing(self) -> None:
        assert CATALOG is not None
        self.assertIsNotNone(
            CATALOG.get("Thing"),
            msg="Thing node should be accessible.",
        )

    def test_gotFooBarThing(self) -> None:
        assert CATALOG is not None
        self.assertIsNone(
            CATALOG.get("FooBar"),
            msg="FooBar node should NOT be accessible.",
        )

    def test_NewsArticleIsType(self) -> None:
        self.assertEqual(
            _term("NewsArticle").termType, TermKind.TYPE, "NewsArticle is a class."
        )

    def test_QuantityisDataType(self) -> None:
        self.assertEqual(
            _term("Quantity").termType,
            TermKind.DATATYPE,
            "Quantity is a DataType.",
        )

    def test_ItemAvailabilityIsEnumeration(self) -> None:
        self.assertEqual(
            _term("ItemAvailability").termType,
            TermKind.ENUMERATION,
            "ItemAvailability is an Enumeration.",
        )

    def test_EnumerationIsEnumeration(self) -> None:
        self.assertEqual(
            _term("Enumeration").termType,
            TermKind.ENUMERATION,
            "Enumeration is an Enumeration type.",
        )

    def test_ArticleSupertypeNewsArticle(self) -> None:
        self.assertIn(
            "NewsArticle",
            _term("Article").subs.ids,
            "NewsArticle is a sub-type of Article",
        )

    def test_NewsArticleSupertypeArticle(self) -> None:
        self.assertNotIn(
            "Article",
            _term("NewsArticle").subs.ids,
            "Article is not a sub-type of NewsArticle",
        )

    def test_ThingSupertypeThing(self) -> None:
        self.assertNotIn("Thing", _term("Thing").subs.ids, "Thing subClassOf Thing.")

    def test_DataTypeSupertypeDataType(self) -> None:
        self.assertNotIn(
            "DataType", _term("DataType").subs.ids, "DataType subClassOf DataType."
        )

    def test_PersonSupertypeThing(self) -> None:
        self.assertIn("Person", _term("Thing").subs.ids, "Person subClassOf Thing.")

    def test_ThingNotSupertypePerson(self) -> None:
        self.assertNotIn(
            "Thing", _term("Person").subs.ids, "Thing not subClassOf Person."
        )

    def test_StoreSupertypeLocalBusiness(self) -> None:
        assert CATALOG is not None
        self.assertTrue(
            CATALOG.is_subclass_of("Store", "LocalBusiness"),
            "Store subClassOf LocalBusiness.",
        )

    def test_StoresArePlaces(self) -> None:
        assert CATALOG is not None
        self.assertTrue(
            CATALOG.is_subclass_of("Store", "Place"),
            "Store subClassOf Place.",
        )

    def test_StoresAreOrganizations(self) -> None:
        assert CATALOG is not None
        self.assertTrue(
            CATALOG.is_subclass_of("Store", "Organization"),
            "Store subClassOf Organization.",
        )

    def test_PersonNotAttribute(self) -> None:
        self.assertNotEqual(
            _term("Person").termType,
            TermKind.PROPERTY,
            "Not true that Person is a Property.",
        )

    def test_GetImmediateSubtypesOk(self) -> None:
        self.assertIn(
            "NewsArticle",
            _term("Article").subs.ids,
            "NewsArticle is in immediate subtypes of Article.",
        )

    def test_GetImmediateSubtypesWrong(self) -> None:
        self.assertNotIn(
            "NewsArticle",
            _term("CreativeWork").subs.ids,
            "NewsArticle is not in immediate subtypes of CreativeWork.",
        )


class SchemaPropertyAPITestCase(unittest.TestCase):
    def test_actorSupersedesActors(self) -> None:
        self.assertIn("actors", _term("actor").supersedes, "actor supersedes actors.")

    def test_actorsSuperseded(self) -> None:
        p_actors = _term("actors")
        self.assertTrue(
            p_actors.superseded,
            f"actors property has been superseded. {p_actors.superseded} {p_actors.supersededBy}",
        )

    def test_actorNotSuperseded(self) -> None:
        self.assertFalse(
            _term("actor").superseded, "actor property has not been superseded."
        )

    def test_offersNotSuperseded(self) -> None:
        self.assertFalse(
            _term("offers").superseded, "offers property has not been superseded."
        )

    def test_actorNotSupersededByOffers(self) -> None:
        self.assertNotIn(
            "actor",
            _term("offers").supersedes,
            msg="actor property doesn't supersede offers property.",
        )

    def test_offersNotSupersededByActor(self) -> None:
        self.assertNotIn(
            "offers",
            _term("actor").supersedes,
            msg="offers property doesn't supersede actors property.",
        )


class SchemaPropertyMetadataTestCase(unittest.TestCase):
    def test_suggestedAnswerSuperproperties(self) -> None:
        self.assertIn(
            "suggestedAnswer",
            _term("acceptedAnswer").supers.ids,
            msg="suggestedAnswer should be in acceptedAnswer superproperties.",
        )

    def test_acceptedAnswerSuperpropertiesArrayLen(self) -> None:
        aa_supers = _term("acceptedAnswer").supers
        self.assertEqual(
            len(aa_supers),
            1,
            msg=f"acceptedAnswer superproperties should have len 1. Actual: {len(aa_supers)}.",
        )

    def test_answerSubproperty(self) -> None:
        self.assertIn(
            "acceptedAnswer",
            _term("suggestedAnswer").subs.ids,
            msg="acceptedAnswer is a subPropertyOf suggestedAnswer.",
        )

    def test_answerSubproperties(self) -> None:
        self.assertEqual(
            tuple(_term("suggestedAnswer").subs.ids),
            ("acceptedAnswer",),
            msg="suggestedAnswer subproperties should be ('acceptedAnswer',).",
        )

    def test_offerSubpropertiesArrayLen(self) -> None:
        self.assertEqual(
            len(_term("offers").subs), 0, "offers subproperties() gives array of len 0."
        )

    def test_alumniSuperproperty(self) -> None:
        p_alumni = _term("alumni")
        p_suggested_answer = _term("suggestedAnswer")
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
        p_alumni = _term("alumni")
        p_alumni_of = _term("alumniOf")
        p_suggested_answer = _term("suggestedAnswer")

        assert p_alumni_of.inverse is not None
        assert p_alumni.inverse is not None
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
        self.assertIsNone(
            p_suggested_answer.inverse, msg="suggestedAnswer has no inverseOf."
        )


class EnumerationValueTests(unittest.TestCase):
    def test_EventStatusTypeIsEnumeration(self) -> None:
        self.assertEqual(
            _term("EventStatusType").termType,
            TermKind.ENUMERATION,
            msg="EventStatusType is an Enumeration.",
        )

    def test_EventStatusTypeIsntEnumerationValue(self) -> None:
        self.assertNotEqual(
            _term("EventStatusType").termType,
            TermKind.ENUMERATIONVALUE,
            msg="EventStatusType is not an Enumeration value.",
        )

    def test_EventCancelledIsEnumerationValue(self) -> None:
        self.assertEqual(
            _term("EventCancelled").termType,
            TermKind.ENUMERATIONVALUE,
            msg="EventCancelled is an Enumeration value.",
        )


class DataTypeTests(unittest.TestCase):
    def test_booleanDataType(self) -> None:
        self.assertEqual(_term("Boolean").termType, TermKind.DATATYPE)
        self.assertEqual(_term("DataType").termType, TermKind.DATATYPE)
        self.assertNotEqual(_term("Thing").termType, TermKind.DATATYPE)
        self.assertNotEqual(_term("Duration").termType, TermKind.DATATYPE)


class MarkDownTest(unittest.TestCase):
    def test_emph(self) -> None:
        markstring = "This is _em_, __strong__, ___strong em___"
        html = markdown.Markdown.parse(markstring, True)
        self.assertMultiLineEqual(
            html,
            "<p>This is <em>em</em>, <strong>strong</strong>, <em><strong>strong em</strong></em></p>\n",
            "Markdown string not formatted correctly",
        )

    def test_wikilink_wpre_override(self) -> None:
        html = markdown.Markdown.parse(
            "See [[Thing]].", wpre="https://schema.org/"
        )
        self.assertEqual(
            html, 'See <a class="localLink" href="https://schema.org/Thing">Thing</a>.'
        )
        self.assertEqual(
            markdown.Markdown.parse("See [[Thing]]."),
            'See <a class="localLink" href="/Thing">Thing</a>.',
        )


class HasMultipleBaseTypesTests(unittest.TestCase):
    def test_localbusiness2supertypes(self) -> None:
        self.assertGreater(
            len(_term("LocalBusiness").supers),
            1,
            msg="LocalBusiness is subClassOf Place + Organization.",
        )

    def test_restaurant_non_multiple_supertypes(self) -> None:
        self.assertEqual(
            len(_term("Restaurant").supers),
            1,
            msg="Restaurant only has one *direct* supertype.",
        )

    def test_article_non_multiple_supertypes(self) -> None:
        self.assertEqual(
            len(_term("Article").supers),
            1,
            msg="Article only has one direct supertype.",
        )


class SimpleCommentCountTests(unittest.TestCase):
    def test_zeroCommentCount(self) -> None:
        assert GRAPH is not None
        query = f"""
            SELECT ?term ?comment WHERE {{
                ?term a ?type.
                FILTER NOT EXISTS {{ ?term rdfs:comment ?comment. }}
                FILTER (strStarts(str(?term), "{VOCABURI}"))
            }}
            ORDER BY ?term
        """
        ndi1_results = list(GRAPH.query(query))
        for row in ndi1_results:
            assert isinstance(row, rdflib.query.ResultRow)
            log.warning("Term %s has no rdfs:comment value", row["term"])
        self.assertEqual(
            len(ndi1_results),
            0,
            f"Found: {len(ndi1_results)} term(s) without comment value",
        )

    def test_multiCommentCount(self) -> None:
        assert GRAPH is not None
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
        ndi1_results = list(GRAPH.query(query))
        msg_lines: list[str] = []
        if ndi1_results:
            log.warning("Query was: %s", query)
            for row in ndi1_results:
                assert isinstance(row, rdflib.query.ResultRow)
                log.warning(
                    "Term %s has rdfs:comment value %s", row["term"], row["comment"]
                )
                msg_lines.append(f"{row['term']}: {row['comment']}")
        self.assertEqual(
            len(ndi1_results),
            0,
            f"Found: {len(ndi1_results)} term(s) with multiple comment values:\n"
            + "\n\t".join(msg_lines),
        )


class BasicJSONLDTests(unittest.TestCase):
    ctx: dict[str, Any]

    @classmethod
    def setUpClass(cls) -> None:
        context_file = Releases(
            paths.DefaultInputLayout(), schema.VERSION
        ).file(filename="schemaorgcontext.jsonld")
        try:
            cls.ctx = json.loads(context_file.read_text(encoding="utf-8"))
        except OSError as exc:
            raise unittest.SkipTest(
                f"{context_file} not built - bypassing tests"
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


if __name__ == "__main__":
    unittest.main()
