#!/usr/bin/python

# TODO: 
# * this is fragile, you need path to the right python which has an rdflib
# * consider https://github.com/schemaorg/schemaorg/issues/178 - bundling
# * if you hit problems loading appengine libs, you might be running wrong python interpreter

# based on original in google appengine dist

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

# [START runner]
import argparse
import optparse
import os
import sys
import unittest


USAGE = """%prog SDK_PATH TEST_PATH
Run unit tests for App Engine apps.

SDK_PATH    Path to Google Cloud or Google App Engine SDK installation, usually
            ~/google_cloud_sdk
TEST_PATH   Path to package containing test modules"""


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

    #parser = optparse.OptionParser(USAGE)
    #options, args = parser.parse_args()

    parser = argparse.ArgumentParser(description='Configurable testing of schema.org.')
    parser.add_argument('--skipbasics', action='store_true', help='Skip basic tests.')
    args = parser.parse_args()

    # SDK_PATH = "~/google-cloud-sdk"
    SDK_PATH = os.path.expanduser("~") + "/google-cloud-sdk"
    print SDK_PATH
    TEST_PATH = "./tests/"

    main(SDK_PATH, TEST_PATH, args)

# [END runner]
