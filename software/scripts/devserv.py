#!/usr/bin/env python3
"""Local Flask development server for a built Schema.org site."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

from colorama import Fore, Style
from flask import Flask, Response, abort, after_this_request, send_from_directory

from schemaorg import constants
from schemaorg.layout import InputLayout, Releases
from util.schema import VERSION, config, constants as schema_constants

_docs: Path = Path(schema_constants.DOCSDOCSDIR.lstrip("/"))

app: Flask = Flask(
    __name__,
    static_folder=str(constants.PROJECT_ROOT / config.OUTPUTDIR),
    static_url_path="",
)


def _send_static(rel_path: Path | str) -> Response:
    print(f"Serving file: {rel_path}")
    return app.send_static_file(str(rel_path))


@app.route("/")
def serve_home() -> Response:
    @after_this_request
    def add_headers(response: Response) -> Response:
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Headers"] = "Accept"
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET"
        response.headers["Access-Control-Expose-Headers"] = "Link"
        response.headers["link"] = (
            '</docs/jsonldcontext.jsonld>; rel="alternate"; type="application/ld+json"'
        )
        return response

    return _send_static(_docs / "home.html")


@app.route("/favicon.ico")
def serve_favicon() -> Response:
    return _send_static(_docs / "favicon.ico")


@app.route("/robots.txt")
def serve_robots() -> Response:
    return _send_static(_docs / "robots-blockall.txt")


@app.route("/docs/devnote.css")
def serve_devnote() -> Response:
    filename = (
        "devnotehide.css"
        if app.config.get("PRODUCTION", False)
        else "devnoteshow.css"
    )
    return _send_static(_docs / filename)


@app.route("/sitemap.xml")
@app.route("/docs/sitemap.xml")
def serve_sitemap() -> Response:
    filename = (
        "sitemap.xml"
        if app.config.get("PRODUCTION", False)
        else "sitemap.xml_no_serve"
    )
    return _send_static(_docs / filename)


@app.route("/docs/collab/<path:path>")
def serve_colls(path: str) -> Response:
    stem = path.removesuffix(".html")
    return _send_static(_docs / "collab" / f"{stem}.html")


@app.route("/<path>")
def serve_terms(path: str) -> Response:
    stem = path.removesuffix(".html")
    if stem and stem[0].islower():
        return _send_static(Path("terms/properties") / stem[0] / f"{stem}.html")
    if stem and (stem[0].isupper() or stem[0].isdigit()):
        return _send_static(Path("terms/types") / stem[0] / f"{stem}.html")
    return _send_static(path)


@app.route("/version/<ver>")
@app.route("/version/<ver>/")
@app.route("/version/<ver>/<path:path>")
def serve_downloads(ver: str, path: str = "") -> Response:
    releases = Releases(InputLayout(constants.PROJECT_ROOT), VERSION)
    try:
        resolved = releases.resolve(ver)
    except ValueError:
        abort(404)
    release_dir = releases.dir(resolved)
    if not path:
        if (release_dir / "schema-all.html").is_file():
            print(f"Serving release file: {release_dir / 'schema-all.html'}")
            return send_from_directory(release_dir, "schema-all.html")
        return _send_static(_docs / "fullrelease.html")

    print(f"Serving release file: {release_dir / path}")
    return send_from_directory(release_dir, path)


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Local dev server for Schema.org.")
    parser.add_argument("--host", default="localhost", help="Host (default: localhost)")
    parser.add_argument("--port", type=int, default=8080, help="Port (default: 8080)")
    parser.add_argument(
        "--production",
        action="store_true",
        help="Production settings",
    )
    args_parsed = parser.parse_args(argv)

    app.config["PRODUCTION"] = args_parsed.production

    print(
        f"Local dev server for Schema.org (default: 'next', latest release: "
        f"{VERSION.current().number()})"
    )
    print(f"Serving files from {app.static_folder}")
    if args_parsed.production:
        print(Fore.RED + "Running with Production settings" + Style.RESET_ALL)
    else:
        print(Fore.GREEN + "Running with Development settings" + Style.RESET_ALL)

    app.run(host=args_parsed.host, port=args_parsed.port, debug=True)


if __name__ == "__main__":
    main()
