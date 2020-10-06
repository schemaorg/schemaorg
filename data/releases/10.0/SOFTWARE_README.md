
Schema.org Software
===================

This document describes the software that underpins Schema.org. Most collaborators will only need to be able to run 
it. At this time we do not solicit active collaboration on the codebase itself from the general public.

* see https://github.com/schemaorg/schemaorg/blob/master/LICENSE for open-source license info (Apache2)

Software 
========

The site codebase is a simple Python application. It uses Google App Engine, and is designed to allow Schema.org contributors to explore new or improved schemas. The code has a bias towards simplicity and minimal dependencies.

This repository only contains the vocabulary definition, and examples files, supporting documentation, and Schema.org specific tests and build scripts.

The core software is included via a sub module [sdopythonapp](https://github.com/schemaorg/sdopythonapp). 

Working with a local version of Schema.org
==========================================

Note: The python application only runs under **_Python 2.7_** which should be preinstalled on the local system.

Note: The associated configuration scripts are designed to run in a Linux or similar environment, including MAC-OS. 

To work on the vocabulary and run locally firstly clone the repository on a local system:

    `git clone --recurse-submodules https://github.com/schemaorg/schemaorg.git`
    
(If you forget the `--recurse-submodules` option, run the command `git submodule update --init --recursive`)

**Note:** The default branch name for the schemaorg repository was changed from *master* to *main* (as of 23rd July 2020).  See [MASTER_BRANCH_RENAME.md](MASTER_BRANCH_RENAME.md) for details.

To locally run the application run `./runpythonapp.sh`
* In most circumstances using value of '**L**' (for local configuration files) and the default '**N**' (for building site static files) will be sufficient.
* To ensure up to date supplementary files (data dump files, jsonld context, owl file) select '**Y**'.

To deploy to a Google appengine run `./deploypythonapp.sh`
* In most circumstances using value of '**L**' (for local configuration files) and the default '**Y**' (for building site static files) will be sufficient.
* Version for release should be entered as relevant to the vocabulary release version (eg. 3.8, 3.9, 4.0, 5.0, etc)
* **Project:** This is entered as a valid name for a Google cloud project that you have write permission to access.
* **Version:** This is the version of code that is running within the project - this is different from the release version of Schema.org 
* If a version that is already running in the appengine project is selected, you will be asked to confirm its overwrite.
* After upload you can choose to **Exercise site** (to pre-load caches) - this should only be necessary for uploading a new version to a busy site. 

There are preconfigured scripts `./scripts/deployschema.org.sh` & `./scripts/deploywebschemas.org.sh` to deploy to the main schema.org sites (with relevant permissions).

Note: If you are informed of an update to the sdopythonapp submodule, use the command `git submodule update --remote` to synchronise with the local version 

Note: To run subdomain areas of the application on a local development system eg.  `http://bib.localhost:8080/` the subdomains will need to be added to the local system's host file.  eg. `127.0.0.1 localhost bib.localhost pending.localhost` etc.


Internals
=========

Internally, the app uses a simple RDF-like graph data model, and has a parser for 
the RDFa Lite subset that we use to represent schemas. 

See also wiki: https://github.com/schemaorg/schemaorg/wiki/Contributing

Static Build
=========

On sites, such as Schema.org, it has become preferable for robustness and performance reasons to implement a version that requires no runtime processing.   A site that only includes static web pages and files.

To this end from version v8.0 onwards, an additional step has been introduced to create a snapshot of a current version of the site implemented only using static pages.

The intention is that enhancements and developments to the vocabulary and site functionality are produced in the normal way; testing and validating on a locally hosted site using the `./runpythonapp.sh` script or deploying to test appengine instances using the `./deploypythonapp.sh` script.

When a version is ready for deployment to major sites, such as webschemas.org or schema.org, an additional script `./staticbuild/scripts/createstaticsite.sh` should be run.  

This script confirms the status of the current version (running tests, building download files, owl & sitemap files, etc.); creates a static image of the site; creates version specific yaml configuration files; and controls the deployment to the relevant appengine instance.

For more information see the [STATICBUILD_README](./staticbuild/STATICBUILD_README..md) file

