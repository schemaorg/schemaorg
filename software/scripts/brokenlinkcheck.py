#!/usr/bin/env python3
# Based on a CC0 licensed script shared by Gabriel Romualdo <https://xtrp.io/>

# <https://xtrp.io/blog/2019/11/09/a-quick-python-script-to-find-broken-links/>
"""Basic command line tool to find broken links in a website."""

from __future__ import annotations

import argparse
from collections.abc import Iterator, Sequence
from dataclasses import dataclass
import sys
from urllib.parse import urldefrag, urljoin, urlparse

import bs4
import requests

_SKIPPED_EXTENSIONS: tuple[str, ...] = (".png", ".jpg", ".jpeg", ".gif", ".ico")


@dataclass(frozen=True)
class BadLink:
    bad_link: str
    source: str
    error: str

    def __str__(self) -> str:
        return f"{self.error}: link {self.bad_link} from {self.source}"


def getLinksFromHTML(html: str) -> Iterator[str]:
    for el in bs4.BeautifulSoup(html, features="html.parser").select("a[href]"):
        href = el.get("href")
        if isinstance(href, str):
            yield href


def find_broken_links(
    domain_to_search: str,
    target_url: str,
    parent_url: str = "",
    depth: int = 0,
    targetonly: bool = False,
    timeout: float = 10.0,
    session: requests.Session | None = None,
    searched_links: set[str] | None = None,
) -> tuple[list[BadLink], list[BadLink]]:
    if searched_links is None:
        searched_links = set()
    if session is None:
        with requests.Session() as new_session:
            return find_broken_links(
                domain_to_search=domain_to_search,
                target_url=target_url,
                parent_url=parent_url,
                depth=depth,
                targetonly=targetonly,
                timeout=timeout,
                session=new_session,
                searched_links=searched_links,
            )

    broken_links: list[BadLink] = []
    error_links: list[BadLink] = []
    target_url = urldefrag(target_url).url

    if (
        target_url not in searched_links
        and not target_url.startswith("mailto:")
        and "javascript:" not in target_url
        and not target_url.lower().endswith(_SKIPPED_EXTENSIONS)
    ):
        searched_links.add(target_url)
        try:
            response = session.get(target_url, timeout=timeout)
            if response.status_code >= 400:
                broken_links.append(
                    BadLink(
                        bad_link=target_url,
                        source=parent_url,
                        error=f"Broken ({response.status_code})",
                    )
                )
            elif (
                urlparse(target_url).netloc == domain_to_search
                and "text/html"
                in response.headers.get("Content-Type", "").lower()
                and (not targetonly or depth == 0)
            ):
                for link in getLinksFromHTML(response.text):
                    b, e = find_broken_links(
                        domain_to_search=domain_to_search,
                        target_url=urljoin(target_url, link),
                        parent_url=target_url,
                        depth=depth + 1,
                        targetonly=targetonly,
                        timeout=timeout,
                        session=session,
                        searched_links=searched_links,
                    )
                    broken_links.extend(b)
                    error_links.extend(e)
        except requests.RequestException as exc:
            error_links.append(
                BadLink(
                    bad_link=target_url, source=parent_url, error=f"Error: {exc}"
                )
            )

    return broken_links, error_links


def run_check(
    target_url: str, targetonly: bool = False, timeout: float = 10.0
) -> int:
    print(f"Looking for broken links in {target_url}")
    searched_links: set[str] = set()
    broken_links, error_links = find_broken_links(
        domain_to_search=urlparse(target_url).netloc,
        target_url=target_url,
        targetonly=targetonly,
        timeout=timeout,
        searched_links=searched_links,
    )
    print("\n--- DONE! ---\n")
    print("The following links returned errors:")
    for link in error_links:
        print(f"\t{link}")

    print("\nThe following links were broken:")
    for link in broken_links:
        print(f"\t{link}")

    print(
        f"\nLinks Checked: {len(searched_links)}  "
        f"Broken: {len(broken_links)}  Error: {len(error_links)}"
    )
    return len(error_links) + len(broken_links)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-t",
        "--targetonly",
        action="store_true",
        help="Only check links in target URL",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=10.0,
        help="Per-request HTTP timeout in seconds (default: 10)",
    )
    parser.add_argument("target", help="Target URL to check")
    args = parser.parse_args(argv)
    return run_check(
        target_url=args.target,
        targetonly=args.targetonly,
        timeout=args.timeout,
    )


if __name__ == "__main__":
    sys.exit(main())
