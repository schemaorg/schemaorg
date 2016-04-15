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
This module provides an ISO 8601:2004 duration parser.

It also provides a wrapper to strftime. This wrapper makes it easier to
format timedelta or Duration instances as ISO conforming strings.
'''
from datetime import timedelta
import re

from isodate.duration import Duration
from isodate.isoerror import ISO8601Error
from isodate.isodatetime import parse_datetime
from isodate.isostrf import strftime, D_DEFAULT

ISO8601_PERIOD_REGEX = re.compile(r"^(?P<sign>[+-])?"
                r"P(?P<years>[0-9]+([,.][0-9]+)?Y)?"
                r"(?P<months>[0-9]+([,.][0-9]+)?M)?"
                r"(?P<weeks>[0-9]+([,.][0-9]+)?W)?"
                r"(?P<days>[0-9]+([,.][0-9]+)?D)?"
                r"((?P<separator>T)(?P<hours>[0-9]+([,.][0-9]+)?H)?"
                r"(?P<minutes>[0-9]+([,.][0-9]+)?M)?"
                r"(?P<seconds>[0-9]+([,.][0-9]+)?S)?)?$")
# regular expression to parse ISO duartion strings.


def parse_duration(datestring):
    """
    Parses an ISO 8601 durations into datetime.timedelta or Duration objects.

    If the ISO date string does not contain years or months, a timedelta
    instance is returned, else a Duration instance is returned.

    The following duration formats are supported:
      -PnnW                  duration in weeks
      -PnnYnnMnnDTnnHnnMnnS  complete duration specification
      -PYYYYMMDDThhmmss      basic alternative complete date format
      -PYYYY-MM-DDThh:mm:ss  extended alternative complete date format
      -PYYYYDDDThhmmss       basic alternative ordinal date format
      -PYYYY-DDDThh:mm:ss    extended alternative ordinal date format

    The '-' is optional.

    Limitations:  ISO standard defines some restrictions about where to use
      fractional numbers and which component and format combinations are
      allowed. This parser implementation ignores all those restrictions and
      returns something when it is able to find all necessary components.
      In detail:
        it does not check, whether only the last component has fractions.
        it allows weeks specified with all other combinations

      The alternative format does not support durations with years, months or
      days set to 0.
    """
    if not isinstance(datestring, basestring):
        raise TypeError("Expecting a string %r" % datestring)
    match = ISO8601_PERIOD_REGEX.match(datestring)
    if not match:
        # try alternative format:
        if datestring.startswith("P"):
            durdt = parse_datetime(datestring[1:])
            if durdt.year != 0 or durdt.month != 0:
                # create Duration
                ret = Duration(days=durdt.day, seconds=durdt.second,
                               microseconds=durdt.microsecond,
                               minutes=durdt.minute, hours=durdt.hour,
                               months=durdt.month, years=durdt.year)
            else:  # FIXME: currently not possible in alternative format
                # create timedelta
                ret = timedelta(days=durdt.day, seconds=durdt.second,
                                microseconds=durdt.microsecond,
                                minutes=durdt.minute, hours=durdt.hour)
            return ret
        raise ISO8601Error("Unable to parse duration string %r" % datestring)
    groups = match.groupdict()
    for key, val in groups.items():
        if key not in ('separator', 'sign'):
            if val is None:
                groups[key] = "0n"
            #print groups[key]
            groups[key] = float(groups[key][:-1].replace(',', '.'))
    if groups["years"] == 0 and groups["months"] == 0:
        ret = timedelta(days=groups["days"], hours=groups["hours"],
                        minutes=groups["minutes"], seconds=groups["seconds"],
                        weeks=groups["weeks"])
        if groups["sign"] == '-':
            ret = timedelta(0) - ret
    else:
        ret = Duration(years=groups["years"], months=groups["months"],
                       days=groups["days"], hours=groups["hours"],
                       minutes=groups["minutes"], seconds=groups["seconds"],
                       weeks=groups["weeks"])
        if groups["sign"] == '-':
            ret = Duration(0) - ret
    return ret


def duration_isoformat(tduration, format=D_DEFAULT):
    '''
    Format duration strings.

    This method is just a wrapper around isodate.isostrf.strftime and uses
    P%P (D_DEFAULT) as default format.
    '''
    # TODO: implement better decision for negative Durations.
    #       should be done in Duration class in consistent way with timedelta.
    if ((isinstance(tduration, Duration) and (tduration.years < 0 or
                                             tduration.months < 0 or
                                             tduration.tdelta < timedelta(0)))
        or (isinstance(tduration, timedelta) and (tduration < timedelta(0)))):
        ret = '-'
    else:
        ret = ''
    ret += strftime(tduration, format)
    return ret
