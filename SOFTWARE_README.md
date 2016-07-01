
Schema.org Software
===================

This document describes the software that underpins schema.org. Most collaborators will only need to be able to run 
it. At this time we do not solicit active collaboration on the codebase itself from the general public.

* see https://github.com/schemaorg/schemaorg/blob/sdo-phobos/LICENSE for opensource license info (Apache2)

Software 
========

The site codebase is a simple Python application. It uses Google App Engine, and is designed to allow schema.org contributors to explore new or improved schemas. The code has a bias towards simplicity and minimal dependencies,
rather than elegance and re-usability. We expect collaboration will focus more on schemas and examples than 
on our supporting software.

The app reads its schemas and examples from the data/ directory when it starts up. These
are expressed in simple text formats. Proposals to schema.org can be provided as diffs
or github pull requests.

Internals
=========

Internally, the app uses a simple RDF-like graph data model, and has a parser for 
the RDFa Lite subset that we use to represent schemas. Potential contributors are 
cautioned that this code is not designed to become a general purpose framework, and
that we're comfortable with it being hardcoded in various ways around the needs and
approaches of schema.org. If that's not too discouraging, do let us know if you find
interesting uses for it or have ideas for improvements.

See also wiki: https://github.com/schemaorg/schemaorg/wiki/Contributing

External Software
=================

In addition to AppEngine and Python itself, this repository
contains copies of the following opensource libraries in the 
lib/ directory tree.

1.) html5lib/

https://pypi.python.org/pypi/html5lib (MIT License)

2.) isodate/

https://pypi.python.org/pypi/isodate (BSD License)

3.) markdown/

https://pypi.python.org/pypi/Markdown (BSD License)

4.) pyparsing.py

From  lib/pyparsing.py 

    # Copyright (c) 2003-2015  Paul T. McGuire
    #
    # Permission is hereby granted, free of charge, to any person obtaining
    # a copy of this software and associated documentation files (the
    # "Software"), to deal in the Software without restriction, including
    # without limitation the rights to use, copy, modify, merge, publish,
    # distribute, sublicense, and/or sell copies of the Software, and to
    # permit persons to whom the Software is furnished to do so, subject to
    # the following conditions:
    #
    # The above copyright notice and this permission notice shall be
    # included in all copies or substantial portions of the Software.
    #
    # THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
    # EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
    # MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
    # IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
    # CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
    # TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
    # SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

5.) rdflib/ and rdflib_jsonld/

https://github.com/RDFLib 
    https://github.com/RDFLib/rdflib/blob/master/LICENSE

https://github.com/RDFLib/rdflib-jsonld
    https://github.com/RDFLib/rdflib-jsonld/blob/master/LICENSE.md
