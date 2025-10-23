#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import io
import os
import sys

if not (sys.version_info.major == 3 and sys.version_info.minor > 5):
    print(
        "Python version %s.%s not supported version 3.6 or above required - exiting"
        % (sys.version_info.major, sys.version_info.minor)
    )
    sys.exit(1)


for path in [
    os.getcwd(),
    "software/Util",
    "software/SchemaTerms",
    "software/SchemaExamples",
]:
    sys.path.insert(1, path)  # Pickup libs from local  directories

from sdotermsource import SdoTermSource
from schemaexamples import SchemaExamples


if not SdoTermSource.SOURCEGRAPH:
    print("Loading triples files")
    SdoTermSource.loadSourceGraph("default")
    print(
        "loaded %s triples - %s terms"
        % (len(SdoTermSource.sourceGraph()), len(SdoTermSource.getAllTerms()))
    )

workingterms = []


def getterms(term, recursive):
    global workingterms

    termlist = []
    for ts in term:
        termlist.extend(ts)

    for t in termlist:
        term = SdoTermSource.getTerm(t)
        if not term:
            print("No such term: %s" % t)
            continue
        addtoworking(term.id)

        if recursive:
            addrecursive(term)


def addtoworking(term):
    global workingterms
    if term not in workingterms:
        workingterms.append(term)


def addrecursive(term):
    for t in term.subs:
        addtoworking(t)
        addrecursive(SdoTermSource.getTerm(t))


def getexamples(terms):
    for t in terms:
        examples = SchemaExamples.examplesForTerm(t)
        addtoworkingex(examples)


workingex = []


def addtoworkingex(examples):
    for e in examples:
        if e not in workingex:
            workingex.append(e)


def buildoutput(workingex, fname):
    workingex = sorted(workingex, key=lambda x: (x.keyvalue))

    buildcsvoutput(workingex, fname)


def buildcsvoutput(workingex, fname):
    import csv

    if not fname.endswith(".csv"):
        fname = fname + ".csv"

    data = []
    fields = ["Example Id", "Source File", "Linked to Terms"]
    for e in workingex:
        row = {}
        row["Example Id"] = e.keyvalue
        row["Source File"] = e.getMeta("source")
        row["Linked to Terms"] = array2str(e.terms)
        data.append(row)

    csvout = io.StringIO()
    print("examples4term: Writing to: %s" % fname)

    csvfile = open(fname, "w", encoding="utf8")
    writer = csv.DictWriter(
        csvout, fieldnames=fields, quoting=csv.QUOTE_ALL, lineterminator="\n"
    )
    writer.writeheader()
    for row in data:
        writer.writerow(row)
    csvfile.write(csvout.getvalue())
    csvfile.close()


def array2str(ar):
    if not ar or not len(ar):
        return ""
    buf = []
    first = True
    for i in ar:
        if first:
            first = False
        else:
            buf.append(", ")
        buf.append(i)
    return "".join(buf)


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
        help="Use tern=m and subtypes",
    )
    parser.add_argument("-o", "--output", required=True, help="csv output file")
    args = parser.parse_args()

    getterms(args.term, args.recursive)
    getexamples(workingterms)
    fname = args.output
    buildoutput(workingex, fname)
