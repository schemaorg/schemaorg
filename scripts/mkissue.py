#!/usr/bin/python

#<li id="g1787"><a href="https://github.com/schemaorg/schemaorg/issues/1787">Issue #1787</a>:
import sys
i = int(sys.argv[1])
print i
print ('<li id="g%i"><a href="https://github.com/schemaorg/schemaorg/issues/%i">Issue #%i</a>:' % (i, i, i))
