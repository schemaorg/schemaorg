#INTESTHARNESS used to flag we are in a test harness - not called by webApp so some things will work different!
#setInTestHarness(True) should be called from test suites.
#defaults to False (we are not in tests)

#Include "from testharness import *" BEFORE calls to other sdo libraries such as api, sdoapp, etc.
#Then call setInTestHarness() with the appropriate value.

INTESTHARNESS = False

def _setInTestHarness(val):
    global INTESTHARNESS
    INTESTHARNESS = val

def setInTestHarness(val):
    _setInTestHarness(val)

    
def getInTestHarness():
    global INTESTHARNESS
    return INTESTHARNESS
