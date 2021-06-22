#!/usr/bin/python3


import fileinput

for line in fileinput.input():
    line = line.rstrip()
    print("<a href=\"/%s\">%s</a>" % (line, line) )
    pass
