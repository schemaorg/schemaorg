#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
from pathlib import Path
import sys
from typing import Any, Dict, List, Optional

from colorama import Fore, Style
from flask import Flask, Response, after_this_request

if os.getcwd() not in sys.path:
    sys.path.insert(1, os.getcwd())
import software

from util.schema import getVersion, constants, config


parser: argparse.ArgumentParser = argparse.ArgumentParser()
parser.add_argument("--host", default="localhost", help="Host (default: localhost)")
parser.add_argument("--port", type=int, default=8080, help="Port (default: 8080)")
parser.add_argument("--production", default=False, action="store_true", help="Production settings")
args_parsed: argparse.Namespace = parser.parse_args()

# Resolve absolute paths relative to this script's location
_script_dir = Path(__file__).resolve().parent
_root_dir = _script_dir.parent.parent
_docs: Path = Path(constants.DOCSDOCSDIR.lstrip('/'))

app: Flask = Flask(__name__, static_folder=str(_root_dir / config.OUTPUTDIR), static_url_path="")


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

    path = _docs / "home.html"
    print(f"Serving file: {path}")
    return app.send_static_file(str(path))


@app.route("/favicon.ico")
def serve_favicon() -> Response:
    path = _docs / "favicon.ico"
    print(f"Serving file: {path}")
    return app.send_static_file(str(path))


@app.route("/robots.txt")
def serve_robots() -> Response:
    path = _docs / "robots-blockall.txt"
    print(f"Serving file: {path}")
    return app.send_static_file(str(path))


@app.route("/docs/devnote.css")
def serve_devnote() -> Response:
    filename = "devnotehide.css" if args_parsed.production else "devnoteshow.css"
    path = _docs / filename
    print(f"Serving file: {path}")
    return app.send_static_file(str(path))


@app.route("/sitemap.xml")
@app.route("/docs/sitemap.xml")
def serve_sitemap() -> Response:
    filename = "sitemap.xml" if args_parsed.production else "sitemap.xml_no_serve"
    path = _docs / filename
    print(f"Serving file: {path}")
    return app.send_static_file(str(path))


@app.route("/docs/collab/<path:path>")
def serve_colls(path: str) -> Response:
    if not path.endswith(".html"):
        path_obj = _docs / "collab" / f"{path}.html"
        path = str(path_obj)

    print(f"Serving file: {path}")
    return app.send_static_file(path)


@app.route("/<path>")
def serve_terms(path: str) -> Response:
    if not path.endswith(".html"):
        if path[0].islower():
            path_obj = Path("terms/properties") / path[0] / f"{path}.html"
            path = str(path_obj)
        elif path[0].isupper() or path[0].isdigit():
            path_obj = Path("terms/types") / path[0] / f"{path}.html"
            path = str(path_obj)

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

    full_path = Path("releases") / ver / path
    print(f"Serving file: {full_path}")
    return app.send_static_file(str(full_path))


if __name__ == "__main__":
    print(f"Local dev server for Schema.org version: {getVersion()}")
    print(f"Serving files from {_root_dir}")
    if args_parsed.production:
        print(Fore.RED + "Running with Production settings" + Style.RESET_ALL)
    else:
        print(Fore.GREEN + "Running with Development settings" + Style.RESET_ALL)

    app.run(host=args_parsed.host, port=args_parsed.port, debug=True)
