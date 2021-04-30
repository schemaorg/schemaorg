#!/usr/bin/python3

import sys
sys.path.append("../software/scripts/")

import markdown2 as markdown

# Rough cut, testing on a single page for now
# Can we make our primary sources be markdown?
# How does this relate to the templating?


begin = """<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
<title>Schema.org Markup Validator</title></head><body onload="updatetext()">"""




with open('validator.md', 'r') as f:
    text = f.read()
    md_html = markdown.markdown(text)

with open('validator.html', 'w') as f:

    f.write(begin)
    f.write(md_html)
