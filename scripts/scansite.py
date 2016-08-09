#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
from pprint import pprint

# Work in progress attempt to fetch all term URLs
# from our data dumps (and sanity check them), then
# fetch pages via WWW e.g. for 
# https://github.com/schemaorg/schemaorg/issues/1285
# (We could also generate a sitemap.xml file maybe?)

# STATUS: Not working yet. Didn't find /Person from core.

# params		 TODO: pass this in
v = '3.1' 
verbose = True


fn = 'data/releases/%s/all-layers.jsonld' % v # Per-release JSON-LD dumps.

print "Scanning fn: %s" % fn

with open(fn) as data_file:
  data = json.load(data_file)
if verbose:
  pprint(data) 

for g in data["@graph"]:
  pprint("GRAPH: %s " % g["@id"])
  for t in g["@graph"]:
    url = t["@id"]

    if 'schema.org' not in url:
      break # cases like file:// and wikipedia links show up.

    print url

    # Note that for extensions we may want the subdomain     
    # or the bare term, or both, depending on application needs.
    # i.e. http://schema.org/Thesis (the actual type)
    # or http://bib.schema.org/Thesis (the substantive documentation)

# doesn't print Person yet
