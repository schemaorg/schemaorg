Schema.org project repository

This repository contains all the schemas, examples and software use to publish schema.org. 

The codebase is a simple Python application. It uses Google App Engine, and is designed to allow schema.org contributors to explore new or improved schemas. The code has a bias towards simplicity and minimal dependencies,
rather than elegance and re-usability. 

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

See also wiki: https://github.com/rvguha/schemaorg/wiki/Contributing

Formats and standards
=====================

All schemas and examples are in data/ in utf-8 encoded files.

The main schemas file is data/schema.rdfa (utf-8)

While developing schemas, using data/sdo-somethinghere-schema.rdfa can be useful.

The format is based on W3C RDFS in HTML/RDFa format, see http://schema.org/docs/datamodel.html

The examples are stored in data/examples.txt (utf-8) 

As with schemas, data/*examples.txt will also be read. It can be useful to develop
using separate files. When vocabulary is finally integrated into the main repository, schema
data will be merged into schema.org. However examples will stay in separate files, as this
works better with git's file comparison machinery.


Github Branch naming
====================

Since discussion of http://schema.org/Role frequently referred to Ghostbusters, 
and we want to name Github branches for upcoming releases without pre-deciding 
their final official schema.org version number, we'll start at 
http://en.wikipedia.org/wiki/Ghostbusters#Cast and take it from there. 

i.e. sdo-venkman, sdo-stantz, sdo-barrett, sdo-spengler, sdo-zeddemore, 
sdo-tully, sdo-melnitz, sdo-peck, sdo-lenny, sdo-gozer.

We'll name these 'sdo-venkman', 'sdo-stantz' etc. as this naming pattern is used for 
our test builds on Appspot.

See http://schema.org/docs/releases.html for published release history.

The successor to http://schema.org/docs/releases.html#v1.91 was code-named sdo-venkman, 
and eventually became http://schema.org/docs/releases.html#v1.92




Notes
=====

This documentation concerns the software codebase rather than schema.org itself. 

However do note that labels, comments, and documentation should use US English (in the code
and schemas), if a choice between English variants is needed. Please aim for international 
English wherever possible.

See also: https://twitter.com/schemaorg_dev
