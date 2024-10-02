#!/usr/bin/env python

# https://developer.github.com/v3/issues/
# https://developer.github.com/v3/repos/
# GET /repos/:owner/:repo/issues

# Beginning of script to scan github for issue/term associations.

# Note: https://developer.github.com/v3/#rate-limiting
# 60 requests per hour per IP address.

import requests  # http://www.python-requests.org/en/latest/
import json
import re
import os

myre = re.compile(r"^\s*http://schema.org/(\w+)", re.MULTILINE)


def getPagedAPI(u):
    r = requests.get(u)
    if r.ok:
        if len(r.json()) == 0:
            return "000"
        for i in r.json():
            if "body" in i:
                body = i["body"]
                hits = myre.findall(body)
                for h in hits:
                    print("http://schema.org/" + h)
                    print(i["url"])
                    if "title" in i:
                        print(i["title"])
                        print("\n")
            print
        return None
    else:
        print("# Issue API error.")
        return "500"


# Auth - to avoid rate limits, create an OAuth application and put details in GH_AUTH env var.
# See https://developer.github.com/v3/#rate-limiting

gh_auth = os.environ["GH_AUTH"]
for i in range(10):
    u = (
        "https://api.github.com/repos/schemaorg/schemaorg/issues?milestone=*;page=%i;%s"
        % (i, gh_auth)
    )
    print("# Fetching page %i " % i)
    x = getPagedAPI(u)  # bogus return codes
    if x != None:
        break
