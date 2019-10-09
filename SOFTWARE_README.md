
Schema.org Software
===================

This document describes the software that underpins schema.org. Most collaborators will only need to be able to run 
it. At this time we do not solicit active collaboration on the codebase itself from the general public.

* see https://github.com/schemaorg/schemaorg/blob/master/LICENSE for opensource license info (Apache2)

Software 
========

The site codebase is a simple Python application. It uses Google App Engine, and is designed to allow schema.org contributors to explore new or improved schemas. The code has a bias towards simplicity and minimal dependencies.

This repository only contains the vovcabulary definition, and examples files, supporting documetation, and Schema,org specifi tests and build scripts.

The core software is included via a sub module 'sdopythonapp'. 

To locally run the application run `./sdopythonapp/runscripts/runpythonlocal.sh`

To deploy to a Google appengine run `./sdopythonapp/runscripts/runpythondeploy.sh`

There are preconfigured scripts `./scripts/deployschema.org.sh` & `./scripts/deploywebschemas.org.sh` to deploy to the main schema.org sites (with relevant permissions).



Internals
=========

Internally, the app uses a simple RDF-like graph data model, and has a parser for 
the RDFa Lite subset that we use to represent schemas. 

See also wiki: https://github.com/schemaorg/schemaorg/wiki/Contributing

External Software
=================

Checkout ./sdopythonapp/SOFTWARE_README.md 

