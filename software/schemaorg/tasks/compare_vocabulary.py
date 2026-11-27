"""Floating task that compares vocabulary terms and triples across sources."""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path

from rdflib import Dataset, Graph, Namespace, RDF, RDFS, URIRef
from rdflib.term import Node

from schemaorg import constants
from schemaorg.graph_loader import GraphLoader
from schemaorg.layout import Domain, InputLayout, Issues, Releases
from schemaorg.progress import ProgressReporter
from schemaorg.sdo_uri import SDO, SdoUri
from schemaorg.version import Version


@dataclass(frozen=True)
class VocabularyDiffReport:
    """Summary and formatted text output of comparing two vocabulary graphs."""

    current_count: int
    previous_count: int
    added: tuple[str, ...]
    dropped: tuple[str, ...]
    changed_count: int
    formatted_report: str


def _parse_rdf_file(path: Path) -> Graph:
    if path.suffix == ".nq":
        ds = Dataset()
        ds.parse(path, format="nquads")
        flat = Graph(bind_namespaces="none")
        for s, p, o, _ in ds.quads((None, None, None, None)):
            flat.add((s, p, o))
        return flat
    return Graph(bind_namespaces="none").parse(path)


def _load_spec(
    input_layout: InputLayout,
    spec: str | None,
    default_to_source: bool,
) -> Graph:
    if spec == "source" or (spec is None and default_to_source):
        return GraphLoader.load(Issues(input_layout).get_ttl_files())

    if spec is not None:
        candidate = Path(spec)
        if candidate.is_dir():
            ttl_files = sorted(candidate.rglob("*.ttl"))
            if not ttl_files:
                raise FileNotFoundError(f"No .ttl files found in {candidate}")
            return GraphLoader.load(ttl_files)
        if candidate.is_file():
            return _parse_rdf_file(candidate)

    version_registry = Version(
        input_layout.file(Domain.ROOT, constants.VERSIONS_FILE)
    )
    releases = Releases(input_layout, version_registry)

    if spec is None:
        declared = releases.versions()
        target_ver = declared[1] if len(declared) > 1 else declared[0]
        spec = str(target_ver)

    try:
        return _parse_rdf_file(releases.get_ttl_files(spec)[0])
    except FileNotFoundError:
        release_dir = releases.dir(spec)
        for fallback in ("schema.nt", "all-layers.nq", "schemaorg-all-http.ttl"):
            fallback_path = release_dir / fallback
            if fallback_path.is_file():
                return _parse_rdf_file(fallback_path)
        raise


def _filter_layers(
    graph: Graph,
    exclude: Iterable[str],
    include: Iterable[str],
) -> Graph:
    included = set(include)
    excluded = set(exclude) - included
    if not excluded:
        return graph

    skip_core = "core" in excluded
    skip_extensions = "extensions" in excluded

    layers_by_subject: dict[Node, set[str]] = {}
    for s, p, o in graph:
        if isinstance(p, URIRef) and SdoUri(p).uri == SDO.isPartOf:
            layer = SdoUri(o).layer()
            if layer != "core":
                layers_by_subject.setdefault(s, set()).add(layer)

    filtered = Graph(bind_namespaces="none")
    for s, p, o in graph:
        layers = layers_by_subject.get(s)
        if not layers:
            if skip_core:
                continue
        elif (layers & excluded) or (
            skip_extensions and not (layers & included)
        ):
            continue
        filtered.add((s, p, o))
    return filtered


def _terms_in_graph(graph: Graph) -> set[str]:
    return {
        str(SdoUri(s))
        for s in graph.subjects(RDF.type, None)
        if isinstance(s, URIRef)
    }


def _term_subgraphs(
    graph: Graph, terms: set[str]
) -> dict[str, set[tuple[Node, Node, Node]]]:
    indexed: dict[str, set[tuple[Node, Node, Node]]] = {t: set() for t in terms}
    for s, p, o in graph:
        if isinstance(s, URIRef):
            subj = SdoUri(s)
            key = str(subj)
            if key in indexed:
                pred = SdoUri(p).uri if isinstance(p, URIRef) else p
                obj = SdoUri(o).uri if isinstance(o, URIRef) else o
                indexed[key].add((subj.uri, pred, obj))
    return indexed


