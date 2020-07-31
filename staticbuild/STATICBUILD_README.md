Schema.org Software - Static Build
==================================

Background
==========
This document describes the software that underpins the static implemented deployment of Schema.org. 

For details of the basic development and local operation of the Schema.org site, consult the **README.md** and **SOFTWARE_README.md** documents.

Principle of Operation
======================
On sites, such as Schema.org, it has become preferable for robustness and performance reasons to implement a version that requires no runtime processing.   A site that only includes static web pages and files.

To this end from version v8.0 onwards, an additional step has been introduced to create a snapshot of a current version of the site implemented only using static pages.

The intention is that enhancements and developments to the vocabulary and site functionality are produced in the normal way; testing and validating on a locally hosted site using the `./runpythonapp.sh` script or deploying to test appengine instances using the `./deploypythonapp.sh` script.

When a version is ready for deployment to major sites, such as webschemas.org or schema.org, an additional script `./staticbuild/scripts/createstaticsite.sh` should be run.  

A static build should be created for each new/updated version to be deployed to the webschemas.org draft site. or the main Schema.org site.  This step should not be necessary for local development testing or deployment to an example appengine instance.


The 'staticbuild' Area of Repository
====================================

`staticbuild` is an additional area (directory) in the schemaorg repository.

It contains:
 * Build scripts in a `scripts` directory
 * Templates and sources for version specific deployment `.yaml` files
 * Once a version is built:
   * `docs` directory for static and generated document files
   * `terms` directory containing snapshotted images of term pages
   * `releases` directory containing vocabulary download files for current and previous versions
  
Creating a Static Build
=======================
So that scripts have access to the working directories and configuration files for the vocabulary, the build is initiated from the root `schemaorg` directory of the repository by running the following command:

    `./staticbuild/scripts/createstaticsite.sh`

The script goes through the following steps:

 * Requests the version number (7.01, 8.0, 9.0, etc.) for the deployment.
   If this version is not the 'current' configured version the script will abort for this to be corrected.
   
 * Checks for the existence of a relevantly numbered area in the `data/releases` area.
   Will call the appropriate script to build these if necessary or the user acknowledges changes in the configuration since the last build.
   _(This step takes some time)_
   
 * If it detects a previous build of the required version it will ask if this is a build to reflect a *Site Change* or just a *Redeploy*.
   A Site Change initiates a directory clearing and clean creation of a new static image
   A Redeploy skips the clear and creation step
   
 * A site create process (this takes 15-20 minutes to complete):
   * Copies static docs files (html, jpg, css, js, etc.) into the static build docs directory.
   * Calls operational python code to create and store page images for generated docs pages (home, full, development, etc.).
   * Calls operational python code to create and store page images for all vocabulary terms, into the terms directory.
   * Creates from templates version specific .yaml files - these handle redirection of requests to '/version/latest' to the current version release files.
   
 * Deployment and file upload to relevant appengine instances using gcloud.
 
Development Warning
===================

Direct editing of files within a static built image is not advised.

These files are created by processing the code and configuration files in the main processing area, tracked in github.  As such any changes in the `staticbuild` area will be not captured in github and will be overwritten an lost in subsequent builds.



The Createstaticsite.sh Script
==============================
