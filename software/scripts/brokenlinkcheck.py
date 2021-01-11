#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# Based on a CC0 licensed script <https://xtrp.io/blog/2019/11/09/a-quick-python-script-to-find-broken-links/>
# Shared by Gabriel Romualdo <https://xtrp.io/>

import requests
import sys
import argparse
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urldefrag, urljoin

searched_links = []
broken_links = []
error_links = []

def getLinksFromHTML(html):
    def getLink(el):
        return el["href"]
    return list(map(getLink, BeautifulSoup(html, features="html.parser").select("a[href]")))

def find_broken_links(domainToSearch, URL, parentURL, depth=0):
    URL = urldefrag(URL).url
    if (not (URL in searched_links)) and (not URL.startswith("mailto:")) and (not ("javascript:" in URL)) and (not URL.endswith(".png")) and (not URL.endswith(".jpg")) and (not URL.endswith(".jpeg")):
        try:
            searched_links.append(URL)
            requestObj = requests.get(URL)
            if(requestObj.status_code == 404):
                broken_links.append("\rBROKEN: link " + URL + " from " + parentURL)
                print(broken_links[-1])
            else:
                #print("NOT BROKEN: link " + URL + " from " + parentURL)
                if urlparse(URL).netloc == domainToSearch:
                    for link in getLinksFromHTML(requestObj.text):
                        if not args.targetonly or not depth:
                            find_broken_links(domainToSearch, urljoin(URL, link), URL, depth=depth + 1)
        except Exception as e:
            error_links.append("\rError: link " + URL + " from " + parentURL + " >>> " + str(e))
            print(error_links[-1])
    
    sys.stdout.write("\rLinks Checked: %d  Broken: %d  Error: %d " %(len(searched_links), len(broken_links), len(error_links)))
    sys.stdout.flush()

parser = argparse.ArgumentParser()
parser.add_argument("-t","--targetonly",default=False, action='store_true', help="Only check links in target URL")
parser.add_argument("target")
args = parser.parse_args()


find_broken_links(urlparse(args.target).netloc, args.target, "")

print("\n--- DONE! ---\n")

print("The following links returned errors:")
for link in error_links:
    print ("\t" + link)
    
print("\nThe following links were broken:")
for link in broken_links:
    print ("\t" + link)

print("\nLinks Checked: %d  Broken: %d  Error: %d " %(len(searched_links), len(broken_links), len(error_links)))

sys.exit(len(error_links) + len(broken_links))
