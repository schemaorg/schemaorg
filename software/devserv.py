#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import sys
from pathlib import Path
from typing import Any, Dict, Optional, List

from colorama import Fore, Style
from flask import Flask, after_this_request, Response

for path in [Path.cwd(), Path("software/util")]:
    if str(path) not in sys.path:
        sys.path.insert(1, str(path))

from software.util.schemaversion import getVersion

parser: argparse.ArgumentParser = argparse.ArgumentParser()
parser.add_argument("--host", default="localhost", help="Host (default: localhost)")
parser.add_argument("--port", type=int, default=8080, help="Port (default: 8080)")
parser.add_argument("--production", default=False, action="store_true", help="Production settings")
args_parsed: argparse.Namespace = parser.parse_args()

app: Flask = Flask(__name__, static_folder="site", static_url_path="")


@app.route("/")
def serve_home() -> Response:
    @after_this_request
    def add_headers(response: Response) -> Response:
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Headers"] = "Accept"
        response.headers["Access-Control-Allow-Origin"] = '"*"'
        response.headers["Access-Control-Allow-Methods"] = "GET"
        response.headers["Access-Control-Expose-Headers"] = "Link"
        response.headers["link"] = '</docs/jsonldcontext.jsonld>; rel="alternate"; type="application/ld+json"'
        return response

    path: str = "docs/home.html"
    print(f"Serving file: {path}")
    return app.send_static_file(path)


@app.route("/favicon.ico")
def serve_favicon() -> Response:
    path: str = "docs/favicon.ico"
    print(f"Serving file: {path}")
    return app.send_static_file(path)


@app.route("/robots.txt")
def serve_robots() -> Response:
    path: str = "docs/robots-blockall.txt"
    print(f"Serving file: {path}")
    return app.send_static_file(path)


@app.route("/docs/devnote.css")
def serve_devnote() -> Response:
    path: str = "docs/devnotehide.css" if args_parsed.production else "docs/devnoteshow.css"
    print(f"Serving file: {path}")
    return app.send_static_file(path)


@app.route("/sitemap.xml")
@app.route("/docs/sitemap.xml")
def serve_sitemap() -> Response:
    path: str = "docs/sitemap.xml" if args_parsed.production else "docs/sitemap.xml_no_serve"
    print(f"Serving file: {path}")
    return app.send_static_file(path)


@app.route("/docs/collab/<path:path>")
def serve_colls(path: str) -> Response:
    if not path.endswith(".html"):
        path = f"docs/collab/{path}.html"

    print(f"Serving file: {path}")
    return app.send_static_file(path)


@app.route("/<path:path>")
def serve_terms(path: str) -> Response:
    if not path.endswith(".html"):
        if path[0].islower():
            path = f"terms/properties/{path[0]}/{path}.html"
        elif path[0].isupper() or path[0].isdigit():
            path = f"terms/types/{path[0]}/{path}.html"

    print(f"Serving file: {path}")
    return app.send_static_file(path)


@app.route("/version/<ver>")
@app.route("/version/<ver>/")
@app.route("/version/<ver>/<path:path>")
def serve_downloads(ver: str, path: str = "") -> Response:
    if ver == "latest":
        ver = getVersion()
    if not path:
        path = "schema-all.html"
    
    full_path: str = f"releases/{ver}/{path}"
    print(f"Serving file: {full_path}")
    return app.send_static_file(full_path)


if __name__ == "__main__":
    print(f"Local dev server for Schema.org version: {getVersion()}")
    if args_parsed.production:
        print(Fore.RED + "Running with Production settings" + Style.RESET_ALL)
    else:
        print(Fore.GREEN + "Running with Development settings" + Style.RESET_ALL)

    app.run(host=args_parsed.host, port=args_parsed.port, debug=True)
