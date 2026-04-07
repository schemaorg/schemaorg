#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Tool that handles includes in static html files."""

import logging
import re
import sys
from pathlib import Path
from typing import Dict, Generator, Tuple, Optional, List, Iterable, Union

if Path.cwd() not in [Path(p).resolve() for p in sys.path]:
    sys.path.insert(1, str(Path.cwd()))

import software.util.schemaversion as schemaversion
import software.util.fileutils as fileutils
import software.util.convertmd2htmldocs as convertmd2htmldocs

log: logging.Logger = logging.getLogger(__name__)


def _getInserts() -> Generator[Tuple[str, str], None, None]:
    template_dir: Path = Path("./templates/static-doc-inserts")
    f_path: Path
    for f_path in template_dir.glob("*.html"):
        fn: str = f_path.stem.lower()
        if fn.startswith("sdi-"):
            fn = fn[4:]
            
        indata: str = f_path.read_text()
        indata = indata.replace("{{version}}", schemaversion.getVersion())
        indata = indata.replace("{{versiondate}}", str(schemaversion.getCurrentVersionDate()))
        indata = indata.replace("{{docsdir}}", "/docs")
        yield (fn, indata)


class Replacer:
    def __init__(self, destdir: Union[str, Path]) -> None:
        self.inserts: Dict[str, str] = dict(_getInserts())
        self.destdir: Path = Path(destdir)

    def insertcopy(self, doc: Union[str, Path], docdata: Optional[str] = None) -> None:
        """Apply all substitutions defined in self.inserts to a file."""
        doc_path: Path = Path(doc)
        data: str = docdata if docdata is not None else doc_path.read_text()

        if re.search(r"<!-- #### Static Doc Insert", data, re.IGNORECASE):
            sub: str
            insert_content: str
            for sub, insert_content in self.inserts.items():
                subpattern: re.Pattern = re.compile(f"<!-- #### Static Doc Insert {sub} .* -->", re.IGNORECASE)
                data = subpattern.sub(insert_content, data)

            targetfile: Path = self.destdir / doc_path.name
            targetfile.write_text(data)


def htmlinserts(destdir: Union[str, Path]) -> None:
    """Perform substitutions on all HTML files in destdir."""
    log.info("Adding header/footer templates to all html files")
    dest_path: Path = Path(destdir)
    docs: List[Path] = sorted(dest_path.glob("*.html"))
    replacer: Replacer = Replacer(destdir=dest_path)
    doc: Path
    for doc in docs:
        replacer.insertcopy(doc)
    log.info(f"Added to {len(docs)} files")


def copyFiles(srcdir: str, destdir: str) -> None:
    """Copy and complete all the static document pages."""
    fileutils.mycopytree(srcdir, destdir)
    log.info("Converting .md docs to html")
    convertmd2htmldocs.mddocs(destdir, destdir)
    htmlinserts(destdir=destdir)
    log.info("Done")


if __name__ == "__main__":
    copyFiles("./docs", "./software/site/docs")
