from __future__ import annotations

import json
import logging
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import rdflib
from schemaorg.graph_loader import split_release_graphs
from schemaorg.layout import Domain, InputLayout, OutputLayout, Releases, Scope
from schemaorg.model import SDO, VocabularyLoader
from schemaorg.renderers import (
    CountsRenderer,
    CsvRenderer,
    OwlRenderer,
    RdfRenderer,
    ShapesRenderer,
    protocol_swap,
    render_examples,
    render_http_equivs,
    render_jsonld_context,
    render_jsonld_tree,
    render_sitemap,
    uriwrap,
)
from schemaorg import markdown
from schemaorg.progress import LogProgressReporter, NullProgressReporter
from schemaorg.site_bundle import SiteBundle
from schemaorg.tasks.export_release_files import (
    Artifact,
    ExportReleaseFilesTask,
    plan_release_unscoped,
    plan_scoped,
    write_artifacts,
)
from schemaorg.tasks.export_site_metadata import (
    ExportSiteMetadataTask,
    plan_site_docs,
)
from schemaorg.version import Version, VersionItem
import scripts.buildfiles as buildfiles
import scripts.buildsite as buildsite
import util.schema as schema

FIXTURE_TTL = """
@prefix : <https://schema.org/> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix foaf: <http://xmlns.com/foaf/0.1/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
:Thing a rdfs:Class ; rdfs:label "Thing" ; rdfs:comment "Generic item." .
:Place a rdfs:Class ; rdfs:label "Place" ; rdfs:subClassOf :Thing ;
    :isPartOf <https://pending.schema.org> .
:Person a rdfs:Class ; rdfs:label "Person" ; rdfs:subClassOf :Thing ;
    rdfs:comment "A person, a kind of [[Thing]]." ;
    owl:equivalentClass foaf:Person .
:Hybrid a rdfs:Class ; rdfs:label "Hybrid" ; rdfs:subClassOf :Person, :Place .
:OldThing a rdfs:Class ; rdfs:label "OldThing" ; rdfs:subClassOf :Thing ;
    :isPartOf <https://attic.schema.org> .
:DataType a rdfs:Class ; rdfs:label "DataType" ; rdfs:subClassOf rdfs:Class .
:Text a :DataType, rdfs:Class ; rdfs:label "Text" .
:name a rdf:Property ; rdfs:label "name" ; :domainIncludes :Thing ; :rangeIncludes :Text .
"""


def _fixture_graph() -> rdflib.Graph:
    g = rdflib.Graph(bind_namespaces="none")
    g.parse(data=FIXTURE_TTL, format="turtle")
    return g


