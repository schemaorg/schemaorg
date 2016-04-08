Welcome to Schema.org
=====================


This is the Schema.org project repository. It contains all the schemas, examples and software use to publish schema.org. For the site itself, please see http://schema.org/ instead.

Issues and proposals are managed here by participants of the W3C Schema.org Community Group.
See http://www.w3.org/community/schemaorg for the group. If you are interested to participate please
join the group at W3C, introduce yourself and find or file issues here that engage your interest. If you are new to Git and GitHub, there's a useful [introduction to Github](https://www.w3.org/2006/tools/wiki/Github) in the W3C Wiki.

Issue #1 (https://github.com/schemaorg/schemaorg/issues/1) in Github is an entry point for release planning. It 
should provide an overview of upcoming work, in terms of broad themes, specific issues and release milestones.

Our next milestone release has the working name 'sdo-ganymede'. See
https://github.com/schemaorg/schemaorg/issues/510 for an entry point, or else navigate issues via label or milestone withing Github. Every change to the site comes via discussions here. Substantive changes are recorded in our [release notes](http://schema.org/docs/releases.html). A preview of the [draft new release notes](http://sdo-ganymede.appspot.com/docs/releases.html#sdo-ganymede) can be found as part of the test site for our next release. Every month or so, after final review by the Schema.org Steering Group, we make a formal release. 

Software
========

For most collaborators, all you need to know about the software is how to run it. Essentially you will need to have the Python version of Google App Engine SDK running on the platform of your choice. You can then make test builds of schema.org running on your own machine accessible as http://localhost:8080/ or else post them on appspot.com for collaboration. See https://cloud.google.com/appengine/docs for details. 

More information about the software is also available in [SOFTWARE_README.md](SOFTWARE_README.md)

See also notes in the wiki: https://github.com/schemaorg/schemaorg/wiki/Contributing

Formats and standards
=====================

All schemas and examples are in data/ in utf-8 encoded files.

The main schemas file is data/schema.rdfa (utf-8)

While developing schemas, using data/sdo-somethinghere-schema.rdfa can be useful.

The format is based on W3C RDFS in HTML/RDFa format, see http://schema.org/docs/datamodel.html

The examples are stored in data/examples.txt (utf-8) and other *.txt files.

As with schemas, data/*examples.txt will also be read. It can be useful to develop
using separate files. When vocabulary is finally integrated into the main repository, schema
data will be merged into schema.org. However examples will stay in separate files, as this
works better with git's file comparison machinery.

The data/releases/ hierarchy is reserved for release snapshots (see http://schema.org/version/).

The ext/*/ hierarchy is reserved for extensions (see http://schema.org/docs/extension.html).


Github Branch naming
====================

http://schema.org/docs/releases.html lists releases by working codename and release name.

We began using Ghostbusters character names (http://en.wikipedia.org/wiki/Ghostbusters#Cast)
sdo-stantz, sdo-venkman, sdo-stantz; inspired by http://schema.org/Role discussions.

e.g. successor to http://schema.org/docs/releases.html#v1.91 was code-named sdo-venkman, 
and eventually became http://schema.org/docs/releases.html#v1.92

You can therefore see candidate draft release notes in the Git repository at docs/releases.html

As of May 2015, our next release will be called sdo-ganymede. The default branch in Github
is named after the release. https://en.wikipedia.org/wiki/Ganymede_(moon) ... subsequent names
will be in this general direction.


Notes
=====

This documentation concerns the software codebase rather than schema.org itself. 

However do note that labels, comments, and documentation should use US English (in the code
and schemas), if a choice between English variants is needed. Please aim for international 
English wherever possible.

See also: https://twitter.com/schemaorg_dev
