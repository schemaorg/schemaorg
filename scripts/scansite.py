#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
from pprint import pprint

# Work in progress attempt to fetch all term URLs
# from our data dumps (and sanity check them), then
# fetch pages via WWW e.g. for 
# https://github.com/schemaorg/schemaorg/issues/1285
# (We could also generate a sitemap.xml file maybe?)

# params		 TODO: pass this in
v = '3.1' 
verbose = False

#verbose = True

fn = 'data/releases/%s/all-layers.jsonld' % v # Per-release JSON-LD dumps.

print "Scanning fn: %s" % fn

with open(fn) as data_file:
  data = json.load(data_file)
if verbose:
  pprint(data) 

# Core is      "@id": "http://schema.org/#3.1"

# TODO: Not robust. Fix w/ regex to handle versions, cases etc.
#
def subdomain(gurl):
  tid = gurl.replace('http://','')
  tid = tid.replace('#' + str(v),'') # this version
  tid = tid.replace('.schema.org/','') # ext
  tid = tid.replace('schema.org/','') # core
  return( tid )

for g in data["@graph"]:
  pprint("GRAPH: %s" % g["@id"])
  for t in g["@graph"]:
    url = t["@id"]

    if 'schema.org' not in str(url):
      continue # cases like file:// and wikipedia links show up.

    if g['@id'] != "http://schema.org/#%s" % v: # extension
      exturl = url.replace('schema.org', subdomain(g['@id']) + '.schema.org')
    else:
      exturl = '' # core 

    print "%s,\t%s" % (url, exturl)

    # Note that for extensions we may want the subdomain        
    # or the bare term, or both, depending on application needs.
    # i.e. http://schema.org/Thesis (the actual type)
    # or http://bib.schema.org/Thesis (the substantive documentation)
