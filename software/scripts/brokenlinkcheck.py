#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# Note: links below are broken.
# Based on a CC0 licensed script <https://xtrp.io/blog/2019/11/09/a-quick-python-script-to-find-broken-links/>
# Shared by Gabriel Romualdo <https://xtrp.io/>


"""Basic command line tool to find broken links in a web-site."""

import argparse
import bs4
import requests
import sys


from urllib.parse import urlparse, urldefrag, urljoin


class BadLink:
    def __init__(self, bad_link, source, error):
        self.bad_link = bad_link
        self.source = source
        self.error = error

    def __str__(self):
        return "%s: link %s from %s" % (self.error, self.bad_link, self.source)


searched_links = set()


def getLinksFromHTML(html):
    return map(
        lambda el: el["href"],
        bs4.BeautifulSoup(html, features="html.parser").select("a[href]"),
    )


def find_broken_links(
    domainToSearch, target_url, parent_url="", depth=0, targetonly=False
):
    broken_links = []
    error_links = []
    target_url = urldefrag(target_url).url

    if (
        (not (target_url in searched_links))
        and (not target_url.startswith("mailto:"))
        and (not ("javascript:" in target_url))
        and (not target_url.endswith(".png"))
        and (not target_url.endswith(".jpg"))
        and (not target_url.endswith(".jpeg"))
    ):
        try:
            searched_links.add(target_url)
            requestObj = requests.get(target_url)
            if requestObj.status_code == 404:
                broken_links.append(
                    BadLink(
                        bad_link=target_url, source=parent_url, error="Broken (404)"
                    )
                )
            else:
                if urlparse(target_url).netloc == domainToSearch:
                    for link in getLinksFromHTML(requestObj.text):
                        if not targetonly or not depth:
                            b, e = find_broken_links(
                                domainToSearch=domainToSearch,
                                target_url=urljoin(target_url, link),
                                parent_url=target_url,
                                depth=depth + 1,
                                targetonly=targetonly,
                            )
                            broken_links.extend(b)
                            error_links.extend(e)
        except Exception as e:
            error_links.append(
                BadLink(bad_link=target_url, source=parent_url, error="Error: %s" % e)
            )

    return (broken_links, error_links)


def main(target_url, targetonly):
    print("Looking for broken links in %s" % target_url)
    broken_links, error_links = find_broken_links(
        domainToSearch=urlparse(target_url).netloc,
        target_url=target_url,
        targetonly=targetonly,
    )
    print("\n--- DONE! ---\n")
    print("The following links returned errors:")
    for link in error_links:
        print("\t%s" % link)

    print("\nThe following links were broken:")
    for link in broken_links:
        print("\t%s" % link)

    print(
        "\nLinks Checked: %d  Broken: %d  Error: %d "
        % (len(searched_links), len(broken_links), len(error_links))
    )
    return len(error_links) + len(broken_links)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-t",
        "--targetonly",
        default=False,
        action="store_true",
        help="Only check links in target URL",
    )
    parser.add_argument("target")
    args = parser.parse_args()
    sys.exit(main(target_url=args.target, targetonly=args.targetonly))
