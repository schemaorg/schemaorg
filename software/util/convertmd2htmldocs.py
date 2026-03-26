#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import standard python libraries

import sys
import os
import glob
import markdown2 as markdown
import typing
from typing import Any, Dict, List, Optional, Tuple, Union, Iterable, Sequence, Set, Callable

# Import schema.org libraries
if not os.getcwd() in sys.path:
    sys.path.insert(1, os.getcwd())

import software


begin: str = """<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
<title>{title} - Schema.org</title>

<!-- #### Static Doc Insert Head goes here -->
</head><body>
<!-- #### Static Doc Insert PageHead goes here -->
<div id="mainContent" class="faq">"""

end: str = """</div>\n<!-- #### Static Doc Insert Footer goes here -->\n </html>"""


def mddocs(sourceDir: str, destDir: str) -> None:
    docs: List[str] = glob.glob(sourceDir + "/*.md")
    for d in docs:
        convert2html(d, destDir)


def convert2html(input_path: str, destdir: str) -> None:
    filename: str = os.path.basename(input_path)
    name: str
    extension: str
    name, extension = os.path.splitext(filename)
    with open(input_path, "r") as in_handle:
        text: str = in_handle.read()
        md_html: str = markdown.markdown(text)

    output_path: str = os.path.join(destdir, name + ".html")
    with open(output_path, "w") as output_handle:
        output_handle.write(begin.format(title=name.title()))
        output_handle.write(md_html)
        output_handle.write(end)

    os.remove(input_path)


if __name__ == "__main__":
    mddocs(".", ".")
