#!/usr/bin/env python3

from __future__ import annotations

import json
from pprint import pprint
from urllib.parse import urlparse

import urllib2

from schemaorg.sdo_uri import SCHEMA_URL, SdoUri

# Work in progress attempt to fetch all term URLs
# from our data dumps (and sanity check them), then
# fetch pages via WWW e.g. for
# https://github.com/schemaorg/schemaorg/issues/1285
# (We could also generate a sitemap.xml file maybe?)

# params		 TODO: pass this in
v = "3.1"
verbose = False
SEARCH_TERM = "klzzwxh"
host = SCHEMA_URL.hostname
# host = f"staging.{SCHEMA_URL.hostname}"
# host = "localhost:8080"


# Points a schema.org URI of any layer at the host under test.
def on_test_host(uri: str) -> str:
    return uri.replace(SCHEMA_URL.hostname or "", host, 1)


# verbose = True

fn = f"data/releases/{v}/schemaorg-current.jsonld"  # Per-release JSON-LD dumps.
found = []
checked = 0

print(f"\nScanning file: {fn}")
print(f"Searching for: {SEARCH_TERM}")
print(f"Searching target: {host}\n")

with open(fn) as data_file:
    data = json.load(data_file)
if verbose:
    pprint(data)

# Core is      "@id": "http://schema.org/#3.1"


def checkurl(url):
    global checked
    checked += 1

    try:
        result = urllib2.urlopen(str(url))
        thepage = result.read()
    except Exception as e:
        print(f"EXCEPT: {e}")
    else:
        count = thepage.count(SEARCH_TERM)
        if count:
            msg = f"{url} - Found {count} instances"
            found.append(msg)
            print(msg)
        else:
            print(f"{url} clear")


extensions = []

for g in sorted(data["@graph"], key=lambda u: u["@id"]):
    # pprint("GRAPH: %s" % g["@id"])
    layer = SdoUri(g["@id"]).layer()
    if layer != "core" and layer not in extensions:
        extensions.append(layer)
        print(f"Extension: {layer}")
    layer_host = urlparse(str(SdoUri.for_layer(layer))).netloc
    for t in sorted(g["@graph"], key=lambda u: u["@id"]):
        url = t["@id"]

        if not SdoUri(url).is_sdo():
            continue  # cases like file:// and wikipedia links show up.

        # Extension terms are served from the layer host; scheme as dumped.
        targeturl = on_test_host(urlparse(url)._replace(netloc=layer_host).geturl())
        checkurl(targeturl)

# Check extension home pages

for e in extensions:
    e = on_test_host(urlparse(str(SdoUri.for_layer(e)))._replace(scheme="http").geturl())
    # print e
    checkurl(e)

print(f"\nChecked {checked} pages")
if len(found):
    print(f"Found '{SEARCH_TERM}' in {len(found)} pages")
    for f in found:
        print(f)
else:
    print(f"Found 0 instances of {SEARCH_TERM()}")
