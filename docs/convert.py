#!/usr/bin/python3

import sys
import argparse
sys.path.append("../software/scripts/")
import markdown2 as markdown

parser = argparse.ArgumentParser()
parser.add_argument("-i", help="input name, eg. foo for foo.md / foo.html)")
args = parser.parse_args()
print("input: ",args.i)



# Rough cut, testing on a single page for now
# Can we make our primary sources be markdown?
# How does this relate to the templating?

fn = "nope"

if args.i:
    fn = args.i
else:
    print ("No input. Defaulting to 'validator'.");
    fn = "validator"

begin = """<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
<title>Schema.org Markup Validator</title></head><body onload="updatetext()">"""




with open(fn+'.md', 'r') as f:
    text = f.read()
    md_html = markdown.markdown(text)

with open(fn + '.html', 'w') as f:

    f.write(begin)
    f.write(md_html)


#<!-- #### Static Doc Insert Head goes here -->
#<!-- #### Static Doc Insert Footer here -->
#|<!-- #### Static Doc Insert PageHead goes here -->

#These use relative paths to the css/javascripts etc.
#The easiest thing to do would be to do versions of these that have full schema.org path
#These files are in templates/static-doc-inserts
