#!/usr/bin/python

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
import sys
import unittest

def main(sdk_path, test_path, args):

    # If the sdk path points to a google cloud sdk installation
    # then we should alter it to point to the GAE platform location.
    if os.path.exists(os.path.join(sdk_path, 'platform/google_appengine')):
        sys.path.insert(0, os.path.join(sdk_path, 'platform/google_appengine'))
    else:
        sys.path.insert(0, sdk_path)

    # Ensure that the google.appengine.* packages are available
    # in tests as well as all bundled third-party packages.
    import dev_appserver
    dev_appserver.fix_sys_path()

    # Loading appengine_config from the current project ensures that any
    # changes to configuration there are available to all tests (e.g.
    # sys.path modifications, namespaces, etc.)
    try:
        import appengine_config
        (appengine_config)
    except ImportError:
        print "Note: unable to import appengine_config."

    # Discover and run tests.
    #suite = unittest.loader.TestLoader().discover(test_path)
    #unittest.TextTestRunner(verbosity=2).run(suite)

    if vars(args)["skipbasics"]:
        suite = unittest.loader.TestLoader().discover(test_path, pattern="*graphs*.py")
    else:
        suite = unittest.loader.TestLoader().discover(test_path, pattern="test*.py")

    unittest.TextTestRunner(verbosity=2).run(suite)



if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Configurable testing of schema.org.')
    parser.add_argument('--skipbasics', action='store_true', help='Skip basic tests.')
    args = parser.parse_args()


    # alternative, try
    # PYTHONPATH=/usr/local/google_appengine ./scripts/run_tests.py 

    SDK_PATH = os.path.expanduser("~") + "/google-cloud-sdk"
    print SDK_PATH
    TEST_PATH = "./tests/"

    main(SDK_PATH, TEST_PATH, args)

