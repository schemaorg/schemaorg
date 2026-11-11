#!/usr/bin/env python3
"""Compare vocabulary terms and triples between two schema.org releases or sources."""

from __future__ import annotations

import argparse
from collections.abc import Iterable, Sequence
import io
import logging
from pathlib import Path

from rdflib import Graph, Namespace, RDF, RDFS, URIRef
from rdflib.term import Node

from schemaorg.graph_loader import GraphLoader
from schemaorg.layout import Issues, Releases
from schemaorg.sdo_uri import SDO, SdoUri
import util.paths as paths
import util.schema as schema

log: logging.Logger = logging.getLogger(__name__)


def _parse_bool_arg(value: str | bool) -> bool:
    if isinstance(value, bool):
        return value
    lowered = value.strip().lower()
    if lowered in ("yes", "true", "1", "y"):
        return True
    if lowered in ("no", "false", "0", "n"):
        return False
    raise argparse.ArgumentTypeError(f"Expected Yes or No, got {value!r}")


def _load_spec(spec: str | None, *, default_to_source: bool) -> Graph:
    input_layout = paths.DefaultInputLayout()
    releases = Releases(input_layout, schema.VERSION)

    if spec is None:
        if default_to_source:
            return GraphLoader.load(Issues(input_layout).get_ttl_files())
        declared = releases.versions()
        target_ver = declared[1] if len(declared) > 1 else declared[0]
        spec = str(target_ver)

    if spec == "source":
        return GraphLoader.load(Issues(input_layout).get_ttl_files())

    candidate = Path(spec)
    if candidate.is_dir():
        return GraphLoader.load(sorted(candidate.rglob("*.ttl")))
    if candidate.is_file():
        if candidate.suffix == ".ttl":
            return GraphLoader.load([candidate])
        return Graph().parse(candidate)

    try:
        return GraphLoader.load(releases.get_ttl_files(spec))
    except FileNotFoundError:
        release_dir = releases.dir(spec)
        for fallback in ("schema.nt", "all-layers.nq", "schemaorg-all-http.ttl"):
            fallback_path = release_dir / fallback
            if fallback_path.is_file():
                return Graph().parse(fallback_path)
        raise


def _filter_layers(
    graph: Graph,
    exclude: Iterable[str],
    include: Iterable[str],
) -> Graph:
    excluded = set(exclude) - set(include)
    if not excluded:
        return graph

    skip_core = "core" in excluded
    skip_extensions = "extensions" in excluded

    layers_by_subject: dict[Node, set[str]] = {}
    for s, p, o in graph:
        if isinstance(p, URIRef) and SdoUri(p).uri == SDO.isPartOf:
            layers_by_subject.setdefault(s, set()).add(SdoUri(o).layer())

    filtered = Graph(bind_namespaces="none")
    for s, p, o in graph:
        layers = layers_by_subject.get(s)
        if not layers:
            if skip_core:
                continue
        else:
            if skip_extensions or (layers & excluded):
                continue
        filtered.add((s, p, o))
    return filtered


def termsInGraph(g: Graph) -> set[str]:
    """Return canonicalized URIs of all typed subjects in `g`."""
    return {
        str(SdoUri(s))
        for s in g.subjects(RDF.type, None)
        if isinstance(s, URIRef)
    }


def _term_subgraphs(
    g: Graph, terms: set[str]
) -> dict[str, set[tuple[Node, Node, Node]]]:
    indexed: dict[str, set[tuple[Node, Node, Node]]] = {t: set() for t in terms}
    for s, p, o in g:
        if isinstance(s, URIRef):
            subj = SdoUri(s)
            key = str(subj)
            if key in indexed:
                pred = SdoUri(p).uri if isinstance(p, URIRef) else p
                obj = SdoUri(o).uri if isinstance(o, URIRef) else o
                indexed[key].add((subj.uri, pred, obj))
    return indexed


