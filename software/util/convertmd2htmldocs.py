#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import standard python libraries

from pathlib import Path
import random
from typing import Union

import markdown2 as markdown

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


def mddocs(sourceDir: Union[str, Path], destDir: Union[str, Path]) -> None:
    for d in Path(sourceDir).glob("*.md"):
        convert2html(d, destDir)


def convert2html(input_path: Union[str, Path], destdir: Union[str, Path]) -> None:
    in_file = Path(input_path)
    text: str = in_file.read_text()
    random.seed(42)  # To obfuscate the email in a cross-release predictable way.
    md_html: str = markdown.markdown(text)

    output_path = Path(destdir) / f"{in_file.stem}.html"
    output_path.write_text(f"{begin.format(title=in_file.stem.title())}{md_html}{end}")
    in_file.unlink()


if __name__ == "__main__":
    mddocs(".", ".")
