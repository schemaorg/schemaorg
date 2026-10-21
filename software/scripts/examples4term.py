#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import csv
from pathlib import Path
from typing import Iterable, List, Set

from SchemaExamples.schemaexamples import Example, SchemaExamples
from SchemaTerms.sdoterm import SdoTerm
from SchemaTerms.sdotermsource import SdoTermSource
import util.textutils as textutils


def _add_subterms(term: SdoTerm, seen: Set[str], result: List[str]) -> None:
    for sub_id in term.subs.ids:
        if sub_id not in seen:
            seen.add(sub_id)
            result.append(sub_id)
        if sub_term := SdoTermSource.getTerm(sub_id):
            _add_subterms(sub_term, seen, result)


def getterms(term_groups: Iterable[Iterable[str]], recursive: bool) -> List[str]:
    result: List[str] = []
    seen: Set[str] = set()

    for t in (t for group in term_groups for t in group):
        term = SdoTermSource.getTerm(t)
        if not term:
            print(f"No such term: {t}")
            continue
        if term.id not in seen:
            seen.add(term.id)
            result.append(term.id)
        if recursive:
            _add_subterms(term, seen, result)

    return result


def getexamples(terms: Iterable[str]) -> List[Example]:
    result: List[Example] = []
    for t in terms:
        for e in SchemaExamples.examplesForTerm(t):
            if e not in result:
                result.append(e)
    return result


def buildoutput(examples: Iterable[Example], fname: str) -> None:
    buildcsvoutput(sorted(examples, key=lambda x: str(x.keyvalue)), fname)


def buildcsvoutput(examples: Iterable[Example], fname: str) -> None:
    if not fname.endswith(".csv"):
        fname = f"{fname}.csv"

    fields = ["Example Id", "Source File", "Linked to Terms"]
    data = [
        {
            "Example Id": e.keyvalue,
            "Source File": e.getMeta("source"),
            "Linked to Terms": textutils.Array2String(e.terms),
        }
        for e in examples
    ]

    print(f"examples4term: Writing to: {fname}")
    with Path(fname).open("w", encoding="utf-8", newline="") as csvfile:
        writer = csv.DictWriter(
            csvfile, fieldnames=fields, quoting=csv.QUOTE_ALL, lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(data)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-t",
        "--term",
        required=True,
        default=[],
        action="append",
        nargs="*",
        help="Term to use(repeatable)",
    )
    parser.add_argument(
        "-r",
        "--recursive",
        default=False,
        action="store_true",
        help="Use term and subtypes",
    )
    parser.add_argument("-o", "--output", required=True, help="csv output file")
    args = parser.parse_args()

    if not SdoTermSource.SOURCEGRAPH:
        print("Loading triples files")
        SdoTermSource.loadSourceGraph("default")
        print(
            f"loaded {len(SdoTermSource.sourceGraph())} triples - "
            f"{len(SdoTermSource.getAllTerms())} terms"
        )

    terms = getterms(args.term, args.recursive)
    examples = getexamples(terms)
    buildoutput(examples, args.output)
