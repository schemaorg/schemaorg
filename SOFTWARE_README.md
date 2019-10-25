
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

Working with a local version of Schema.org
==========================================

To work on the vocabulary and run locally firstly clone the repository on a local system:

    `git clone --recurse-submodules https://github.com/schemaorg/schemaorg.git`
    
(If you forget the `--recurse-submodules` option, run the command `git submodule update --init --recursive`)

To locally run the application run `./runpythonapp.sh`

To deploy to a Google appengine run `./deploypythonapp.sh`

Note: The pyton application only runs under **_Python 2.7_**

There are preconfigured scripts `./scripts/deployschema.org.sh` & `./scripts/deploywebschemas.org.sh` to deploy to the main schema.org sites (with relevant permissions).

Note: If you are informed of an update to the sdopythonapp submodule, use the command `git submodule update --remote` to synchronise with the local version 


Internals
=========

Internally, the app uses a simple RDF-like graph data model, and has a parser for 
the RDFa Lite subset that we use to represent schemas. 

See also wiki: https://github.com/schemaorg/schemaorg/wiki/Contributing

External Software
=================

Checkout ./sdopythonapp/SOFTWARE_README.md 

