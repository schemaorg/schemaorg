#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# Import standard python libraries

import sys
import os
import glob
import markdown2 as markdown

# Import schema.org libraries
if not os.getcwd() in sys.path:
    sys.path.insert(1, os.getcwd())

import software


begin = """<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
<title>{title} - Schema.org</title>

<!-- #### Static Doc Insert Head goes here -->
</head><body>
<!-- #### Static Doc Insert PageHead goes here -->
<div id="mainContent" class="faq">"""

end = """</div>\n<!-- #### Static Doc Insert Footer goes here -->\n </html>"""

def mddocs(sourceDir, destDir):
    docs = glob.glob(sourceDir +'/*.md')
    for d in docs:
        convert2html(d,destDir)

def convert2html(input_path, destdir):
    filename = os.path.basename(input_path)
    name, extension = os.path.splitext(filename)
    with open(input_path, 'r') as in_handle:
        text = in_handle.read()
        md_html = markdown.markdown(text)

    output_path = os.path.join(destdir, name + '.html')
    with open(output_path, 'w') as output_handle:
        output_handle.write(begin.format(title=name.title()))
        output_handle.write(md_html)
        output_handle.write(end)

    os.remove(input_path)


if __name__ == '__main__':
    mddocs(".",".")

