#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import sys
if not (sys.version_info.major == 3 and sys.version_info.minor > 5):
    print("Python version %s.%s not supported version 3.6 or above required - exiting" % (sys.version_info.major,sys.version_info.minor))
    sys.exit(1)

import os
import glob
import markdown2 as markdown

begin = """<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
<title>Schema.org: Documentation: Schema.org Feeds 1.0</title>

<!-- #### Static Doc Insert Head goes here -->
</head><body onload="updatetext()">
 <div id="mainContent" class="faq">
<!-- #### Static Doc Insert PageHead goes here -->"""

end = """<!-- #### Static Doc Insert Footer goes here -->\n </div>\n</html>"""

def mddocs(sourceDir, destDir):
    docs = glob.glob(sourceDir +'/*.md')
    for d in docs:
        convert2html(d,destDir)

def convert2html(doc,destdir):
    file = os.path.basename(doc)
    htf = file.rsplit('.', 1)[0] + '.html'
    with open(doc, 'r') as f:
        text = f.read()
        md_html = markdown.markdown(text)

    with open(destdir+'/'+htf, 'w') as f:
        f.write(begin)
        f.write(md_html)
        f.write(end)

    os.remove(doc)


if __name__ == '__main__':
    mddocs(".",".")

