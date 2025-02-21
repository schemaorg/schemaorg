#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
from pprint import pprint
import urllib2
from google.appengine.api import urlfetch

# Work in progress attempt to fetch all term URLs
# from our data dumps (and sanity check them), then
# fetch pages via WWW e.g. for
# https://github.com/schemaorg/schemaorg/issues/1285
# (We could also generate a sitemap.xml file maybe?)

# params		 TODO: pass this in
v = "3.1"
verbose = False
SEARCH_TERM = "klzzwxh"
host = "schema.org"
# host = "staging.schema.org"
# host = "localhost:8080"

# verbose = True

fn = "data/releases/%s/schemaorg-current.jsonld" % v  # Per-release JSON-LD dumps.
found = []
checked = 0

print("\nScanning file: %s" % fn)
print("Searching for: %s" % SEARCH_TERM)
print("Searching target: %s\n" % host)

with open(fn) as data_file:
    data = json.load(data_file)
if verbose:
    pprint(data)

# Core is      "@id": "http://schema.org/#3.1"


# TODO: Not robust. Fix w/ regex to handle versions, cases etc.
#
def subdomain(gurl):
    tid = gurl.replace("http://", "")
    tid = tid.replace("#" + str(v), "")  # this version
    tid = tid.replace(".schema.org/", "")  # ext
    tid = tid.replace("schema.org/", "")  # core
    return tid


def checkurl(url):
    global checked
    checked += 1

    try:
        result = urllib2.urlopen(str(url))
        thepage = result.read()
    except Exception as e:
        print("EXCEPT: %s" % str(e))
    else:
        count = thepage.count(SEARCH_TERM)
        if count:
            msg = "%s - Found %s instances" % (url, count)
            found.append(msg)
            print(msg)
        else:
            print("%s clear" % url)


extensions = []

for g in sorted(data["@graph"], key=lambda u: u["@id"]):
    # pprint("GRAPH: %s" % g["@id"])
    for t in sorted(g["@graph"], key=lambda u: u["@id"]):
        url = t["@id"]
        targeturl = url

        if "schema.org" not in str(url):
            continue  # cases like file:// and wikipedia links show up.

        if g["@id"] != "http://schema.org/#%s" % v:  # extension
            ext = subdomain(g["@id"])
            if ext not in extensions:
                extensions.append(ext)
                print("Extension: %s" % ext)
            exturl = url.replace("schema.org", ext + ".schema.org")
            targeturl = exturl
        else:
            exturl = ""  # core

        if host != "schema.org":
            targeturl = targeturl.replace("schema.org", host)

        # print "%s, %s,\t%s" % (targeturl, url, exturl)
        checkurl(targeturl)

# Check extension home pages

for e in extensions:
    e = "http://%s.%s" % (e, host)
    # print e
    checkurl(e)

print("\nChecked %s pages" % checked)
if len(found):
    print("Found '%s' in %s pages" % (SEARCH_TERM, len(found)))
    for f in found:
        print(f)
else:
    print("Found 0 instances of %s" % SEARCH_TERM())
