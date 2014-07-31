schemaorg
=========

Schema.org on app engine

This codebase is a simple Python app used to publish the schema.org site.

It uses Google App Engine, and is designed to allow schema.org contributors to explore 
new or improved schemas. The code has a bias towards simplicity and minimal dependencies,
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

Notes
=====

This documentation concerns the software codebase rather than schema.org itself. 

However do note that labels, comments, and documentation should use US English (in the code
and schemas), if a choice between English variants is needed. Please aim for international 
English wherever possible.
