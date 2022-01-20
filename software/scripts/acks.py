#!/usr/bin/env python

import sys
import re

# Takes a list of property URLs and generates property-acks.rdfa markup

string = ""
with open(sys.argv[1], 'r') as file:
    for line in file.readlines():
        if re.match("^\s",line):
            pass
        else:
            line = line.rstrip("\n")

            string += """<div typeof="rdf:Property" resource="%s"><link property="dc:source" href="http://www.w3.org/wiki/WebSchemas/SchemaDotOrgSources#source_GoodRelationsTerms"/></div>\n""" % line

#            string = string + '<a href="%s">%s</a>, ' % (line, line)

print("<div>\n%s</div>\n\n" % string)
