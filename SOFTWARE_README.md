
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

Note: The associated configuration scripts are designed to run in a Linux or similar environment, including MAC-OS. 

**_Note:_** Build notes from an example (Ubuntu) environment are available here: [AWS_Build_Notes_Ubuntu_AWS.md](AWS_Build_Notes_Ubuntu_AWS)

To work on the vocabulary and run locally firstly clone the repository on a local system:

    git clone https://github.com/schemaorg/schemaorg.git
    

**_Note:_** The python application only runs under **_Python 3.6 or above_** which should be preinstalled on the local system.

It is recommended that a Python virtual environment is created to avoid conflicts with other python activities on your system. For further information on how to create virtual environments see: https://docs.python.org/3.7/library/venv.html


The python environment for schemaorg depends on a small number of python libraries. To install these run the following command in the root `schemaorg` directory:

    pip install -r requirements.txt

All commands and scripts should be run from in the root `schemaorg` directory.

**Module Not Found Errors**  
If when running local scripts you receive an error of this form: 

    ModuleNotFoundError: No module named 'moule_name'  

There are two common causes. Either your Python environment is not correctly set to 3.6 or above, or it does not contain all the required modules which may be because new dependancies have been addded.  To confirm you have the correct modules loaded, run again the cmmand: 

   pip install -r requirements.txt

**Initial Build**  
Once a local version of the repository has been cloned, in to an appropriate python environment, initially run the following command:
    
    ./util/buildsite.py -a

This will create a local working copy of the schema.org website in the local `site` directory. Dependent on the configuration of your system, this will take between 10-20 minutes. Note, this full build is only needed initially, or when significant changes have been made and prior to deploying a new version.  See below for details on how to build individual files and pages.

**buildsite.py**

The `buildsite.py` script creates and manages a local image of the Schema.org website as a set of static html pages and download files in the `site` directory. This it constructs from local working copies of the files in the repository. The contents of the `site` directory are **not** committed and stored in the repository.  The `site` directory image has two main purposes: 1) It provides a local work-in-progress representation of the website for local testing and debug (see below) and; 2) It provides an image of the website that is used for deployment to GCloud for wider access and the production Schema.org site.

Running Locally
===============

To locally serve as a website, run:

`./devserv.py`  

This will serve the site from the `localhost:8080` address. Use options `--host` and `--port` to change this.

Open a browser, on the same system, to `localhost:8080` to see the locally served site.

Deploying to GCloud
===================

Run the command:

    ./gcloud/deploy2gcloud.sh
    
This will deploy the local version of the site to an appengine instance.  You will need to supply a valid appengine project name and a version ID (This does not need to be the same as the Schema Version).  Accept the default `other.yaml` yaml file name.

Note: There are specific deployment scripts for webscemas.org & schema.org.

For more information about GCloud appengine see: https://cloud.google.com/appengine

Internals
=========

Internally, the app uses a simple RDF-like graph data model, and has a parser for 
the Turtle format (`.ttl`) subset that we use to represent schemas. 

See also wiki: https://github.com/schemaorg/schemaorg/wiki/Contributing

The build scripts use a single configuration file `versions.json` to control the version of schema.org release that is built.  To change that version the `schemaversion` value should be set to the new version and a matching entry should be added to the `releaseLog` section.  If a version is not yet ready for release, the convention is to substitute `XX` in the date section.  eg. `"11.2": "2020-XX-XX",`.

If the version number or date has been changed, a full build of the site is required, to reflect that change:
    
    ./util/buildsite.py -a

Vocabulary Definition and Examples Files
========================================

Definitions of the vocabulary terms are held in `.ttl` files stored either in the `./data` or `./data/ext/*` directories.  The vocabulary produced is the result of combining the contents of all `.ttl` files found in those directories into a single RDF graph.

Files containing the examples used on the term pages are held in files of the pattern `*examples.txt` stored either in the `./data` or `./data/ext/*` directories. 

Building Individual Files Documents and Term Pages
==================================================

During development, it is possible to select individual term pages, dynamic docs pages, static docs pages, or output files (vocabulary definition RDF files, sitemap, jsonldcontext, etc.) for rebuilding in the local `site` directory.  
For details see the output of the command `./util/buildsite.py -h`.  Examples include:

* `./util/buildsite.py -t Book sameAs`  Would rebuild the *Book* and *sameAs* term pages.
* `./util/buildsite.py -t All`  Would rebuild all term pages.
* `./util/buildsite.py -f Owl` Would rebuild the file `docs/schemaorg.owl` file.
* `./util/buildsite.py -f RDFExport.turtle` Would rebuild the Turtle format vocabulary definition files.
* `./util/buildsite.py -f All` Would rebuild all output and definition files.
* `./util/buildsite.py -s` Would copy any static docs pages, css files etc. into the `site`.
* `./util/buildsite.py -d PendingHome` Would rebuild the home page for the pending section (`docs/pending.home.html`).
* `./util/buildsite.py -d All` Would rebuild all dynamically created docs files.

Changes to created pages are immediately reflected in the output of the local `./devserv.py` server, without the need for a restart. You may need to do a full refresh of a page to see changes, because of browser caching.

Whenever any changes or additions are made to .ttl files, examples files, documents or other files in the docs directory, these will need to be reflected into the `site` directory using `buildsite.py`. 

In a local development process, defining new types, properties, or changing wording for instance, it would only be necessary to build/rebuild the relevant term pages to see the effects via the website locally served by`./devserv.py`.

_Note:_ **Remember** to run the `buildsite.py` with the `-a` option prior to a deployment or release, to reflect all potential changes (including those pulled from the repository) in the local system into the `site` website image.

Releasing New Production Releases of the Site
=============================================

Once a new candidate release of the site is established and checked/merged into the `main` github branch, there are some steps that need to be taken to prepare that release for deployment, initially to the https://webschemas.org preview site, then to the http://schema.org site.  These steps are detailed in the [RELEASING.TXT](RELEASING.TXT) file.
