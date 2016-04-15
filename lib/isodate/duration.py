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
This module defines a Duration class.

The class Duration allows to define durations in years and months and can be
used as limited replacement for timedelta objects.
'''
from datetime import date, datetime, timedelta


def fquotmod(val, low, high):
    '''
    A divmod function with boundaries.
    '''
    div, mod = divmod(val - low, high - low)
    mod += low
    return int(div), mod


def max_days_in_month(year, month):
    '''
    Determines the number of days of a specific month in a specific year.
    '''
    if month in (1, 3, 5, 7, 8, 10, 12):
        return 31
    if month in (4, 6, 9, 11):
        return 30
    if ((year % 400) == 0) or ((year % 100) != 0) and ((year % 4) == 0):
        return 29
    return 28


class Duration(object):
    '''
    A class which represents a duration.

    The difference to datetime.timedelta is, that this class handles also
    differences given in years and months.
    A Duration treats differences given in year, months separately from all
    other components.

    A Duration can be used almost like any timedelta object, however there
    are some restrictions:
      * It is not really possible to compare Durations, because it is unclear,
        whether a duration of 1 year is bigger than 365 days or not.
      * Equality is only tested between the two (year, month vs. timedelta)
        basic components.

    A Duration can also be converted into a datetime object, but this requires
    a start date or an end date.

    The algorithm to add a duration to a date is defined at
    http://www.w3.org/TR/xmlschema-2/#adding-durations-to-dateTimes
    '''

    def __init__(self, days=0, seconds=0, microseconds=0, milliseconds=0,
                 minutes=0, hours=0, weeks=0, months=0, years=0):
        '''
        Initialise this Duration instance with the given parameters.
        '''
        self.months = months
        self.years = years
        self.tdelta = timedelta(days, seconds, microseconds, milliseconds,
                                minutes, hours, weeks)

    def __getattr__(self, name):
        '''
        Provide direct access to attributes of included timedelta instance.
        '''
        return getattr(self.tdelta, name)

    def __str__(self):
        '''
        Return a string representation of this duration similar to timedelta.
        '''
        params = []
        if self.years:
            params.append('%d years' % self.years)
        if self.months:
            params.append('%d months' % self.months)
        params.append(str(self.tdelta))
        return ', '.join(params)

    def __repr__(self):
        '''
        Return a string suitable for repr(x) calls.
        '''
        return "%s.%s(%d, %d, %d, years=%d, months=%d)" % (
                self.__class__.__module__, self.__class__.__name__,
                self.tdelta.days, self.tdelta.seconds,
                self.tdelta.microseconds, self.years, self.months)

    def __neg__(self):
        """
        A simple unary minus.

        Returns a new Duration instance with all it's negated.
        """
        negduration = Duration(years=-self.years, months=-self.months)
        negduration.tdelta = -self.tdelta
        return negduration

    def __add__(self, other):
        '''
        Durations can be added with Duration, timedelta, date and datetime
        objects.
        '''
        if isinstance(other, timedelta):
            newduration = Duration(years=self.years, months=self.months)
            newduration.tdelta = self.tdelta + other
            return newduration
        if isinstance(other, Duration):
            newduration = Duration(years=self.years + other.years,
                                   months=self.months + other.months)
            newduration.tdelta = self.tdelta + other.tdelta
            return newduration
        if isinstance(other, (date, datetime)):
            newmonth = other.month + self.months
            carry, newmonth = fquotmod(newmonth, 1, 13)
            newyear = other.year + self.years + carry
            maxdays = max_days_in_month(newyear, newmonth)
            if other.day > maxdays:
                newday = maxdays
            else:
                newday = other.day
            newdt = other.replace(year=newyear, month=newmonth, day=newday)
            return self.tdelta + newdt
        raise TypeError('unsupported operand type(s) for +: %s and %s' %
                        (self.__class__, other.__class__))

    def __radd__(self, other):
        '''
        Add durations to timedelta, date and datetime objects.
        '''
        if isinstance(other, timedelta):
            newduration = Duration(years=self.years, months=self.months)
            newduration.tdelta = self.tdelta + other
            return newduration
        if isinstance(other, (date, datetime)):
            newmonth = other.month + self.months
            carry, newmonth = fquotmod(newmonth, 1, 13)
            newyear = other.year + self.years + carry
            maxdays = max_days_in_month(newyear, newmonth)
            if other.day > maxdays:
                newday = maxdays
            else:
                newday = other.day
            newdt = other.replace(year=newyear, month=newmonth, day=newday)
            return newdt + self.tdelta
        raise TypeError('unsupported operand type(s) for +: %s and %s' %
                        (other.__class__, self.__class__))

    def __sub__(self, other):
        '''
        It is possible to subtract Duration and timedelta objects from Duration
        objects.
        '''
        if isinstance(other, Duration):
            newduration = Duration(years=self.years - other.years,
                                   months=self.months - other.months)
            newduration.tdelta = self.tdelta - other.tdelta
            return newduration
        if isinstance(other, timedelta):
            newduration = Duration(years=self.years, months=self.months)
            newduration.tdelta = self.tdelta - other
            return newduration
        raise TypeError('unsupported operand type(s) for -: %s and %s' %
                        (self.__class__, other.__class__))

    def __rsub__(self, other):
        '''
        It is possible to subtract Duration objecs from date, datetime and
        timedelta objects.
        '''
        #print '__rsub__:', self, other
        if isinstance(other, (date, datetime)):
            newmonth = other.month - self.months
            carry, newmonth = fquotmod(newmonth, 1, 13)
            newyear = other.year - self.years + carry
            maxdays = max_days_in_month(newyear, newmonth)
            if other.day > maxdays:
                newday = maxdays
            else:
                newday = other.day
            newdt = other.replace(year=newyear, month=newmonth, day=newday)
            return newdt - self.tdelta
        if isinstance(other, timedelta):
            tmpdur = Duration()
            tmpdur.tdelta = other
            return tmpdur - self
        raise TypeError('unsupported operand type(s) for -: %s and %s' %
                        (other.__class__, self.__class__))

    def __eq__(self, other):
        '''
        If the years, month part and the timedelta part are both equal, then
        the two Durations are considered equal.
        '''
        if (isinstance(other, timedelta) and
            self.years == 0 and self.months == 0):
            return self.tdelta == other
        if not isinstance(other, Duration):
            return NotImplemented
        if ((self.years * 12 + self.months) ==
            (other.years * 12 + other.months) and self.tdelta == other.tdelta):
            return True
        return False

    def __ne__(self, other):
        '''
        If the years, month part or the timedelta part is not equal, then
        the two Durations are considered not equal.
        '''
        if isinstance(other, timedelta) and self.years == 0 and self.months == 0:
            return self.tdelta != other
        if not isinstance(other, Duration):
            return NotImplemented
        if ((self.years * 12 + self.months) !=
            (other.years * 12 + other.months) or self.tdelta != other.tdelta):
            return True
        return False

    def todatetime(self, start=None, end=None):
        '''
        Convert this duration into a timedelta object.

        This method requires a start datetime or end datetimem, but raises
        an exception if both are given.
        '''
        if start is None and end is None:
            raise ValueError("start or end required")
        if start is not None and end is not None:
            raise ValueError("only start or end allowed")
        if start is not None:
            return (start + self) - start
        return end - (end - self)
