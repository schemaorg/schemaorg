#!/usr/bin/env python

# https://developer.github.com/v3/issues/
# https://developer.github.com/v3/repos/
# GET /repos/:owner/:repo/issues

# Beginning of script to scan github for issue/term associations.

import requests # http://www.python-requests.org/en/latest/
import json
import re

r = requests.get('https://api.github.com/repos/schemaorg/schemaorg/issues?milestone=*')

myre = re.compile(r"^\s*http://schema.org/(\w+)", re.MULTILINE)

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
        print "Issue API error."

# PROBLEM
#  curl https://api.github.com/repos/schemaorg/schemaorg/issues | grep number > x
#  this isn't listing all issues.

# ~/working/sdo/official/schemaorg[(sdo-stantz)0|0] $ curl -s  "https://api.github.com/repos/schemaorg/schemaorg/issues?milestone=*" | grep 'milestones/' | grep url | wc -l
#      60
#~/working/sdo/official/schemaorg[(sdo-stantz)0|0] $ curl -s  "https://api.github.com/repos/schemaorg/schemaorg/issues" | grep 'milestones/' | grep url | wc -l
#      40
# 
# https://api.github.com/repos/schemaorg/schemaorg/issues?milestone=*&assignee=*&since=2014-01-01
#
# It seems not all issues are returned by this API call.
# -> https://twitter.com/danbri/status/560788325653823488
