See [SOFTWARE_README.md](SOFTWARE_README.md) for commandline scripts. This
document covers the larger release process.


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
* Run the `./util/buildsite.py -e` command to assign missing example ids
    (Any updated examples will need committing)

* The `./util/buildsite.py -a` command should be run successfully following changes prior to release. 
   (The -a option runs local tests)

* The ./site/releases/{version} directory has been copied to ./data/releases directory.

* The version [to be released] has been committed and pushed to github and CI tests completed successfully.

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

DEPLOY TO SCHEMA.ORG SITE
=========================
Use command `./gcloud/deploy2schema.org.sh`