class TestPostProcess(unittest.TestCase):
    def testProtocolSwap(self) -> None:
        swap = protocol_swap()
        self.assertEqual(swap(""), "")
        self.assertEqual(
            swap("Defined in https://schema.org and https://bib.schema.org."),
            "Defined in http://schema.org and http://bib.schema.org.",
        )
        self.assertEqual(
            swap(
                "https://health-lifesci.schema.org https://schema.org/Thing "
                "https://devices.schema.org/x https://schema.organic.example/x"
            ),
            "http://health-lifesci.schema.org http://schema.org/Thing "
            "http://devices.schema.org/x https://schema.organic.example/x",
        )

    def testProtocolSwapPreservesWebsites(self) -> None:
        text = (
            "https://blog.schema.org/post https://dev.schema.org/ "
            "https://myblog.schema.org/y"
        )
        self.assertEqual(
            protocol_swap()(text),
            "https://blog.schema.org/post https://dev.schema.org/ "
            "http://myblog.schema.org/y",
        )

    def testArtifactWriteAndSharedRenderDeduplication(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            https_path = Path(tmp) / "https.txt"
            http_path = Path(tmp) / "http.txt"
            calls = 0

            def render() -> str:
                nonlocal calls
                calls += 1
                return "https://schema.org/Thing"

            written = write_artifacts(
                [
                    Artifact("https", https_path, render),
                    Artifact("http", http_path, render, protocol_swap()),
                ],
                NullProgressReporter(),
                "test",
            )
            self.assertEqual(written, [https_path, http_path])
            self.assertEqual(calls, 1)
            self.assertEqual(
                https_path.read_text(encoding="utf-8"),
                "https://schema.org/Thing",
            )
            self.assertEqual(
                http_path.read_text(encoding="utf-8"),
                "http://schema.org/Thing",
            )
            Artifact("plain", https_path, lambda: "raw").write()
            self.assertEqual(https_path.read_text(encoding="utf-8"), "raw")


class TestRenderers(unittest.TestCase):
    def setUp(self) -> None:
        self.graph = _fixture_graph()
        self.all_graph, self.current_graph = split_release_graphs(self.graph)
        self.vocab = VocabularyLoader(
            self.all_graph, version=VersionItem("30.1", "2026-09-16")
        ).load()

    def testUriWrap(self) -> None:
        self.assertEqual(uriwrap("Credential"), "https://schema.org/Credential")
        self.assertEqual(
            uriwrap("https://example.com/Bogus"), "https://example.com/Bogus"
        )
        self.assertEqual(
            uriwrap(["Person", "Thing"]),
            "https://schema.org/Person, https://schema.org/Thing",
        )
        with self.assertRaises(TypeError):
            uriwrap(42)

    def testSplitReleaseGraphs(self) -> None:
        foaf_person = rdflib.URIRef("http://xmlns.com/foaf/0.1/Person")
        self.assertIn(
            (foaf_person, rdflib.RDF.type, rdflib.RDFS.Class), self.all_graph
        )
        self.assertNotIn(
            (rdflib.RDFS.Class, rdflib.RDF.type, rdflib.RDFS.Class),
            self.all_graph,
        )
        self.assertIn(
            (SDO.OldThing, rdflib.RDFS.label, rdflib.Literal("OldThing")),
            self.all_graph,
        )
        self.assertNotIn((SDO.OldThing, None, None), self.current_graph)

        bound = {str(k) for k, _ in self.all_graph.namespaces() if str(k)}
        self.assertEqual(bound, {"foaf", "owl", "rdf", "rdfs", "schema", "xsd"})

    def testShapesRendererUsesHttpGraph(self) -> None:
        renderer = ShapesRenderer(self.all_graph)
        http = renderer.http_graph
        self.assertIn(
            (
                rdflib.URIRef("http://schema.org/Person"),
                rdflib.RDFS.subClassOf,
                rdflib.URIRef("http://schema.org/Thing"),
            ),
            http,
        )
        self.assertNotIn((SDO.Person, None, None), http)
        self.assertIn("ValidSchemaPerson", renderer.shex())
        self.assertIn("ValidSchemaPerson", renderer.shacl())
        self.assertIn("subClassOf", renderer.subclasses())

    def testRdfRendererRequiresDatasetUriForNquads(self) -> None:
        renderer = RdfRenderer(self.all_graph)
        with self.assertRaises(ValueError):
            renderer.render("nquads")
        nq = renderer.render("nquads", dataset_uri=SDO["30.1"])
        self.assertIn("<https://schema.org/30.1> .", nq)
        self.assertEqual(nq, "".join(sorted(nq.splitlines(keepends=True))))
        self.assertIs(renderer.canonical, renderer.canonical)

    def testRdfRendererHandlesLangLiteralsWithoutXmlPrefix(self) -> None:
        g = rdflib.Graph(bind_namespaces="none")
        g.parse(
            data=(
                "@prefix schema: <https://schema.org/> .\n"
                "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n"
                'schema:Thing a rdfs:Class ; rdfs:label "Thing"@en .\n'
            ),
            format="turtle",
        )
        rdf_xml = RdfRenderer(g).render("rdf")
        self.assertIn('xml:lang="en"', rdf_xml)
        self.assertNotIn("xml", {str(k) for k, _ in g.namespaces()})

    def testRdfRendererPropagatesSortFailures(self) -> None:
        renderer = RdfRenderer(self.all_graph)
        with patch(
            "schemaorg.renderers.rdf_renderer.sort_xml",
            side_effect=ValueError("bad xml"),
        ):
            with self.assertRaises(ValueError):
                renderer.render("rdf")

    def testRemovingPrefixStatementOnlyRemovesNamespaceEntry(self) -> None:
        ttl_without_foaf_prefix = FIXTURE_TTL.replace(
            "@prefix foaf: <http://xmlns.com/foaf/0.1/> .\n", ""
        ).replace("foaf:Person", "<http://xmlns.com/foaf/0.1/Person>")

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            outputs: dict[str, dict[str, str]] = {}
            for label, ttl_text in (
                ("with_prefix", FIXTURE_TTL),
                ("without_prefix", ttl_without_foaf_prefix),
            ):
                in_dir = root / label
                (in_dir / "data").mkdir(parents=True)
                (in_dir / "versions.json").write_text(
                    json.dumps({
                        "schemaversion": "30.1",
                        "releaseLog": {"30.1": "2026-09-16"},
                    }),
                    encoding="utf-8",
                )
                (in_dir / "data" / "schema.ttl").write_text(
                    ttl_text, encoding="utf-8"
                )
                out_layout = OutputLayout(in_dir / "data")
                buildfiles.export_release_files(
                    InputLayout(in_dir), out_layout, version="30.1"
                )
                rel_dir = Releases(
                    out_layout, Version(in_dir / "versions.json")
                ).dir("30.1")
                outputs[label] = {
                    p.name: p.read_text(encoding="utf-8")
                    for p in rel_dir.iterdir()
                }

        ctx_with = json.loads(
            outputs["with_prefix"]["schemaorgcontext.jsonld"]
        )["@context"]
        ctx_without = json.loads(
            outputs["without_prefix"]["schemaorgcontext.jsonld"]
        )["@context"]
        self.assertEqual(ctx_with.pop("foaf"), "http://xmlns.com/foaf/0.1/")
        self.assertEqual(ctx_with, ctx_without)
        self.assertNotIn("brick", ctx_without)

        # Prefix-independent exports must not change at all.
        for name in (
            "schemaorg-all-https.nt",
            "schemaorg-all-http.nt",
            "schemaorg-all-https.nq",
            "schemaorg-all-http.nq",
            "schemaorg-all-https-types.csv",
            "schemaorg-all-https-properties.csv",
            "schemaorg.owl",
            "httpequivs.ttl",
            "schemaorg-shapes.shexj",
            "schemaorg-subclasses.shacl",
        ):
            self.assertEqual(
                outputs["with_prefix"][name],
                outputs["without_prefix"][name],
                name,
            )

        # Prefix-compacted RDF exports must represent the exact same triples.
        g_with = rdflib.Graph(bind_namespaces="none").parse(
            data=outputs["with_prefix"]["schemaorg-all-https.ttl"],
            format="turtle",
        )
        g_without = rdflib.Graph(bind_namespaces="none").parse(
            data=outputs["without_prefix"]["schemaorg-all-https.ttl"],
            format="turtle",
        )
        self.assertEqual(set(g_with), set(g_without))

    def testJsonLdContextAndTreeRenderers(self) -> None:
        ctx = json.loads(render_jsonld_context(self.all_graph, self.vocab))[
            "@context"
        ]
        self.assertEqual(ctx["@vocab"], "http://schema.org/")
        self.assertEqual(ctx["xsd"], "http://www.w3.org/2001/XMLSchema#")

        tree = json.loads(render_jsonld_tree(self.vocab))
        self.assertEqual(tree["@id"], "schema:Thing")
        by_id = {c["@id"]: c for c in tree["children"]}
        self.assertEqual(
            by_id["schema:Person"]["description"], "A person, a kind of Thing."
        )
        self.assertTrue(by_id["schema:OldThing"]["attic"])
        self.assertTrue(by_id["schema:Place"]["pending"])
        hybrid = by_id["schema:Person"]["children"][0]
        self.assertEqual(hybrid["@id"], "schema:Hybrid")
        self.assertEqual(
            hybrid["rdfs:subClassOf"], ["schema:Person", "schema:Place"]
        )

    def testHttpEquivsExcludesRetiredAndSplitsClassVsProperty(self) -> None:
        ttl = render_http_equivs(self.vocab)
        self.assertIn("schema_p:Person owl:equivalentClass schema_s:Person", ttl)
        self.assertIn("schema_p:name owl:equivalentProperty schema_s:name", ttl)
        self.assertNotIn("OldThing", ttl)

    def testCsvRendererFiltersRetired(self) -> None:
        renderer = CsvRenderer(self.vocab)
        all_rows = renderer.types(include_retired=True)
        current_rows = renderer.types(include_retired=False)
        retired_row = '"https://schema.org/OldThing","OldThing"'
        self.assertIn(retired_row, all_rows)
        self.assertNotIn(retired_row, current_rows)
        self.assertIn("https://attic.schema.org", all_rows)

        props = renderer.properties(include_retired=True)
        self.assertEqual(props.count("\n"), 2)
        self.assertIn('"https://schema.org/name","name"', props)

    def testCsvRendererWikilinksDefaultToAbsoluteSchemaUrls(self) -> None:
        rows = CsvRenderer(self.vocab).types(include_retired=True)
        self.assertIn(
            '<a class=""localLink"" href=""https://schema.org/Thing"">Thing</a>',
            rows,
        )
        relative = CsvRenderer(self.vocab, wikilink_prefix="/")
        self.assertIn(
            'href=""/Thing""',
            relative.types(include_retired=True),
        )

    def testCountsRenderer(self) -> None:
        renderer = CountsRenderer(self.vocab, VersionItem("30.1", "2026-09-16"))
        self.assertEqual(renderer.counts["Property"], 1)
        self.assertEqual(renderer.counts["schemaorgversion"], "30.1")
        self.assertIn(renderer.json(), renderer.jsonp())

    def testOwlRendererHandlesNextWithoutDate(self) -> None:
        prev_wpre = markdown.MarkdownTool.WPRE
        self.addCleanup(markdown.MarkdownTool.setWikilinkPrePath, prev_wpre)
        markdown.MarkdownTool.setWikilinkPrePath("https://schema.org/")

        dated = OwlRenderer(
            self.all_graph, VersionItem("30.1", "2026-09-16")
        ).render()
        self.assertEqual(markdown.MarkdownTool.WPRE, "https://schema.org/")
        self.assertIn("released: 2026-09-16", dated)
        self.assertIn("dcterms:modified", dated)
        self.assertIn('href="/Thing"', dated)

        unreleased = OwlRenderer(self.all_graph, VersionItem("next")).render()
        self.assertIn("Generated from Schema.org version: next", unreleased)
        self.assertNotIn("released:", unreleased)
        self.assertNotIn("None", unreleased)
        self.assertNotIn("dcterms:modified", unreleased)
        self.assertIn("<owl:versionInfo", unreleased)

    def testSitemapRendererOmitsLastmodWithoutDate(self) -> None:
        dated = render_sitemap(self.vocab, VersionItem("30.1", "2026-09-16"))
        self.assertIn("<lastmod>2026-09-16</lastmod>", dated)

        unreleased = render_sitemap(self.vocab, VersionItem("next"))
        self.assertNotIn("<lastmod>", unreleased)
        self.assertIn("<loc>https://schema.org/Person</loc>", unreleased)

    def testExamplesRenderer(self) -> None:
        self.assertEqual(render_examples(()), "")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ex_file = root / "data" / "examples.txt"
            ex_file.parent.mkdir(parents=True)
            ex_file.write_text(
                'TYPES: #eg-1 Person\nPRE-MARKUP:\nAda\nJSON:\n{"@type": "Person"}\n',
                encoding="utf-8",
            )
            rendered = render_examples((ex_file,))
            self.assertIn("#eg-0001", rendered)
            self.assertIn("Person", rendered)


class TestPlan(unittest.TestCase):
    def testReleaseAndSiteDocsPlansAreDisjointAndComplete(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            versions_path = Path(tmp) / "versions.json"
            versions_path.write_text(
                json.dumps({
                    "schemaversion": "30.1",
                    "releaseLog": {"30.1": "2026-09-16"},
                }),
                encoding="utf-8",
            )
            version = Version(versions_path)
            next_version = version.next()
            numbered_version = version.current()
            release_layout = OutputLayout(Path(tmp) / "data")
            site_layout = OutputLayout(Path(tmp) / "site")
            releases = Releases(release_layout, version)
            all_graph, current_graph = split_release_graphs(_fixture_graph())
            vocab = VocabularyLoader(all_graph, version=next_version).load()
            csv = CsvRenderer(vocab)

            next_all_scoped = plan_scoped(
                Scope.ALL, all_graph, csv, next_version, releases
            )
            next_current_scoped = plan_scoped(
                Scope.CURRENT, current_graph, csv, next_version, releases
            )
            next_unscoped = plan_release_unscoped(
                all_graph, vocab, next_version, releases, ()
            )
            site_docs = plan_site_docs(
                vocab, next_version, releases.dir(next_version), site_layout
            )
            self.assertEqual(
                [a.path.name for a in next_all_scoped],
                ["schemaorg-all-https.ttl"],
            )
            self.assertEqual(
                [a.path.name for a in next_current_scoped],
                ["schemaorg-current-https.ttl"],
            )
            self.assertEqual(len(next_unscoped), 7)
            self.assertEqual(len(site_docs), 8)

            next_artifacts = [
                *next_all_scoped,
                *next_current_scoped,
                *next_unscoped,
            ]
            next_paths = [a.path for a in next_artifacts]
            self.assertEqual(len(next_paths), len(set(next_paths)))
            self.assertEqual(len(next_artifacts), 9)
            self.assertTrue(
                all(p.parent == releases.dir("next") for p in next_paths)
            )
            self.assertTrue(
                all(
                    a.path.parent == site_layout.dir(Domain.DOCS)
                    for a in site_docs
                )
            )

            all_scoped = plan_scoped(
                Scope.ALL, all_graph, csv, numbered_version, releases
            )
            current_scoped = plan_scoped(
                Scope.CURRENT, current_graph, csv, numbered_version, releases
            )
            release_unscoped = plan_release_unscoped(
                all_graph, vocab, numbered_version, releases, ()
            )
            self.assertEqual(len(all_scoped), 14)
            self.assertEqual(len(current_scoped), 14)
            self.assertEqual(len(release_unscoped), 7)

            release_artifacts = [
                *all_scoped,
                *current_scoped,
                *release_unscoped,
            ]
            release_paths = [a.path for a in release_artifacts]
            self.assertEqual(
                len(release_paths),
                len(set(release_paths)),
                "duplicate artifact paths",
            )
            self.assertEqual(len(release_artifacts), 35)
            self.assertTrue(
                all(p.parent == releases.dir("30.1") for p in release_paths)
            )
            http = [
                a
                for a in release_artifacts
                if a.path.name.endswith(("-http.nt", "-http-types.csv"))
            ]
            self.assertEqual(len(http), 4)
            self.assertTrue(all(a.post for a in http))

    def testExportReleaseFilesAndSiteDocsWithLayouts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            in_dir = root / "in"
            site_dir = root / "site"
            (in_dir / "data").mkdir(parents=True)
            (in_dir / "versions.json").write_text(
                json.dumps({
                    "schemaversion": "30.1",
                    "releaseLog": {"30.1": "2026-09-16"},
                }),
                encoding="utf-8",
            )
            (in_dir / "data" / "schema.ttl").write_text(
                FIXTURE_TTL, encoding="utf-8"
            )
            input_layout = InputLayout(in_dir)
            release_out_layout = OutputLayout(in_dir / "data")
            site_out_layout = OutputLayout(site_dir)

            stale = release_out_layout.file(Domain.RELEASE, "next/stale.txt")
            stale.write_text("obsolete", encoding="utf-8")
            stale_http = release_out_layout.file(
                Domain.RELEASE, "next/schemaorg-all-http.ttl"
            )
            stale_http.write_text("obsolete", encoding="utf-8")

            buildfiles.export_release_files(
                input_layout=input_layout, output_layout=release_out_layout
            )

            self.assertFalse((in_dir / "data" / "docs").exists())
            self.assertFalse(stale.exists())
            self.assertFalse(stale_http.exists())

            releases = Releases(
                release_out_layout, Version(in_dir / "versions.json")
            )
            self.assertEqual(
                sorted(p.name for p in releases.dir("next").iterdir()),
                [
                    "httpequivs.ttl",
                    "schemaorg-all-examples.txt",
                    "schemaorg-all-https.ttl",
                    "schemaorg-current-https.ttl",
                    "schemaorg-shapes.shacl",
                    "schemaorg-shapes.shexj",
                    "schemaorg-subclasses.shacl",
                    "schemaorg.owl",
                    "schemaorgcontext.jsonld",
                ],
            )

            buildfiles.export_site_docs(
                input_layout=input_layout, output_layout=site_out_layout
            )
            for name in (
                "jsoncounts.json",
                "jsonpcounts.js",
                "sitemap.xml",
                "tree.jsonld",
                "schemaorg.owl",
                "jsonldcontext.jsonld",
                "jsonldcontext.json",
                "jsonldcontext.json.txt",
            ):
                self.assertTrue(
                    site_out_layout.file(Domain.DOCS, name).is_file(), name
                )
            self.assertFalse((site_dir / "releases").exists())
            self.assertEqual(
                releases.file(filename="schemaorgcontext.jsonld").read_text(
                    encoding="utf-8"
                ),
                site_out_layout.file(
                    Domain.DOCS, "jsonldcontext.jsonld"
                ).read_text(encoding="utf-8"),
            )

            buildfiles.export_release_files(
                input_layout=input_layout,
                output_layout=release_out_layout,
                version="30.1",
            )
            self.assertEqual(len(list(releases.dir("30.1").iterdir())), 35)
            for name in (
                "httpequivs.ttl",
                "schemaorg-all-https-types.csv",
                "schemaorg-all-http-types.csv",
                "schemaorg-current-https-properties.csv",
                "schemaorg-current-http-properties.csv",
                "schemaorg-shapes.shexj",
                "schemaorg-shapes.shacl",
                "schemaorg-subclasses.shacl",
                "schemaorgcontext.jsonld",
                "schemaorg.owl",
            ):
                self.assertTrue(
                    releases.file("30.1", filename=name).is_file(), name
                )

            https_nq = releases.file(
                "30.1", filename="schemaorg-all-https.nq"
            ).read_text(encoding="utf-8")
            self.assertIn("<https://schema.org/30.1> .", https_nq)

            https_nt = releases.file(
                "30.1", filename="schemaorg-all-https.nt"
            ).read_text(encoding="utf-8")
            http_nt = releases.file(
                "30.1", filename="schemaorg-all-http.nt"
            ).read_text(encoding="utf-8")
            self.assertIn("<https://schema.org/Person>", https_nt)
            self.assertNotIn("https://schema.org", http_nt)
            self.assertEqual(protocol_swap()(https_nt), http_nt)

    def testStage1ReleaseExportDoesNotLeakStateIntoStage2SiteBuild(
        self,
    ) -> None:
        orig_target = schema.config.TARGET_VERSION
        self.addCleanup(setattr, schema.config, "TARGET_VERSION", orig_target)
        prev_wpre = markdown.MarkdownTool.WPRE
        self.addCleanup(markdown.MarkdownTool.setWikilinkPrePath, prev_wpre)

        with tempfile.TemporaryDirectory() as tmp:
            in_dir = Path(tmp) / "in"
            (in_dir / "data").mkdir(parents=True)
            (in_dir / "versions.json").write_text(
                json.dumps({
                    "schemaversion": "30.1",
                    "releaseLog": {"30.1": "2026-09-16"},
                }),
                encoding="utf-8",
            )
            ttl_with_foreign = (
                FIXTURE_TTL
                + '\n<https://example.org/foreign-dataset> a :Thing ; rdfs:label "Foreign" .\n'
            )
            raw_ttl = in_dir / "data" / "schema.ttl"
            raw_ttl.write_text(ttl_with_foreign, encoding="utf-8")
            input_layout = InputLayout(in_dir)
            release_out_layout = OutputLayout(in_dir / "data")
            version_obj = Version(in_dir / "versions.json")

            markdown.MarkdownTool.setWikilinkPrePath("/")
            schema.config.TARGET_VERSION = "next"

            buildfiles.export_release_files(
                input_layout=input_layout, output_layout=release_out_layout
            )

            self.assertEqual(markdown.MarkdownTool.WPRE, "/")

            with patch.object(buildsite.schema, "VERSION", version_obj):
                catalog, _, _ = buildsite.load_site_bundle(
                    input_layout=input_layout, target=version_obj.next()
                )

            self.assertNotIn(
                rdflib.URIRef("https://example.org/foreign-dataset"),
                catalog.vocab.all_terms(),
            )
            person = catalog.get("Person")
            self.assertIsNotNone(person)
            assert person is not None
            self.assertIn('href="/Thing"', person.comment)

    def testExportTasksProgressOutputLayoutAndErrorGuards(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            in_dir = root / "in"
            rel_dir = root / "external_releases"
            site_dir = root / "site"
            (in_dir / "data").mkdir(parents=True)
            versions_path = in_dir / "versions.json"
            versions_path.write_text(
                json.dumps({
                    "schemaversion": "30.1",
                    "releaseLog": {"30.1": "2026-09-16"},
                }),
                encoding="utf-8",
            )
            (in_dir / "data" / "schema.ttl").write_text(
                FIXTURE_TTL, encoding="utf-8"
            )
            version_obj = Version(versions_path)
            input_layout = InputLayout(in_dir)
            release_out = OutputLayout(rel_dir)

            # Undeclared version fails fast without creating target release dir.
            with self.assertRaises(ValueError):
                ExportReleaseFilesTask(
                    input_layout=input_layout,
                    output_layout=release_out,
                    version=VersionItem("99.0", "2026-01-01"),
                    progress=NullProgressReporter(),
                ).run()
            self.assertFalse((rel_dir / "releases" / "99.0").exists())

            rel_logger = logging.getLogger("test.export_release")
            with self.assertLogs(rel_logger, level=logging.INFO) as captured:
                written = ExportReleaseFilesTask(
                    input_layout=input_layout,
                    output_layout=release_out,
                    version=version_obj.next(),
                    progress=LogProgressReporter(logger=rel_logger),
                ).run()
            self.assertEqual(len(written), 9)
            self.assertIn("(9/9 files)", "\n".join(captured.output))

            with self.assertLogs(rel_logger, level=logging.INFO) as captured:
                written_num = ExportReleaseFilesTask(
                    input_layout=input_layout,
                    output_layout=release_out,
                    version=version_obj.resolve("30.1"),
                    progress=LogProgressReporter(logger=rel_logger),
                ).run()
            self.assertEqual(len(written_num), 35)
            self.assertIn("(35/35 files)", "\n".join(captured.output))

            # ExportSiteMetadataTask reads from SiteBundle backed by OutputLayout.
            bundle = SiteBundle.from_release(
                input_layout=input_layout,
                releases_layout=release_out,
                target_version=version_obj.next(),
                progress=NullProgressReporter(),
            )
            meta_logger = logging.getLogger("test.export_site_metadata")
            site_out = OutputLayout(site_dir)
            with self.assertLogs(meta_logger, level=logging.INFO) as captured:
                meta_written = ExportSiteMetadataTask(
                    bundle=bundle,
                    output_layout=site_out,
                    progress=LogProgressReporter(
                        logger=meta_logger, log_steps=True
                    ),
                ).run()
            self.assertEqual(len(meta_written), 8)
            self.assertIn("(8/8 files)", "\n".join(captured.output))

            # Missing schemaorg.owl fails before creating docs/ or partial files.
            (bundle.release_file.parent / "schemaorg.owl").unlink()
            missing_site = root / "missing_site"
            with self.assertRaises(FileNotFoundError):
                ExportSiteMetadataTask(
                    bundle=bundle,
                    output_layout=OutputLayout(missing_site),
                    progress=NullProgressReporter(),
                ).run()
            self.assertFalse((missing_site / "docs").exists())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    unittest.main()
