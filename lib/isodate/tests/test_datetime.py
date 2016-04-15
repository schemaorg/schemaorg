##############################################################################
# Copyright 2009, Gerhard Weis
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#  * Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#  * Neither the name of the authors nor the names of its contributors
#    may be used to endorse or promote products derived from this software
#    without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT
##############################################################################
'''
Test cases for the isodatetime module.
'''
import unittest
from datetime import datetime

from isodate import parse_datetime, UTC, FixedOffset, datetime_isoformat
from isodate import DATE_BAS_COMPLETE, TIME_BAS_MINUTE, TIME_BAS_COMPLETE
from isodate import DATE_EXT_COMPLETE, TIME_EXT_MINUTE
from isodate import TZ_BAS, TZ_EXT, TZ_HOUR
from isodate import DATE_BAS_ORD_COMPLETE, DATE_EXT_ORD_COMPLETE
from isodate import DATE_BAS_WEEK_COMPLETE, DATE_EXT_WEEK_COMPLETE

# the following list contains tuples of ISO datetime strings and the expected
# result from the parse_datetime method. A result of None means an ISO8601Error
# is expected.
TEST_CASES = [('19850412T1015', datetime(1985, 4, 12, 10, 15),
               DATE_BAS_COMPLETE + 'T' + TIME_BAS_MINUTE),
              ('1985-04-12T10:15', datetime(1985, 4, 12, 10, 15),
               DATE_EXT_COMPLETE + 'T' + TIME_EXT_MINUTE),
              ('1985102T1015Z', datetime(1985, 4, 12, 10, 15, tzinfo=UTC),
               DATE_BAS_ORD_COMPLETE + 'T' + TIME_BAS_MINUTE + TZ_BAS),
              ('1985-102T10:15Z', datetime(1985, 4, 12, 10, 15, tzinfo=UTC),
               DATE_EXT_ORD_COMPLETE + 'T' + TIME_EXT_MINUTE + TZ_EXT),
              ('1985W155T1015+0400', datetime(1985, 4, 12, 10, 15,
                                              tzinfo=FixedOffset(4, 0,
                                                                 '+0400')),
               DATE_BAS_WEEK_COMPLETE + 'T' + TIME_BAS_MINUTE + TZ_BAS),
              ('1985-W15-5T10:15+04', datetime(1985, 4, 12, 10, 15,
                                               tzinfo=FixedOffset(4, 0,
                                                                  '+0400')),
               DATE_EXT_WEEK_COMPLETE + 'T' + TIME_EXT_MINUTE + TZ_HOUR),
              ('20110410T101225.123000Z',
               datetime(2011, 4, 10, 10, 12, 25, 123000, tzinfo=UTC),
               DATE_BAS_COMPLETE + 'T' + TIME_BAS_COMPLETE + ".%f" + TZ_BAS)]


def create_testcase(datetimestring, expectation, format):
    """
    Create a TestCase class for a specific test.

    This allows having a separate TestCase for each test tuple from the
    TEST_CASES list, so that a failed test won't stop other tests.
    """

    class TestDateTime(unittest.TestCase):
        '''
        A test case template to parse an ISO datetime string into a
        datetime object.
        '''

        def test_parse(self):
            '''
            Parse an ISO datetime string and compare it to the expected value.
            '''
            result = parse_datetime(datetimestring)
            self.assertEqual(result, expectation)

        def test_format(self):
            '''
            Take datetime object and create ISO string from it.
            This is the reverse test to test_parse.
            '''
            if expectation is None:
                self.assertRaises(AttributeError,
                                  datetime_isoformat, expectation, format)
            else:
                self.assertEqual(datetime_isoformat(expectation, format),
                                 datetimestring)

    return unittest.TestLoader().loadTestsFromTestCase(TestDateTime)


def test_suite():
    '''
    Construct a TestSuite instance for all test cases.
    '''
    suite = unittest.TestSuite()
    for datetimestring, expectation, format in TEST_CASES:
        suite.addTest(create_testcase(datetimestring, expectation, format))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
