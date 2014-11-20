#!/usr/bin/env python

import optparse
import sys
from os import path
from os.path import expanduser
import unittest

# Simple stand-alone test runner
# - Runs independently of appengine runner
# - So we need to find the GAE library
# - Looks for tests as ./tests/test*.py
# see https://developers.google.com/appengine/docs/python/tools/localunittesting
#
# Or: python -m unittest discover -s tests/ -p 'test_*.py' (plus add the path...)

def main(sdk_path, test_path):
    sys.path.insert(0, sdk_path)
    import dev_appserver
    dev_appserver.fix_sys_path()
    suite = unittest.loader.TestLoader().discover(test_path)
    unittest.TextTestRunner(verbosity=2).run(suite)


if __name__ == '__main__':

    main(expanduser("~") + '/google-cloud-sdk/platform/google_appengine/', './tests/')