def _compare_common_terms(
    common: set[str],
    previous_graph: Graph,
    current_graph: Graph,
    include_lines: bool,
    show_diffs: bool,
) -> tuple[int, list[str]]:
    qname_graph = Graph(bind_namespaces="none")
    qname_graph.bind("schema", SDO)
    qname_graph.bind("dct", Namespace("http://purl.org/dc/terms/"))
    qname_graph.bind("rdf", RDF)
    qname_graph.bind("rdfs", RDFS)

    prev_by_term = _term_subgraphs(previous_graph, common)
    curr_by_term = _term_subgraphs(current_graph, common)

    def fmt_pred(pred: Node) -> str:
        try:
            return (
                qname_graph.qname(pred)
                if isinstance(pred, URIRef)
                else str(pred)
            )
        except Exception:
            return str(pred)

    changed_count = 0
    lines: list[str] = []
    for term in sorted(common):
        curr_triples = curr_by_term[term]
        prev_triples = prev_by_term[term]
        added = curr_triples - prev_triples
        dropped = prev_triples - curr_triples
        if added or dropped:
            changed_count += 1
            if include_lines:
                lines.append(f"   Changed term: {term}")
                if show_diffs:
                    for s, p, o in sorted(
                        added, key=lambda t: (str(t[1]), str(t[2]))
                    ):
                        lines.append(f"       New:     {s} {fmt_pred(p)} {o}")
                    for s, p, o in sorted(
                        dropped, key=lambda t: (str(t[1]), str(t[2]))
                    ):
                        lines.append(f"       Dropped: {s} {fmt_pred(p)} {o}")
    return changed_count, lines


@dataclass(frozen=True)
class CompareVocabularyTask:
    """Compares vocabulary terms and triples between two schema.org sources."""

    input_layout: InputLayout
    previous_spec: str | None
    current_spec: str | None
    exclude_layers: Sequence[str]
    include_layers: Sequence[str]
    show_names: bool
    show_triples: bool
    progress: ProgressReporter

    def run(self) -> VocabularyDiffReport:
        with self.progress.task(
            "Comparing vocabulary graphs",
            total=3,
            unit="steps",
        ) as p:
            p.step("loading current graph")
            current_graph = _filter_layers(
                _load_spec(
                    self.input_layout,
                    self.current_spec,
                    default_to_source=True,
                ),
                exclude=self.exclude_layers,
                include=self.include_layers,
            )
            p.advance(1)

            p.step("loading previous graph")
            previous_graph = _filter_layers(
                _load_spec(
                    self.input_layout,
                    self.previous_spec,
                    default_to_source=False,
                ),
                exclude=self.exclude_layers,
                include=self.include_layers,
            )
            p.advance(1)

            p.step("computing term and triple diffs")
            cur_terms = _terms_in_graph(current_graph)
            prev_terms = _terms_in_graph(previous_graph)

            added = tuple(sorted(cur_terms - prev_terms))
            dropped = tuple(sorted(prev_terms - cur_terms))
            common = cur_terms & prev_terms

            changed, diff_lines = _compare_common_terms(
                common=common,
                previous_graph=previous_graph,
                current_graph=current_graph,
                include_lines=self.show_names or self.show_triples,
                show_diffs=self.show_triples,
            )

            report_lines = [
                f"Current terms count {len(cur_terms)}",
                f"Previous terms Count {len(prev_terms)}",
                "==========   Terms  ================",
                f"Dropped terms {len(dropped)}",
            ]
            if self.show_names:
                report_lines.extend(f"   Dropped term {t}" for t in dropped)
            report_lines.append(f"New terms {len(added)}")
            if self.show_names:
                report_lines.extend(f"   New term {t}" for t in added)
            report_lines.append(f"Changed terms {changed}")
            report_lines.extend(diff_lines)
            p.advance(1)

        return VocabularyDiffReport(
            current_count=len(cur_terms),
            previous_count=len(prev_terms),
            added=added,
            dropped=dropped,
            changed_count=changed,
            formatted_report="\n".join(report_lines) + "\n",
        )
