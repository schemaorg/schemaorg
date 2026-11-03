#!/usr/bin/env python3
"""Scan term pages on a schema.org host for an unexpected substring (e.g. markdown artifacts)."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path
import sys
from urllib.parse import urlparse

from rdflib import Graph, RDF, URIRef
import requests

from schemaorg.graph_loader import GraphLoader
from schemaorg.layout import Releases
from schemaorg.sdo_uri import SCHEMA_URL, SDO, SdoUri
import util.paths as paths
import util.schema as schema

DEFAULT_SEARCH_TERM: str = "klzzwxh"


def _load_vocab_graph(vocab_path: Path) -> Graph:
    if vocab_path.suffix == ".ttl":
        return GraphLoader.load([vocab_path])
    return Graph().parse(vocab_path)


def collect_term_urls(graph: Graph, site_base: str) -> tuple[list[str], list[str]]:
    """Return sorted `(term_urls, extension_urls)` targeted at `site_base`."""
    parsed_site = urlparse(
        site_base if "://" in site_base else f"https://{site_base}"
    )
    scheme = parsed_site.scheme or "https"
    netloc = parsed_site.netloc or (SCHEMA_URL.hostname or "schema.org")
    base_host = SCHEMA_URL.hostname or "schema.org"

    def rewrite_host(uri: str) -> str:
        parsed = urlparse(uri)
        if parsed.netloc == base_host or netloc.startswith("localhost") or ":" in netloc:
            return parsed._replace(scheme=scheme, netloc=netloc).geturl()
        target_netloc = parsed.netloc.replace(base_host, netloc, 1)
        return parsed._replace(scheme=scheme, netloc=target_netloc).geturl()

    extensions: set[str] = set()
    for part in graph.objects(None, SDO.isPartOf):
        sdo_part = SdoUri(part)
        if sdo_part.is_sdo() and sdo_part.layer() != "core":
            extensions.add(sdo_part.layer())

    term_urls: set[str] = set()
    for subject in graph.subjects(RDF.type, None):
        if not isinstance(subject, URIRef):
            continue
        sdo_term = SdoUri(subject)
        if not sdo_term.is_sdo():
            continue
        term_urls.add(rewrite_host(str(sdo_term)))

    ext_urls = [
        rewrite_host(str(SdoUri.for_layer(ext))) for ext in sorted(extensions)
    ]
    return sorted(term_urls), ext_urls


def check_url(
    session: requests.Session,
    url: str,
    search_term: str,
    timeout: float,
    verbose: bool = False,
) -> str | None:
    try:
        response = session.get(url, timeout=timeout)
        response.raise_for_status()
    except requests.RequestException as exc:
        print(f"EXCEPT: {url}: {exc}")
        return None

    count = response.text.count(search_term)
    if count:
        msg = f"{url} - Found {count} instances"
        print(msg)
        return msg
    if verbose:
        print(f"{url} clear")
    return None


def main(argv: Sequence[str] | None = None) -> int:
    default_vocab = Releases(paths.DefaultInputLayout(), schema.VERSION).file()

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--site",
        default=SCHEMA_URL.geturl().rstrip("/"),
        help="Target site base URL (default: https://schema.org)",
    )
    parser.add_argument(
        "--vocab",
        type=Path,
        default=default_vocab,
        help="Vocabulary RDF file to extract terms from (default: current release TTL)",
    )
    parser.add_argument(
        "--search",
        default=DEFAULT_SEARCH_TERM,
        help=f"Substring to scan for (default: {DEFAULT_SEARCH_TERM!r})",
    )
    parser.add_argument(
        "--terms-only",
        action="store_true",
        help="List target URLs without fetching pages over HTTP",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=10.0,
        help="HTTP request timeout in seconds (default: 10)",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Print clear URLs as well"
    )
    args = parser.parse_args(argv)

    if not args.vocab.is_file():
        print(f"Vocabulary file not found: {args.vocab}", file=sys.stderr)
        return 1

    print(f"\nScanning file: {args.vocab}")
    print(f"Searching for: {args.search}")
    print(f"Searching target: {args.site}\n")

    graph = _load_vocab_graph(args.vocab)
    term_urls, ext_urls = collect_term_urls(graph, args.site)
    all_urls = [*term_urls, *ext_urls]

    if args.terms_only:
        for url in all_urls:
            print(url)
        print(f"\nListed {len(all_urls)} target URLs")
        return 0

    found: list[str] = []
    with requests.Session() as session:
        for url in all_urls:
            hit = check_url(
                session=session,
                url=url,
                search_term=args.search,
                timeout=args.timeout,
                verbose=args.verbose,
            )
            if hit:
                found.append(hit)

    print(f"\nChecked {len(all_urls)} pages")
    if found:
        print(f"Found '{args.search}' in {len(found)} pages")
        for msg in found:
            print(msg)
        return 1

    print(f"Found 0 instances of {args.search}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
