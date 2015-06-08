#!/usr/bin/env python

import argparse
import optparse
from os import getenv, path
from os.path import expanduser
import sys
import unittest

# Simple stand-alone test runner
# - Runs independently of appengine runner
# - So we need to find the GAE library
# - Looks for tests as ./tests/test*.py
# - Use --skipbasics to skip the most basic tests and run only tests/test_graphs*.py
#
# see https://developers.google.com/appengine/docs/python/tools/localunittesting
#
# Alt: python -m unittest discover -s tests/ -p 'test_*.py' (problem as needs GAE files)

def main(sdk_path, test_path, args):
    sys.path.insert(0, sdk_path) # add AppEngine SDK to path
    import dev_appserver
    dev_appserver.fix_sys_path()
    print args, test_path
    if vars(args)["skipbasics"]:
        suite = unittest.loader.TestLoader().discover(test_path, pattern="test_graphs*.py")
    else:
        suite = unittest.loader.TestLoader().discover(test_path)
    unittest.TextTestRunner(verbosity=2).run(suite)


if __name__ == '__main__':
    sdk_path = getenv('APP_ENGINE',
                      expanduser("~") + '/google-cloud-sdk/platform/google_appengine/')
    parser = argparse.ArgumentParser(description='Configurable testing of schema.org.')
    parser.add_argument('--skipbasics', action='store_true', help='Skip basic tests.')
    args = parser.parse_args()
    main(sdk_path, './tests/', args)
