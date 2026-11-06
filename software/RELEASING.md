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

**Note**:  These instructions assume the user has sufficient permissions for both github functions and Google Cloud Appengine deployments.


**Technical pre-conditions for release**

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

... this should have an `YYYY-MM-DD` release date for the current release and all
previous published releases archived under `data/releases/{version}/*`. Ongoing
unreleased changes live under `data/releases/next/` and do not appear in
`versions.json`.


e.g.
    data/releases/30.1/schemaorg-all-https.ttl
    data/releases/30.1/schemaorg-all-https.nq
    data/releases/30.1/schemaorg-all-https.jsonld
    data/releases/30.1/schemaorg-current-https.ttl
    data/releases/30.1/schemaorgcontext.jsonld
    data/releases/30.1/schemaorg.owl
    data/releases/30.1/schemaorg-shapes.shacl

PRE-RELEASE STEPS
=================
Before building a release, confirm your Python environment is using the correct versions of Python libraries using the following command:
`pip install -e software`

In a checked out version of the _main_ branch:

* Record the new numbered release and date in `versions.json`:
  `./software/scripts/schemaversion.py --add X.Y --date YYYY-MM-DD`
* Build and validate the numbered release schema files under `data/releases/X.Y/`:
  `./software/scripts/buildsite.py --release --version X.Y`
  (or `./software/scripts/buildfiles.py --version X.Y` followed by `./software/scripts/runtests.py` and `./software/scripts/validate_examples_shacl.py --version X.Y`).
* Build the static site targeting the new published release when preparing deployment:
  `./software/scripts/buildsite.py -a --version latest`
* Commit `versions.json`, `docs/releases.html`, and `data/releases/X.Y/`, push to GitHub, and verify CI tests pass.

DEPLOY RELEASE
==============

Use command `./software/gcloud/deploy2schema.org.sh`

**Note**: Supplying the `-m` option to the `deploy2schema.org.sh` command will disable the step in the deploy process that migrates web traffic to the newly deployed version.  This step can be undertaken manually later via the google cloud appengine console.

Please use the release version as the Appengine Version ID. Update the `.` to `-` for dot releases.

**Warning**: Because of Google cloud caching processes it may take several minutes before new versions of _all_ released files are supplied in response to a browser request.  As this includes javascript and css files, initial unusual behavior may be experienced.  It is recommended that a full reload of pages, at least 10 minutes after deployment and migration, is performed before analysing a new release.


POST-RELEASE STEPS
==================

* Tag github version vXX.X-release

`git tag [tagname] [commit code]` 

eg. `git tag v14.0-release 9d691a8` Note capitalisation

Then push
`git push origin [tag name]`

After push, release should be auto created and be visible on the repo home page (takes a few minutes)

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

To run tests: `./software/scripts/runtests.py`

 Example transcript:

  $ git clone https://github.com/schemaorg/schemaorg.git
  Cloning into 'schemaorg'...
  ...

  ....
  $ cd schemaorg/
  $ ./software/scripts/runtests.py
  [...]

  Ran 70 tests in 21.168s

  OK (expected failures=3)

1-d) Latest candidate release branch is pushed to the generic unstable upstream site
(i.e. staging.schema.org).

Use command `./software/gcloud/deploy2staging.schema.org.sh`

1-e) The manual QA page /docs/qa.html has been reviewed to ensure
representative pages of each type appear to be in a healthy state.

e.g. see http://staging.schema.org/docs/qa.html

