Contents
========
- [RELEASING NOTES](#releasing-notes)
- [PRE-RELEASE STEPS](#pre-release-steps)
- [DEPLOY RELEASE](#deploy-release)
- [POST-RELEASE STEPS](#post-release-steps)
- [GENERAL PRE-Release conditions](#general-pre-release-conditions)
- [DEPLOY TO SCHEMA.ORG SITE](#deploy-to-schemaorg-site)


RELEASING NOTES
===============

See [SOFTWARE_README.md](SOFTWARE_README.md) for commandline scripts. This
document covers the larger release process.

<span style="color: red">Note:</span> These instructions assume the user has sufficient permissions for both github functions and Google Cloud Appengine deployments.


0-a) Technical pre-conditions for release.

Overview

Code, schema, examples and supporting documentation should be in a stable state.

Pay particular attention to release-specific structures and docs/releases.html
(e.g. no stray '2.x', '2.*' etc. in hidden markup or tables)

We declare the current version. This should match the number
chosen in /docs/releases.html (check markup assigns an HTML ID too).

The following steps assume a general healthy freeze (tested / QA as below).

in versions.json:

    "schemaversion": "3.9",
    "releaseLog": {
.
.
        "3.9": "2019-08-01",
        "3.8": "2019-07-01",
    }
becomes
    "schemaversion": "4.0",
    "releaseLog": {
.
.
        "4.0": "2019-10-01",
        "3.9": "2019-08-01",
        "3.8": "2019-07-01",
    }

... this should have a release date for the current release and all
previous releases that are archived under data/releases/{version}/*


e.g.
    data/releases/2.1
    data/releases/2.1/all-layers.nq
    data/releases/2.1/core.nq
    data/releases/2.1/ext-auto.nq
    data/releases/2.1/ext-bib.nq
    data/releases/2.1/README.md
    data/releases/2.1/schema-all.html
    data/releases/2.1/schema.nt
    data/releases/2.1/schema.rdfa

PRE-RELEASE STEPS
=================

In a checked out version of the _main_ branch:

* Successfully run the `./util/buildsite.py -release` command.  This will:
  * assign missing example ids
  * complete a full build of the site, proceeded by tests.
  * copy working copies of release files into data/releases directory

* The resultant version [to be released] should be committed and pushed to github and CI tests completed successfully.

DEPLOY RELEASE
==============

Use command `./gcloud/deploy2schema.org.sh`

**Note**: Supplying the `-m` option to the `deploy2schema.org.sh` command will disable the step in the deploy process that migrates web traffic to the newly deployed version.  This step can be undertaken manually later via the google cloud appengine console.

**Warning**: Because of Google cloud caching processes it may take several minutes before new versions of _all_ released files are supplied in response to a browser request.  As this includes javascript and css files, initial unusual behavior may be experienced.  It is recommended that a full reload of pages, at least 10 minutes after deployment and migration, is performed before analysing a new release.


POST-RELEASE STEPS
==================

* Tag gitub version VXX.X-release
* Set up versions.json file for next version - use 2020-XX-XX wildcard date until actual release date confirmed.

GENERAL PRE-Release conditions
==============================

1) General preconditions / process and QA for release.

1-a) Steering Group have signed off on changes and release plan,
and no active and unresolved disputes in the Community Group.

1-b) All code is committed to appropriate release branch at Github (usually
configured as the current default github branch for /schemaorg/ project).

1-c) All tests pass.
It is best to test against a fresh checkout to avoid depending on uncommitted
files. 

To run tests: `./util/runtests.py`

 Example transcript:

  $ git clone https://github.com/schemaorg/schemaorg.git
  Cloning into 'schemaorg'...
  ...

  ....
  $ cd schemaorg/
  $ ./util/runtests.py
  [...]

  Ran 70 tests in 21.168s

  OK (expected failures=3)

1-d) Latest candidate release branch is pushed to the generic unstable upstream site
(i.e. webschemas.org).

Use command `./gcloud/deploy2webschemas.org.sh`

1-e) The manual QA page /docs/qa.html has been reviewed to ensure
representative pages of each type appear to be in a healthy state.

e.g. see http://webschemas.org/docs/qa.html