def compareCommonTerms(
    common: set[str],
    previous_graph: Graph,
    current_graph: Graph,
    buff: io.StringIO,
    show_diffs: bool = False,
) -> int:
    qname_graph = Graph()
    qname_graph.bind("schema", SDO)
    qname_graph.bind("dc", Namespace("http://purl.org/dc/terms/"))
    qname_graph.bind("rdf", RDF)
    qname_graph.bind("rdfs", RDFS)

    prev_by_term = _term_subgraphs(previous_graph, common)
    curr_by_term = _term_subgraphs(current_graph, common)

    def fmt_pred(pred: Node) -> str:
        try:
            return qname_graph.qname(pred) if isinstance(pred, URIRef) else str(pred)
        except Exception:
            return str(pred)

    changed_count = 0
    for term in sorted(common):
        curr_triples = curr_by_term[term]
        prev_triples = prev_by_term[term]
        added = curr_triples - prev_triples
        dropped = prev_triples - curr_triples
        if added or dropped:
            changed_count += 1
            buff.write(f"   Changed term: {term}\n")
            if show_diffs:
                for s, p, o in sorted(added, key=lambda t: (str(t[1]), str(t[2]))):
                    buff.write(f"       New:     {s} {fmt_pred(p)} {o}\n")
                for s, p, o in sorted(dropped, key=lambda t: (str(t[1]), str(t[2]))):
                    buff.write(f"       Dropped: {s} {fmt_pred(p)} {o}\n")
    return changed_count


def main(argv: Sequence[str] | None = None) -> None:
    logging.basicConfig(level=logging.INFO)
    # Historical releases predate HTTPS; suppress per-URI upgrade chatter.
    logging.getLogger("schemaorg.sdo_uri").setLevel(logging.ERROR)

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-p",
        "--previous",
        help="Previous release version or path (default: previous release in versions.json)",
    )
    parser.add_argument(
        "-c",
        "--current",
        help="Current release version, 'source', or path (default: working-tree source TTLs)",
    )
    parser.add_argument(
        "-e",
        "--exclude",
        default=[],
        action="extend",
        nargs="*",
        help="Exclude layer(s) [core|extensions|pending|attic|meta|auto|bib|...] (repeatable)",
    )
    parser.add_argument(
        "-i",
        "--include",
        default=[],
        action="extend",
        nargs="*",
        help="Include layer(s), overriding --exclude (repeatable)",
    )
    parser.add_argument(
        "-t",
        "--triples",
        nargs="?",
        const=True,
        default=False,
        type=_parse_bool_arg,
        help="Show triple differences (Yes/No or flag)",
    )
    parser.add_argument(
        "-n",
        "--names",
        nargs="?",
        const=True,
        default=False,
        type=_parse_bool_arg,
        help="List added, dropped, and changed term names (Yes/No or flag)",
    )
    args = parser.parse_args(argv)

    current_graph = _filter_layers(
        _load_spec(args.current, default_to_source=True),
        exclude=args.exclude,
        include=args.include,
    )
    previous_graph = _filter_layers(
        _load_spec(args.previous, default_to_source=False),
        exclude=args.exclude,
        include=args.include,
    )

    cur_terms = termsInGraph(current_graph)
    prev_terms = termsInGraph(previous_graph)

    print(f"Current terms count {len(cur_terms)}")
    print(f"Previous terms Count {len(prev_terms)}")

    added = cur_terms - prev_terms
    dropped = prev_terms - cur_terms
    common = cur_terms & prev_terms

    print("==========   Terms  ================")
    print(f"Dropped terms {len(dropped)}")
    if args.names:
        for term in sorted(dropped):
            print(f"   Dropped term {term}")
    print(f"New terms {len(added)}")
    if args.names:
        for term in sorted(added):
            print(f"   New term {term}")

    buff = io.StringIO()
    changed = compareCommonTerms(
        common=common,
        previous_graph=previous_graph,
        current_graph=current_graph,
        buff=buff,
        show_diffs=args.triples,
    )
    print(f"Changed terms {changed}")
    if args.names or args.triples:
        output = buff.getvalue()
        if output:
            print(output, end="")


if __name__ == "__main__":
    main()
