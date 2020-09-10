
Schema.org Software
===================

This document describes the software that underpins Schema.org. Most collaborators will only need to be able to run 
it. At this time we do not solicit active collaboration on the codebase itself from the general public.

* see https://github.com/schemaorg/schemaorg/blob/master/LICENSE for open-source license info (Apache2)

Software 
========

*__Note:__ from Schema version V11.0 onwards the software architecture changed significantly. Please check below for details.*

The site codebase is a simple Python (3.6 or above) application. It is used to create a static image of the Schema.org website to be served locally for testing, or uploading to Google's GCloud for web access.

This repository only contains the vocabulary definition, and examples files, supporting documentation, and Schema.org specific tests and build scripts.

Working with a local version of Schema.org
==========================================

Note: The python application only runs under **_Python 3.6 or above_** which should be preinstalled on the local system.
It depends on a small number of python libraries. To install these run the following command in the root `schemaorg` directory:

    `pip install -r requirements.txt`

Note: The associated configuration scripts are designed to run in a Linux or similar environment, including MAC-OS. 

To work on the vocabulary and run locally firstly clone the repository on a local system:

    `git clone https://github.com/schemaorg/schemaorg.git`
    
**Note:** The default branch name for the schemaorg repository was changed from *master* to *main* (as of 23rd July 2020).  See [MASTER_BRANCH_RENAME.md](MASTER_BRANCH_RENAME.md) for details.

All commands and scripts should be run from in the root `schemaorg` directory.

Once a local version of the repository has been installed initially run the following command:
    `./util/buildsite.py -a`

This will create a local working copy of the schema.org website in the local `site` directory. Dependant on the configuration of your system, this will take between 10-20 minutes. Note, this full build is needed only when significant changes have been made, or prior to shipping a new version.  See below for how to build individual files and pages.

Running Locally
===============

To locally run the application run:

`./devserv.py`  

This will serve the site from the `localhost:8080` address. Use options `--host` and `--port` to change this.

Open a browser, on the same system, to `localhost:8080` to see the locally served site.

Deploying to GCloud
===================

Run the command `./gcloud/deploy2gcloud.sh` to deploy a version of the site to an appengine instance.  You will need to supply a valid appengine project name and a version ID (This does not need to be the same as the Schema Version).  Accept the default `other.yaml` yaml file name.

There are specific deployment scripts for webscemas.org & schema.org.

Internals
=========

Internally, the app uses a simple RDF-like graph data model, and has a parser for 
the Turtle format (`.ttl`) subset that we use to represent schemas. 

See also wiki: https://github.com/schemaorg/schemaorg/wiki/Contributing

The build scripts use a single configuration file `versions.json` to control the version of schema.org release that is built.  To change that version the `schemaversion` value should be set to the new version and a matching entry should be added to the `releaseLog` section.  If a version is not yet ready for release, the convention is to substitute `XX` in the date section.  eg. `"11.2": "2020-XX-XX",`.

If the version number or date has been changed, a full build of the site is required, to reflect that change:
    `./util/buildsite.py -a`

Vocabulary Definition and Examples Files
========================================

Definitions of the vocabulary terms are held in `.ttl` files stored either in the `./data` or `./data/ext/*` directories.  The vocabulary produced is the result of combining the contents of all `.ttl` files found in those directories into a single RDF graph.

Files containing the examples used on the term pages are held in files of the pattern `*examples.txt` stored either in the `./data` or `./data/ext/*` directories. 

Building Individual Files and Term Pages
========================================

During development, it is possible to select individual term pages, dynamic docs pages, or output files (vocabulary definition RDF files, sitemap, jsonldcontext, etc.) for rebuilding.  For details see the output of the command `./util/buildsite.py -h`.  Examples include:
* `./util/buildsite.py -t Book sameAs`  Would rebuild the Book and sameAs term pages.
* `./util/buildsite.py -f Owl` Would rebuild the file `docs/schemaorg.owl` file.
* `./util/buildsite.py -f RDFExport.turtle` Would rebuild the Turtle format vocabulary definition files.
* `./util/buildsite.py -d PendingHome` Would rebuld the home page for the pending section (`docs/pending.home.html`).

Changes to created pages are immediately reflected in the output of the local `./devserv.py` server.

_Note:_ Remember to run the buildsite.py with the `-a` option prior to a deployment or release.
