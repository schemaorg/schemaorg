#!/usr/bin/python3


# Convert markdown to html
# example usage:
# python3 ./convert.py -i feeds
# Also need to run buildsite.py -a utility to include headers/footers.


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
<title>Schema.org: Documentation: Schema.org Feeds 1.0</title>

<!-- #### Static Doc Insert Head goes here -->
</head><body onload="updatetext()">
 <div id="mainContent" class="faq">
<!-- #### Static Doc Insert PageHead goes here -->"""

end = """<!-- #### Static Doc Insert Footer goes here -->\n </div>\n</html>"""


with open(fn+'.md', 'r') as f:
    text = f.read()
    md_html = markdown.markdown(text)

with open(fn + '.html', 'w') as f:

    f.write(begin)
    f.write(md_html)
    f.write(end)


#<!-- #### Static Doc Insert Head goes here -->
#<!-- #### Static Doc Insert Footer here -->
#|<!-- #### Static Doc Insert PageHead goes here -->

#These use relative paths to the css/javascripts etc.
#The easiest thing to do would be to do versions of these that have full schema.org path
#These files are in templates/static-doc-inserts
