#!/usr/bin/env python3
"""Convert RDF vocabulary files across formats while stripping legacy schema:category triples."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

import rdflib
from rdflib.term import URIRef

from schemaorg.sdo_uri import SCHEMA_URL, SDO

SCHEMA_HTTP: rdflib.Namespace = rdflib.Namespace(
    SCHEMA_URL._replace(scheme="http").geturl()
)

OUTTYPES: dict[str, str] = {
    "jsonld": "json-ld",
    "json-ld": "json-ld",
    "xml": "xml",
    "rdf": "xml",
    "nq": "nquads",
    "nquads": "nquads",
    "nt": "nt",
    "ttl": "turtle",
    "turtle": "turtle",
}

_INPUT_FORMATS: dict[str, str] = {
    "jsonld": "json-ld",
    "nq": "nquads",
    "nt": "nt",
    "rdf": "xml",
    "ttl": "turtle",
    "xml": "xml",
}


def _strip_categories(target: rdflib.Graph | rdflib.Dataset) -> None:
    if isinstance(target, rdflib.Dataset):
        for ctx in target.graphs():
            ctx.remove((None, SCHEMA_HTTP.category, None))
            ctx.remove((None, SDO.category, None))
    else:
        target.remove((None, SCHEMA_HTTP.category, None))
        target.remove((None, SDO.category, None))


def _write_graph(
    graph: rdflib.Graph | rdflib.Dataset,
    outfile: Path,
    serializer_fmt: str,
    default_ns: str,
) -> None:
    _strip_categories(graph)
    graph.bind("", URIRef(default_ns), override=True)
    outfile.parent.mkdir(parents=True, exist_ok=True)
    kwargs = {"auto_compact": True} if serializer_fmt == "json-ld" else {}
    print(f"Writing {len(graph)} triples to {outfile}")
    outfile.write_text(
        str(graph.serialize(format=serializer_fmt, **kwargs)),
        encoding="utf-8",
    )


def _new_graph(use_dataset: bool) -> rdflib.Graph | rdflib.Dataset:
    return rdflib.Dataset() if use_dataset else rdflib.Graph()


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-i",
        "--input",
        required=True,
        default=[],
        action="extend",
        nargs="+",
        type=Path,
        help="Input RDF file(s)",
    )
    parser.add_argument(
        "-o", "--outputdir", type=Path, help="Output directory (default: alongside input or cwd)"
    )
    parser.add_argument(
        "-f",
        "--format",
        default="ttl",
        choices=tuple(OUTTYPES),
        help="Output format",
    )
    parser.add_argument(
        "-c", "--combinefile", help="Combine all inputs into a single output file"
    )
    parser.add_argument(
        "-d",
        "--defaultns",
        default=str(SDO),
        help=f"Default output namespace (default: {SDO})",
    )
    args = parser.parse_args(argv)

    serializer_fmt = OUTTYPES[args.format]
    use_dataset = serializer_fmt == "nquads" or any(
        p.suffix.lower() == ".nq" for p in args.input
    )
    combined_graph = _new_graph(use_dataset)

    for input_path in args.input:
        target_graph = combined_graph if args.combinefile else _new_graph(use_dataset)
        ext = input_path.suffix.lstrip(".").lower()
        input_fmt = _INPUT_FORMATS.get(ext)
        if isinstance(target_graph, rdflib.Dataset) and input_fmt != "nquads":
            target_graph.default_graph.parse(input_path, format=input_fmt)
        else:
            target_graph.parse(input_path, format=input_fmt)
        print(f"Loaded {len(target_graph)} triples from {input_path}")

        if not args.combinefile:
            base_dir = args.outputdir if args.outputdir else input_path.parent
            outfile = base_dir / f"{input_path.stem}.{args.format}"
            _write_graph(target_graph, outfile, serializer_fmt, args.defaultns)

    if args.combinefile:
        outfile = (
            args.outputdir / args.combinefile
            if args.outputdir
            else Path(args.combinefile)
        )
        _write_graph(combined_graph, outfile, serializer_fmt, args.defaultns)


if __name__ == "__main__":
    main()
