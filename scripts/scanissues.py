#!/usr/bin/env python

# https://developer.github.com/v3/issues/
# https://developer.github.com/v3/repos/
# GET /repos/:owner/:repo/issues

# Beginning of script to scan github for issue/term associations.


import requests # http://www.python-requests.org/en/latest/
import json
import re

myre = re.compile(r"^\s*http://schema.org/(\w+)", re.MULTILINE)

def getPagedAPI(u):
    r = requests.get(u) 

    if (r.ok):
        for i in r.json():
          #print i["title"]
          if "body" in i:
              body = i["body"]
              hits = myre.findall(body)
              for h in hits:
                  print i["url"]
                  if "title" in i:
                      print i["title"]
                  print "http://schema.org/"+h
                  print "\n"
          print
    else:
            print "# Issue API error."


# TODO: figure out how (headers?) to know how many pages to fetch.

for i in range(10):
  u = "https://api.github.com/repos/schemaorg/schemaorg/issues?milestone=*;page=%i" % i 
  print "# Fetching: %s " % u
  getPagedAPI(u)
  
