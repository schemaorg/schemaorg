#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import sys
if not (sys.version_info.major == 3 and sys.version_info.minor > 5):
    print("Python version %s.%s not supported version 3.6 or above required - exiting" % (sys.version_info.major,sys.version_info.minor))
    sys.exit(1)

# Note: if this stops working in OSX, consider "sudo pip uninstall protobuf"
# to remove a 2nd clashing google/ python lib. See
# https://github.com/coto/gae-boilerplate/issues/306

# This script runs the Schema.org unit tests. The basic tests are concerned
# with our site infrastructure; loading and accessing data.  The graph tests
# are concerned with the shape/size of the schema graph itself.

# Currently this means they require Google AppEngine to be installed,
# because api.py and sdoapp.py both  depend upon AppEngine. This is
# something we should minimise - eventually only
# sdoapp.py should need AppEngine.  We use W3C SPARQL for the graph tests,
# and therefore these tests will only run  if 'rdflib' is installed.
#
# We do not currently test the generated Web site with unit tests. However
# please see /docs/qa.html for some useful links to check whenever site UI
# code is being changed.
#
# There are two dependencies:
#
# 1. AppEngine SDK
# Typically in ~/google_cloud_sdk and/or linked from /usr/local/google_appengine
# This script will do its best to update your python path to point to
# the SDK (whether you point to it directly or the broader Cloud SDK), to
# AppEngine's tools and libs and to other bundled libraries. But to bootstrap
# this is needs to at least find dev_appserver.
#
# 2. rdflib
#
# A normal Python package. Take care that it is installed against the version of
# Python that is being used to run this script. easy_install or pip should work.
# We may later bundle this, see https://github.com/schemaorg/schemaorg/issues/178
#
# script originally based on original in google appengine dist and shared
# under same terms,
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import argparse
import optparse

import os
import subprocess
import unittest
#import os
from os import path, getenv, putenv, getcwd, environ
from os.path import expanduser

SITEDIR="site"
STANDALONE=False


    # Ensure that the google.appengine.* packages are available
    # in tests as well as all bundled third-party packages.
def main(test_path, args=None):

    httpexamplescheck = "grep -l 'http://schema.org' data/*examples.txt data/ext/*/*examples.txt"
    print ("Checking examples files for use of 'http://schema.org'")
    out=""
    try:
        out = subprocess.check_output(httpexamplescheck,shell=True)
    except:
        pass
    if len(out):
        print ("Examples file(s) found containing 'http://schema.org':\n%s" % out)
        print ("Replace with 'https://schema.org and rerun")
        sys.exit(1)
    print ("No use of 'http://schema.org' discovered in examples\n\n")

    if os.path.isfile("%s/docs/jsonldcontext.jsonld" % SITEDIR):
        contextCheck = "cat %s/docs/jsonldcontext.jsonld |cut -d'\"' -f2|sort|uniq -d" % SITEDIR
        print ("Checking jsonldcontext for duplicates")
        dups = subprocess.check_output(contextCheck,shell=True)
        if len(dups):
            print ("Duplicate entries in jsonldcontext: %s" % dups)
            if STANDALONE:
                sys.exit(1)
            return 1
        print ("No duplicates in jsonldcontext\n\n")
    else:
        print("Bypassing jsonldcontext duplicates test\n")
    
    if args and vars(args)["skipbasics"]:
        suite = unittest.loader.TestLoader().discover(test_path, pattern="*graphs*.py")
    else:
        suite = unittest.loader.TestLoader().discover(test_path, pattern="test*.py")

    res = unittest.TextTestRunner(verbosity=2).run(suite)
    
    count = len(res.failures) + len(res.errors)
    if STANDALONE:
        sys.exit(count)
    else:
        return(count)
    
    
if __name__ == '__main__':
    STANDALONE=True
    parser = argparse.ArgumentParser(description='Configurable testing of schema.org.')
    parser.add_argument('--skipbasics', action='store_true', help='Skip basic tests.')
    args = parser.parse_args()
    main('./tests/', args)

# alternative, try
# PYTHONPATH=/usr/local/google_appengine ./scripts/run_tests.py
