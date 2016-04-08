
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
