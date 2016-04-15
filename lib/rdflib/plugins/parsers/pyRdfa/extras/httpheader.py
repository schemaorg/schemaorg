#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
""" Utility functions to work with HTTP headers.

 This module provides some utility functions useful for parsing
 and dealing with some of the HTTP 1.1 protocol headers which
 are not adequately covered by the standard Python libraries.

 Requires Python 2.2 or later.

 The functionality includes the correct interpretation of the various
 Accept-* style headers, content negotiation, byte range requests,
 HTTP-style date/times, and more.

 There are a few classes defined by this module:

   * class content_type   -- media types such as 'text/plain'
   * class language_tag   -- language tags such as 'en-US'
   * class range_set      -- a collection of (byte) range specifiers
   * class range_spec     -- a single (byte) range specifier

 The primary functions in this module may be categorized as follows:

   * Content negotiation functions...
     * acceptable_content_type()
     * acceptable_language()
     * acceptable_charset()
     * acceptable_encoding()

   * Mid-level header parsing functions...
     * parse_accept_header()
     * parse_accept_language_header()
     * parse_range_header()
 
   * Date and time...
     * http_datetime()
     * parse_http_datetime()

   * Utility functions...
     * quote_string()
     * remove_comments()
     * canonical_charset()

   * Low level string parsing functions...
     * parse_comma_list()
     * parse_comment()
     * parse_qvalue_accept_list()
     * parse_media_type()
     * parse_number()
     * parse_parameter_list()
     * parse_quoted_string()
     * parse_range_set()
     * parse_range_spec()
     * parse_token()
     * parse_token_or_quoted_string()

 And there are some specialized exception classes:

   * RangeUnsatisfiableError
   * RangeUnmergableError
   * ParseError

 See also:

   * RFC 2616, "Hypertext Transfer Protocol -- HTTP/1.1", June 1999.
             <http://www.ietf.org/rfc/rfc2616.txt>
             Errata at <http://purl.org/NET/http-errata>
   * RFC 2046, "(MIME) Part Two: Media Types", November 1996.
             <http://www.ietf.org/rfc/rfc2046.txt>
   * RFC 3066, "Tags for the Identification of Languages", January 2001.
             <http://www.ietf.org/rfc/rfc3066.txt>
             
             
  Note: I have made a small modification on the regexp for internet date, 
  to make it more liberal (ie, accept a time zone string of the form +0000)
  Ivan Herman <http://www.ivan-herman.net>, March 2011.
  
  Have added statements to make it (hopefully) Python 3 compatible.
  Ivan Herman <http://www.ivan-herman.net>, August 2012.
"""

__author__ = "Deron Meranda <http://deron.meranda.us/>"
__date__ = "2012-08-31"
__version__ = "1.02"
__credits__ = """Copyright (c) 2005 Deron E. Meranda <http://deron.meranda.us/>
Licensed under GNU LGPL 2.1 or later.  See <http://www.fsf.org/>.

This library is free software; you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public
License as published by the Free Software Foundation; either
version 2.1 of the License, or (at your option) any later version.

This library is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public
License along with this library; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
"""

# Character classes from RFC 2616 section 2.2
SEPARATORS = '()<>@,;:\\"/[]?={} \t'
LWS = ' \t\n\r'  # linear white space
CRLF = '\r\n'
DIGIT = '0123456789'
HEX = '0123456789ABCDEFabcdef'

import sys
PY3 = (sys.version_info[0] >= 3)

# Try to get a set/frozenset implementation if possible
try:
    type(frozenset)
except NameError:
    try:
        # The demset.py module is available at http://deron.meranda.us/
        from demset import set, frozenset
        __emulating_set = True  # So we can clean up global namespace later
    except ImportError:
        pass

try:
    # Turn character classes into set types (for Python 2.4 or greater)
    SEPARATORS = frozenset([c for c in SEPARATORS])
    LWS = frozenset([c for c in LWS])
    CRLF = frozenset([c for c in CRLF])
    DIGIT = frozenset([c for c in DIGIT])
    HEX = frozenset([c for c in HEX])
    del c
except NameError:
    # Python 2.3 or earlier, leave as simple strings
    pass


def _is_string( obj ):
    """Returns True if the object is a string or unicode type."""
    if PY3 :
        return isinstance(obj,str)
    else :
        return isinstance(obj,str) or isinstance(obj,unicode)


def http_datetime( dt=None ):
    """Formats a datetime as an HTTP 1.1 Date/Time string.

    Takes a standard Python datetime object and returns a string
    formatted according to the HTTP 1.1 date/time format.

    If no datetime is provided (or None) then the current
    time is used.
    
    ABOUT TIMEZONES: If the passed in datetime object is naive it is
    assumed to be in UTC already.  But if it has a tzinfo component,
    the returned timestamp string will have been converted to UTC
    automatically.  So if you use timezone-aware datetimes, you need
    not worry about conversion to UTC.

    """
    if not dt:
        import datetime
        dt = datetime.datetime.utcnow()
    else:
        try:
            dt = dt - dt.utcoffset()
        except:
            pass  # no timezone offset, just assume already in UTC

    s = dt.strftime('%a, %d %b %Y %H:%M:%S GMT')
    return s


def parse_http_datetime( datestring, utc_tzinfo=None, strict=False ):
    """Returns a datetime object from an HTTP 1.1 Date/Time string.

    Note that HTTP dates are always in UTC, so the returned datetime
    object will also be in UTC.

    You can optionally pass in a tzinfo object which should represent
    the UTC timezone, and the returned datetime will then be
    timezone-aware (allowing you to more easly translate it into
    different timzeones later).

    If you set 'strict' to True, then only the RFC 1123 format
    is recognized.  Otherwise the backwards-compatible RFC 1036
    and Unix asctime(3) formats are also recognized.
    
    Please note that the day-of-the-week is not validated.
    Also two-digit years, although not HTTP 1.1 compliant, are
    treated according to recommended Y2K rules.

    """
    import re, datetime
    m = re.match(r'(?P<DOW>[a-z]+), (?P<D>\d+) (?P<MON>[a-z]+) (?P<Y>\d+) (?P<H>\d+):(?P<M>\d+):(?P<S>\d+(\.\d+)?) (?P<TZ>[a-zA-Z0-9_+]+)$',
                 datestring, re.IGNORECASE)
    if not m and not strict:
        m = re.match(r'(?P<DOW>[a-z]+) (?P<MON>[a-z]+) (?P<D>\d+) (?P<H>\d+):(?P<M>\d+):(?P<S>\d+) (?P<Y>\d+)$',
                     datestring, re.IGNORECASE)
        if not m:
            m = re.match(r'(?P<DOW>[a-z]+), (?P<D>\d+)-(?P<MON>[a-z]+)-(?P<Y>\d+) (?P<H>\d+):(?P<M>\d+):(?P<S>\d+(\.\d+)?) (?P<TZ>\w+)$',
                         datestring, re.IGNORECASE)
    if not m:
        raise ValueError('HTTP date is not correctly formatted')

    try:
        tz = m.group('TZ').upper()
    except:
        tz = 'GMT'
    if tz not in ('GMT','UTC','0000','00:00'):
        raise ValueError('HTTP date is not in GMT timezone')

    monname = m.group('MON').upper()
    mdict = {'JAN':1, 'FEB':2, 'MAR':3, 'APR':4, 'MAY':5, 'JUN':6,
             'JUL':7, 'AUG':8, 'SEP':9, 'OCT':10, 'NOV':11, 'DEC':12}
    month = mdict.get(monname)
    if not month:
        raise ValueError('HTTP date has an unrecognizable month')
    y = int(m.group('Y'))
    if y < 100:
        century = datetime.datetime.utcnow().year / 100
        if y < 50:
            y = century * 100 + y
        else:
            y = (century - 1) * 100 + y
    d = int(m.group('D'))
    hour = int(m.group('H'))
    minute = int(m.group('M'))
    try:
        second = int(m.group('S'))
    except:
        second = float(m.group('S'))
    dt = datetime.datetime( y, month, d, hour, minute, second, tzinfo=utc_tzinfo )
    return dt


class RangeUnsatisfiableError(ValueError):
    """Exception class when a byte range lies outside the file size boundaries."""
    def __init__(self, reason=None):
        if not reason:
            reason = 'Range is unsatisfiable'
        ValueError.__init__(self, reason)


class RangeUnmergableError(ValueError):
    """Exception class when byte ranges are noncontiguous and can not be merged together."""
    def __init__(self, reason=None):
        if not reason:
            reason = 'Ranges can not be merged together'
        ValueError.__init__(self, reason)


class ParseError(ValueError):
    """Exception class representing a string parsing error."""
    def __init__(self, args, input_string, at_position):
        ValueError.__init__(self, args)
        self.input_string = input_string
        self.at_position = at_position
    def __str__(self):
        if self.at_position >= len(self.input_string):
            return '%s\n\tOccured at end of string' % self.args[0]
        else:
            return '%s\n\tOccured near %s' % (self.args[0], repr(self.input_string[self.at_position:self.at_position+16]))


def is_token(s):
    """Determines if the string is a valid token."""
    for c in s:
        if ord(c) < 32 or ord(c) > 128 or c in SEPARATORS:
            return False
    return True


def parse_comma_list(s, start=0, element_parser=None, min_count=0, max_count=0):
    """Parses a comma-separated list with optional whitespace.

    Takes an optional callback function `element_parser`, which
    is assumed to be able to parse an individual element.  It
    will be passed the string and a `start` argument, and
    is expected to return a tuple (parsed_result, chars_consumed).

    If no element_parser is given, then either single tokens or
    quoted strings will be parsed.

    If min_count > 0, then at least that many non-empty elements
    must be in the list, or an error is raised.

    If max_count > 0, then no more than that many non-empty elements
    may be in the list, or an error is raised.

    """
    if min_count > 0 and start == len(s):
        raise ParseError('Comma-separated list must contain some elements',s,start)
    elif start >= len(s):
        raise ParseError('Starting position is beyond the end of the string',s,start)

    if not element_parser:
        element_parser = parse_token_or_quoted_string
    results = []
    pos = start
    while pos < len(s):
        e = element_parser( s, pos )
        if not e or e[1] == 0:
            break # end of data?
        else:
            results.append( e[0] )
            pos += e[1]
        while pos < len(s) and s[pos] in LWS:
            pos += 1
        if pos < len(s) and s[pos] != ',':
            break
        while pos < len(s) and s[pos] == ',':
            # skip comma and any "empty" elements
            pos += 1  # skip comma
            while pos < len(s) and s[pos] in LWS:
                pos += 1
    if len(results) < min_count:
        raise ParseError('Comma-separated list does not have enough elements',s,pos)
    elif max_count and len(results) > max_count:
        raise ParseError('Comma-separated list has too many elements',s,pos)
    return (results, pos-start)


def parse_token(s, start=0):
    """Parses a token.

    A token is a string defined by RFC 2616 section 2.2 as:
       token = 1*<any CHAR except CTLs or separators>

    Returns a tuple (token, chars_consumed), or ('',0) if no token
    starts at the given string position.  On a syntax error, a
    ParseError exception will be raised.

    """
    return parse_token_or_quoted_string(s, start, allow_quoted=False, allow_token=True)


def quote_string(s, always_quote=True):
    """Produces a quoted string according to HTTP 1.1 rules.

    If always_quote is False and if the string is also a valid token,
    then this function may return a string without quotes.

    """
    need_quotes = False
    q = ''
    for c in s:
        if ord(c) < 32 or ord(c) > 127 or c in SEPARATORS:
            q += '\\' + c
            need_quotes = True
        else:
            q += c
    if need_quotes or always_quote:
        return '"' + q + '"'
    else:
        return q


def parse_quoted_string(s, start=0):
    """Parses a quoted string.

    Returns a tuple (string, chars_consumed).  The quote marks will
    have been removed and all \-escapes will have been replaced with
    the characters they represent.

    """
    return parse_token_or_quoted_string(s, start, allow_quoted=True, allow_token=False)


def parse_token_or_quoted_string(s, start=0, allow_quoted=True, allow_token=True):
    """Parses a token or a quoted-string.

    's' is the string to parse, while start is the position within the
    string where parsing should begin.  It will returns a tuple
    (token, chars_consumed), with all \-escapes and quotation already
    processed.

    Syntax is according to BNF rules in RFC 2161 section 2.2,
    specifically the 'token' and 'quoted-string' declarations.
    Syntax errors in the input string will result in ParseError
    being raised.

    If allow_quoted is False, then only tokens will be parsed instead
    of either a token or quoted-string.

    If allow_token is False, then only quoted-strings will be parsed
    instead of either a token or quoted-string.
    """
    if not allow_quoted and not allow_token:
        raise ValueError('Parsing can not continue with options provided')

    if start >= len(s):
        raise ParseError('Starting position is beyond the end of the string',s,start)
    has_quote = (s[start] == '"')
    if has_quote and not allow_quoted:
        raise ParseError('A quoted string was not expected', s, start)
    if not has_quote and not allow_token:
        raise ParseError('Expected a quotation mark', s, start)

    s2 = ''
    pos = start
    if has_quote:
        pos += 1
    while pos < len(s):
        c = s[pos]
        if c == '\\' and has_quote:
            # Note this is NOT C-style escaping; the character after the \ is
            # taken literally.
            pos += 1
            if pos == len(s):
                raise ParseError("End of string while expecting a character after '\\'",s,pos)
            s2 += s[pos]
            pos += 1
        elif c == '"' and has_quote:
            break
        elif not has_quote and (c in SEPARATORS or ord(c)<32 or ord(c)>127):
            break
        else:
            s2 += c
            pos += 1
    if has_quote:
        # Make sure we have a closing quote mark
        if pos >= len(s) or s[pos] != '"':
            raise ParseError('Quoted string is missing closing quote mark',s,pos)
        else:
            pos += 1
    return s2, (pos - start)


def remove_comments(s, collapse_spaces=True):
    """Removes any ()-style comments from a string.

    In HTTP, ()-comments can nest, and this function will correctly
    deal with that.

    If 'collapse_spaces' is True, then if there is any whitespace
    surrounding the comment, it will be replaced with a single space
    character.  Whitespace also collapses across multiple comment
    sequences, so that "a (b) (c) d" becomes just "a d".

    Otherwise, if 'collapse_spaces' is False then all whitespace which
    is outside any comments is left intact as-is.

    """
    if '(' not in s:
        return s  # simple case
    A = []
    dostrip = False
    added_comment_space = False
    pos = 0
    if collapse_spaces:
        # eat any leading spaces before a comment
        i = s.find('(')
        if i >= 0:
            while pos < i and s[pos] in LWS:
                pos += 1
            if pos != i:
                pos = 0
            else:
                dostrip = True
                added_comment_space = True  # lie
    while pos < len(s):
        if s[pos] == '(':
            cmt, k = parse_comment( s, pos )
            pos += k
            if collapse_spaces:
                dostrip = True
                if not added_comment_space:
                    if len(A) > 0 and A[-1] and A[-1][-1] in LWS:
                        # previous part ended with whitespace
                        A[-1] = A[-1].rstrip()
                        A.append(' ')  # comment becomes one space
                        added_comment_space = True
        else:
            i = s.find( '(', pos )
            if i == -1:
                if dostrip:
                    text = s[pos:].lstrip()
                    if s[pos] in LWS and not added_comment_space:
                        A.append(' ')
                        added_comment_space = True
                else:
                    text = s[pos:]
                if text:
                    A.append(text)
                    dostrip = False
                    added_comment_space = False
                break # end of string
            else:
                if dostrip:
                    text = s[pos:i].lstrip()
                    if s[pos] in LWS and not added_comment_space:
                        A.append(' ')
                        added_comment_space = True
                else:
                    text = s[pos:i]
                if text:
                    A.append(text)
                    dostrip = False
                    added_comment_space = False
                pos = i
    if dostrip and len(A) > 0 and A[-1] and A[-1][-1] in LWS:
        A[-1] = A[-1].rstrip()
    return ''.join(A)


def _test_comments():
    """A self-test on comment processing.  Returns number of test failures."""
    def _testrm( a, b, collapse ):
        b2 = remove_comments( a, collapse )
        if b != b2:
            print( 'Comment test failed:' )
            print( '   remove_comments( %s, collapse_spaces=%s ) -> %s' % (repr(a), repr(collapse), repr(b2)) )
            print( '   expected %s' % repr(b) )
            return 1
        return 0
    failures = 0
    failures += _testrm( r'', '', False )
    failures += _testrm( r'(hello)', '', False)
    failures += _testrm( r'abc (hello) def', 'abc  def', False)
    failures += _testrm( r'abc (he(xyz)llo) def', 'abc  def', False)
    failures += _testrm( r'abc (he\(xyz)llo) def', 'abc llo) def', False)
    failures += _testrm( r'abc(hello)def', 'abcdef', True)
    failures += _testrm( r'abc (hello) def', 'abc def', True)
    failures += _testrm( r'abc   (hello)def', 'abc def', True)
    failures += _testrm( r'abc(hello)  def', 'abc def', True)
    failures += _testrm( r'abc(hello) (world)def', 'abc def', True)
    failures += _testrm( r'abc(hello)(world)def', 'abcdef', True)
    failures += _testrm( r'  (hello) (world) def', 'def', True)
    failures += _testrm( r'abc  (hello) (world) ', 'abc', True)
    return failures

def parse_comment(s, start=0):
    """Parses a ()-style comment from a header value.

    Returns tuple (comment, chars_consumed), where the comment will
    have had the outer-most parentheses and white space stripped.  Any
    nested comments will still have their parentheses and whitespace
    left intact.

    All \-escaped quoted pairs will have been replaced with the actual
    characters they represent, even within the inner nested comments.

    You should note that only a few HTTP headers, such as User-Agent
    or Via, allow ()-style comments within the header value.

    A comment is defined by RFC 2616 section 2.2 as:
    
       comment = "(" *( ctext | quoted-pair | comment ) ")"
       ctext   = <any TEXT excluding "(" and ")">
    """
    if start >= len(s):
        raise ParseError('Starting position is beyond the end of the string',s,start)
    if s[start] != '(':
        raise ParseError('Comment must begin with opening parenthesis',s,start)

    s2 = ''
    nestlevel = 1
    pos = start + 1
    while pos < len(s) and s[pos] in LWS:
        pos += 1

    while pos < len(s):
        c = s[pos]
        if c == '\\':
            # Note this is not C-style escaping; the character after the \ is
            # taken literally.
            pos += 1
            if pos == len(s):
                raise ParseError("End of string while expecting a character after '\\'",s,pos)
            s2 += s[pos]
            pos += 1
        elif c == '(':
            nestlevel += 1
            s2 += c
            pos += 1
        elif c == ')':
            nestlevel -= 1
            pos += 1
            if nestlevel >= 1:
                s2 += c
            else:
                break
        else:
            s2 += c
            pos += 1
    if nestlevel > 0:
        raise ParseError('End of string reached before comment was closed',s,pos)
    # Now rstrip s2 of all LWS chars.
    while len(s2) and s2[-1] in LWS:
        s2 = s2[:-1]
    return s2, (pos - start)
    

class range_spec(object):
    """A single contiguous (byte) range.

    A range_spec defines a range (of bytes) by specifying two offsets,
    the 'first' and 'last', which are inclusive in the range.  Offsets
    are zero-based (the first byte is offset 0).  The range can not be
    empty or negative (has to satisfy first <= last).

    The range can be unbounded on either end, represented here by the
    None value, with these semantics:

       * A 'last' of None always indicates the last possible byte
        (although that offset may not be known).

       * A 'first' of None indicates this is a suffix range, where
         the last value is actually interpreted to be the number
         of bytes at the end of the file (regardless of file size).

    Note that it is not valid for both first and last to be None.

    """

    __slots__ = ['first','last']

    def __init__(self, first=0, last=None):
        self.set( first, last )

    def set(self, first, last):
        """Sets the value of this range given the first and last offsets.
        """
        if first is not None and last is not None and first > last:
            raise ValueError("Byte range does not satisfy first <= last.")
        elif first is None and last is None:
            raise ValueError("Byte range can not omit both first and last offsets.")
        self.first = first
        self.last = last

    def __repr__(self):
        return '%s.%s(%s,%s)' % (self.__class__.__module__, self.__class__.__name__,
                                 self.first, self.last)

    def __str__(self):
        """Returns a string form of the range as would appear in a Range: header."""
        if self.first is None and self.last is None:
            return ''
        s = ''
        if self.first is not None:
            s += '%d' % self.first
        s += '-'
        if self.last is not None:
            s += '%d' % self.last
        return s

    def __eq__(self, other):
        """Compare ranges for equality.

        Note that if non-specific ranges are involved (such as 34- and -5),
        they could compare as not equal even though they may represent
        the same set of bytes in some contexts.
        """
        return self.first == other.first and self.last == other.last

    def __ne__(self, other):
        """Compare ranges for inequality.

        Note that if non-specific ranges are involved (such as 34- and -5),
        they could compare as not equal even though they may represent
        the same set of bytes in some contexts.
        """
        return not self.__eq__(other)

    def __lt__(self, other):
        """< operator is not defined"""
        raise NotImplementedError('Ranges can not be relationally compared')
    def __le__(self, other):
        """<= operator is not defined"""
        raise NotImplementedError('Ranges can not be ralationally compared')
    def __gt__(self, other):
        """> operator is not defined"""
        raise NotImplementedError('Ranges can not be relationally compared')
    def __ge__(self, other):
        """>= operator is not defined"""
        raise NotImplementedError('Ranges can not be relationally compared')
    
    def copy(self):
        """Makes a copy of this range object."""
        return self.__class__( self.first, self.last )

    def is_suffix(self):
        """Returns True if this is a suffix range.

        A suffix range is one that specifies the last N bytes of a
        file regardless of file size.

        """
        return self.first == None

    def is_fixed(self):
        """Returns True if this range is absolute and a fixed size.

        This occurs only if neither first or last is None.  Converse
        is the is_unbounded() method.

        """
        return first is not None and last is not None

    def is_unbounded(self):
        """Returns True if the number of bytes in the range is unspecified.

        This can only occur if either the 'first' or the 'last' member
        is None.  Converse is the is_fixed() method.

        """
        return self.first is None or self.last is None

    def is_whole_file(self):
        """Returns True if this range includes all possible bytes.

        This can only occur if the 'last' member is None and the first
        member is 0.

        """
        return self.first == 0 and self.last is None

    def __contains__(self, offset):
        """Does this byte range contain the given byte offset?

        If the offset < 0, then it is taken as an offset from the end
        of the file, where -1 is the last byte.  This type of offset
        will only work with suffix ranges.

        """
        if offset < 0:
            if self.first is not None:
                return False
            else:
                return self.last >= -offset
        elif self.first is None:
            return False
        elif self.last is None:
            return True
        else:
            return self.first <= offset <= self.last

    def fix_to_size(self, size):
        """Changes a length-relative range to an absolute range based upon given file size.

        Ranges that are already absolute are left as is.

        Note that zero-length files are handled as special cases,
        since the only way possible to specify a zero-length range is
        with the suffix range "-0".  Thus unless this range is a suffix
        range, it can not satisfy a zero-length file.

        If the resulting range (partly) lies outside the file size then an
        error is raised.
        """

        if size == 0:
            if self.first is None:
                self.last = 0
                return
            else:
                raise RangeUnsatisfiableError("Range can satisfy a zero-length file.")

        if self.first is None:
            # A suffix range
            self.first = size - self.last
            if self.first < 0:
                self.first = 0
            self.last = size - 1
        else:
            if self.first > size - 1:
                raise RangeUnsatisfiableError('Range begins beyond the file size.')
            else:
                if self.last is None:
                    # An unbounded range
                    self.last = size - 1
        return

    def merge_with(self, other):
        """Tries to merge the given range into this one.

        The size of this range may be enlarged as a result.

        An error is raised if the two ranges do not overlap or are not
        contiguous with each other.
        """
        if self.is_whole_file() or self == other:
            return
        elif other.is_whole_file():
            self.first, self.last = 0, None
            return

        a1, z1 = self.first, self.last
        a2, z2 = other.first, other.last

        if self.is_suffix():
            if z1 == 0: # self is zero-length, so merge becomes a copy
                self.first, self.last = a2, z2
                return
            elif other.is_suffix():
                self.last = max(z1, z2)
            else:
                raise RangeUnmergableError()
        elif other.is_suffix():
            if z2 == 0: # other is zero-length, so nothing to merge
                return
            else:
                raise RangeUnmergableError()

        assert a1 is not None and a2 is not None

        if a2 < a1:
            # swap ranges so a1 <= a2
            a1, z1, a2, z2 = a2, z2, a1, z1

        assert a1 <= a2

        if z1 is None:
            if z2 is not None and z2 + 1 < a1:
                raise RangeUnmergableError()
            else:
                self.first = min(a1, a2)
                self.last = None
        elif z2 is None:
            if z1 + 1 < a2:
                raise RangeUnmergableError()
            else:
                self.first = min(a1, a2)
                self.last = None
        else:
            if a2 > z1 + 1:
                raise RangeUnmergableError()
            else:
                self.first = a1
                self.last = max(z1, z2)
        return


class range_set(object):
    """A collection of range_specs, with units (e.g., bytes).
    """
    __slots__ = ['units', 'range_specs']

    def __init__(self):
        self.units = 'bytes'
        self.range_specs = []  # a list of range_spec objects

    def __str__(self):
        return self.units + '=' + ', '.join([str(s) for s in self.range_specs])

    def __repr__(self):
        return '%s.%s(%s)' % (self.__class__.__module__,
                              self.__class__.__name__,
                              repr(self.__str__()) )

    def from_str(self, s, valid_units=('bytes','none')):
        """Sets this range set based upon a string, such as the Range: header.

        You can also use the parse_range_set() function for more control.

        If a parsing error occurs, the pre-exising value of this range
        set is left unchanged.

        """
        r, k = parse_range_set( s, valid_units=valid_units )
        if k < len(s):
            raise ParseError("Extra unparsable characters in range set specifier",s,k)
        self.units = r.units
        self.range_specs = r.range_specs

    def is_single_range(self):
        """Does this range specifier consist of only a single range set?"""
        return len(self.range_specs) == 1

    def is_contiguous(self):
        """Can the collection of range_specs be coalesced into a single contiguous range?"""
        if len(self.range_specs) <= 1:
            return True
        merged = self.range_specs[0].copy()
        for s in self.range_specs[1:]:
            try:
                merged.merge_with(s)
            except:
                return False
        return True

    def fix_to_size(self, size):
        """Changes all length-relative range_specs to absolute range_specs based upon given file size.
        If none of the range_specs in this set can be satisfied, then the
        entire set is considered unsatifiable and an error is raised.
        Otherwise any unsatisfiable range_specs will simply be removed
        from this set.

        """
        for i in range(len(self.range_specs)):
            try:
                self.range_specs[i].fix_to_size( size )
            except RangeUnsatisfiableError:
                self.range_specs[i] = None
        self.range_specs = [s for s in self.range_specs if s is not None]
        if len(self.range_specs) == 0:
            raise RangeUnsatisfiableError('No ranges can be satisfied')

    def coalesce(self):
        """Collapses all consecutive range_specs which together define a contiguous range.

        Note though that this method will not re-sort the range_specs, so a
        potentially contiguous range may not be collapsed if they are
        not sorted.  For example the ranges:
            10-20, 30-40, 20-30
        will not be collapsed to just 10-40.  However if the ranges are
        sorted first as with:
            10-20, 20-30, 30-40
        then they will collapse to 10-40.
        """
        if len(self.range_specs) <= 1:
            return
        for i in range(len(self.range_specs) - 1):
            a = self.range_specs[i]
            b = self.range_specs[i+1]
            if a is not None:
                try:
                    a.merge_with( b )
                    self.range_specs[i+1] = None # to be deleted later
                except RangeUnmergableError:
                    pass
        self.range_specs = [r for r in self.range_specs if r is not None]


def parse_number( s, start=0 ):
    """Parses a positive decimal integer number from the string.

    A tuple is returned (number, chars_consumed).  If the
    string is not a valid decimal number, then (None,0) is returned.
    """
    if start >= len(s):
        raise ParseError('Starting position is beyond the end of the string',s,start)
    if s[start] not in DIGIT:
        return (None,0)  # not a number
    pos = start
    n = 0
    while pos < len(s):
        c = s[pos]
        if c in DIGIT:
            n *= 10
            n += ord(c) - ord('0')
            pos += 1
        else:
            break
    return n, pos-start


def parse_range_spec( s, start=0 ):
    """Parses a (byte) range_spec.

    Returns a tuple (range_spec, chars_consumed).
    """
    if start >= len(s):
        raise ParseError('Starting position is beyond the end of the string',s,start)
    if s[start] not in DIGIT and s[start] != '-':
        raise ParseError("Invalid range, expected a digit or '-'",s,start)
    first, last = None, None
    pos = start
    first, k = parse_number( s, pos )
    pos += k
    if s[pos] == '-':
        pos += 1
        if pos < len(s):
            last, k = parse_number( s, pos )
            pos += k
    else:
        raise ParseError("Byte range must include a '-'",s,pos)
    if first is None and last is None:
        raise ParseError('Byte range can not omit both first and last indices.',s,start)
    R = range_spec( first, last )
    return R, pos-start


def parse_range_header( header_value, valid_units=('bytes','none') ):
    """Parses the value of an HTTP Range: header.

    The value of the header as a string should be passed in; without
    the header name itself.

    Returns a range_set object.
    """
    ranges, k = parse_range_set( header_value, valid_units=valid_units )
    if k < len(header_value):
        raise ParseError('Range header has unexpected or unparsable characters',
                         header_value, k)
    return ranges


def parse_range_set( s, start=0, valid_units=('bytes','none') ):
    """Parses a (byte) range set specifier.

    Returns a tuple (range_set, chars_consumed).
    """
    if start >= len(s):
        raise ParseError('Starting position is beyond the end of the string',s,start)
    pos = start
    units, k = parse_token( s, pos )
    pos += k
    if valid_units and units not in valid_units:
        raise ParseError('Unsupported units type in range specifier',s,start)
    while pos < len(s) and s[pos] in LWS:
        pos += 1
    if pos < len(s) and s[pos] == '=':
        pos += 1
    else:
        raise ParseError("Invalid range specifier, expected '='",s,pos)
    while pos < len(s) and s[pos] in LWS:
        pos += 1
    range_specs, k = parse_comma_list( s, pos, parse_range_spec, min_count=1 )
    pos += k
    # Make sure no trash is at the end of the string
    while pos < len(s) and s[pos] in LWS:
        pos += 1
    if pos < len(s):
        raise ParseError('Unparsable characters in range set specifier',s,pos)

    ranges = range_set()
    ranges.units = units
    ranges.range_specs = range_specs
    return ranges, pos-start


def _split_at_qfactor( s ):
    """Splits a string at the quality factor (;q=) parameter.

    Returns the left and right substrings as a two-member tuple.

    """
    # It may be faster, but incorrect, to use s.split(';q=',1), since
    # HTTP allows any amount of linear white space (LWS) to appear
    # between the parts, so it could also be "; q = ".

    # We do this parsing 'manually' for speed rather than using a
    # regex, which would be r';[ \t\r\n]*q[ \t\r\n]*=[ \t\r\n]*'

    pos = 0
    while 0 <= pos < len(s):
        pos = s.find(';', pos)
        if pos < 0:
            break # no more parameters
        startpos = pos
        pos = pos + 1
        while pos < len(s) and s[pos] in LWS:
            pos = pos + 1
        if pos < len(s) and s[pos] == 'q':
            pos = pos + 1
            while pos < len(s) and s[pos] in LWS:
                pos = pos + 1
            if pos < len(s) and s[pos] == '=':
                pos = pos + 1
                while pos < len(s) and s[pos] in LWS:
                    pos = pos + 1
                return ( s[:startpos], s[pos:] )
    return (s, '')


def parse_qvalue_accept_list( s, start=0, item_parser=parse_token ):
    """Parses any of the Accept-* style headers with quality factors.

    This is a low-level function.  It returns a list of tuples, each like:
       (item, item_parms, qvalue, accept_parms)

    You can pass in a function which parses each of the item strings, or
    accept the default where the items must be simple tokens.  Note that
    your parser should not consume any paramters (past the special "q"
    paramter anyway).

    The item_parms and accept_parms are each lists of (name,value) tuples.

    The qvalue is the quality factor, a number from 0 to 1 inclusive.

    """
    itemlist = []
    pos = start
    if pos >= len(s):
        raise ParseError('Starting position is beyond the end of the string',s,pos)
    item = None
    while pos < len(s):
        item, k = item_parser(s, pos)
        pos += k
        while pos < len(s) and s[pos] in LWS:
            pos += 1
        if pos >= len(s) or s[pos] in ',;':
            itemparms, qvalue, acptparms = [], None, []
            if pos < len(s) and s[pos] == ';':
                pos += 1
                while pos < len(s) and s[pos] in LWS:
                    pos += 1
                parmlist, k = parse_parameter_list(s, pos)
                for p, v in parmlist:
                    if p == 'q' and qvalue is None:
                        try:
                            qvalue = float(v)
                        except ValueError:
                            raise ParseError('qvalue must be a floating point number',s,pos)
                        if qvalue < 0 or qvalue > 1:
                            raise ParseError('qvalue must be between 0 and 1, inclusive',s,pos)
                    elif qvalue is None:
                        itemparms.append( (p,v) )
                    else:
                        acptparms.append( (p,v) )
                pos += k
            if item:
                # Add the item to the list
                if qvalue is None:
                    qvalue = 1
                itemlist.append( (item, itemparms, qvalue, acptparms) )
                item = None
            # skip commas
            while pos < len(s) and s[pos] == ',':
                pos += 1
                while pos < len(s) and s[pos] in LWS:
                    pos += 1
        else:
            break
    return itemlist, pos - start


def parse_accept_header( header_value ):
    """Parses the Accept: header.

    The value of the header as a string should be passed in; without
    the header name itself.
    
    This will parse the value of any of the HTTP headers "Accept",
    "Accept-Charset", "Accept-Encoding", or "Accept-Language".  These
    headers are similarly formatted, in that they are a list of items
    with associated quality factors.  The quality factor, or qvalue,
    is a number in the range [0.0..1.0] which indicates the relative
    preference of each item.

    This function returns a list of those items, sorted by preference
    (from most-prefered to least-prefered).  Each item in the returned
    list is actually a tuple consisting of:

       ( item_name, item_parms, qvalue, accept_parms )

    As an example, the following string,
        text/plain; charset="utf-8"; q=.5; columns=80
    would be parsed into this resulting tuple,
        ( 'text/plain', [('charset','utf-8')], 0.5, [('columns','80')] )

    The value of the returned item_name depends upon which header is
    being parsed, but for example it may be a MIME content or media
    type (without parameters), a language tag, or so on.  Any optional
    parameters (delimited by semicolons) occuring before the "q="
    attribute will be in the item_parms list as (attribute,value)
    tuples in the same order as they appear in the header.  Any quoted
    values will have been unquoted and unescaped.

    The qvalue is a floating point number in the inclusive range 0.0
    to 1.0, and roughly indicates the preference for this item.
    Values outside this range will be capped to the closest extreme.

         (!) Note that a qvalue of 0 indicates that the item is
         explicitly NOT acceptable to the user agent, and should be
         handled differently by the caller.

    The accept_parms, like the item_parms, is a list of any attributes
    occuring after the "q=" attribute, and will be in the list as
    (attribute,value) tuples in the same order as they occur.
    Usually accept_parms will be an empty list, as the HTTP spec
    allows these extra parameters in the syntax but does not
    currently define any possible values.

    All empty items will be removed from the list.  However, duplicate
    or conflicting values are not detected or handled in any way by
    this function.
    """
    def parse_mt_only(s, start):
        mt, k = parse_media_type(s, start, with_parameters=False)
        ct = content_type()
        ct.major = mt[0]
        ct.minor = mt[1]
        return ct, k

    alist, k = parse_qvalue_accept_list( header_value, item_parser=parse_mt_only )
    if k < len(header_value):
        raise ParseError('Accept header is invalid',header_value,k)

    ctlist = []
    for ct, ctparms, q, acptparms  in alist:
        if ctparms:
            ct.set_parameters( dict(ctparms) )
        ctlist.append( (ct, q, acptparms) )
    return ctlist


def parse_media_type(media_type, start=0, with_parameters=True):
    """Parses a media type (MIME type) designator into it's parts.

    Given a media type string, returns a nested tuple of it's parts.

        ((major,minor,parmlist), chars_consumed)

    where parmlist is a list of tuples of (parm_name, parm_value).
    Quoted-values are appropriately unquoted and unescaped.
    
    If 'with_parameters' is False, then parsing will stop immediately
    after the minor media type; and will not proceed to parse any
    of the semicolon-separated paramters.

    Examples:
        image/png -> (('image','png',[]), 9)
        text/plain; charset="utf-16be"
                  -> (('text','plain',[('charset,'utf-16be')]), 30)

    """

    s = media_type
    pos = start
    ctmaj, k = parse_token(s, pos)
    if k == 0:
        raise ParseError('Media type must be of the form "major/minor".', s, pos)
    pos += k
    if pos >= len(s) or s[pos] != '/':
        raise ParseError('Media type must be of the form "major/minor".', s, pos)
    pos += 1
    ctmin, k = parse_token(s, pos)
    if k == 0:
        raise ParseError('Media type must be of the form "major/minor".', s, pos)
    pos += k
    if with_parameters:
        parmlist, k = parse_parameter_list(s, pos)
        pos += k
    else:
        parmlist = []
    return ((ctmaj, ctmin, parmlist), pos - start)


def parse_parameter_list(s, start=0):
    """Parses a semicolon-separated 'parameter=value' list.

    Returns a tuple (parmlist, chars_consumed), where parmlist
    is a list of tuples (parm_name, parm_value).

    The parameter values will be unquoted and unescaped as needed.

    Empty parameters (as in ";;") are skipped, as is insignificant
    white space.  The list returned is kept in the same order as the
    parameters appear in the string.

    """
    pos = start
    parmlist = []
    while pos < len(s):
        while pos < len(s) and s[pos] in LWS:
            pos += 1 # skip whitespace
        if pos < len(s) and s[pos] == ';':
            pos += 1
            while pos < len(s) and s[pos] in LWS:
                pos += 1 # skip whitespace
        if pos >= len(s):
            break
        parmname, k = parse_token(s, pos)
        if parmname:
            pos += k
            while pos < len(s) and s[pos] in LWS:
                pos += 1 # skip whitespace
            if not (pos < len(s) and s[pos] == '='):
                raise ParseError('Expected an "=" after parameter name', s, pos)
            pos += 1
            while pos < len(s) and s[pos] in LWS:
                pos += 1 # skip whitespace
            parmval, k = parse_token_or_quoted_string( s, pos )
            pos += k
            parmlist.append( (parmname, parmval) )
        else:
            break
    return parmlist, pos - start


class content_type(object):
    """This class represents a media type (aka a MIME content type), including parameters.

    You initialize these by passing in a content-type declaration
    string, such as "text/plain; charset=ascii", to the constructor or
    to the set() method.  If you provide no string value, the object
    returned will represent the wildcard */* content type.

    Normally you will get the value back by using str(), or optionally
    you can access the components via the 'major', 'minor', 'media_type',
    or 'parmdict' members.

    """
    def __init__(self, content_type_string=None, with_parameters=True):
        """Create a new content_type object.

        See the set() method for a description of the arguments.
        """
        if content_type_string:
            self.set( content_type_string, with_parameters=with_parameters )
        else:
            self.set( '*/*' )

    def set_parameters(self, parameter_list_or_dict):
        """Sets the optional paramters based upon the parameter list.

        The paramter list should be a semicolon-separated name=value string.
        Any paramters which already exist on this object will be deleted,
        unless they appear in the given paramter_list.

        """
        if hasattr(parameter_list_or_dict, 'has_key'):
            # already a dictionary
            pl = parameter_list_or_dict
        else:
            pl, k = parse_parameter_list(parameter_list)
            if k < len(parameter_list):
                raise ParseError('Invalid parameter list',paramter_list,k)
        self.parmdict = dict(pl)

    def set(self, content_type_string, with_parameters=True):
        """Parses the content type string and sets this object to it's value.

        For a more complete description of the arguments, see the
        documentation for the parse_media_type() function in this module.
        """
        mt, k = parse_media_type( content_type_string, with_parameters=with_parameters )
        if k < len(content_type_string):
            raise ParseError('Not a valid content type',content_type_string, k)
        major, minor, pdict = mt
        self._set_major( major )
        self._set_minor( minor )
        self.parmdict = dict(pdict)
        
    def _get_major(self):
        return self._major
    def _set_major(self, s):
        s = s.lower()  # case-insentive
        if not is_token(s):
            raise ValueError('Major media type contains an invalid character')
        self._major = s

    def _get_minor(self):
        return self._minor
    def _set_minor(self, s):
        s = s.lower()  # case-insentive
        if not is_token(s):
            raise ValueError('Minor media type contains an invalid character')
        self._minor = s

    major = property(_get_major,_set_major,doc="Major media classification")
    minor = property(_get_minor,_set_minor,doc="Minor media sub-classification")

    def __str__(self):
        """String value."""
        s = '%s/%s' % (self.major, self.minor)
        if self.parmdict:
            extra = '; '.join([ '%s=%s' % (a[0],quote_string(a[1],False)) for a in self.parmdict.items()])
            s += '; ' + extra
        return s

    def __unicode__(self):
        """Unicode string value."""
        # In Python 3 this is probably unnecessary in general, this is just to avoid possible syntax issues. I.H.
        if PY3 :
            return str(self.__str__())
        else :
            return unicode(self.__str__())

    def __repr__(self):
        """Python representation of this object."""
        s = '%s(%s)' % (self.__class__.__name__, repr(self.__str__()))
        return s


    def __hash__(self):
        """Hash this object; the hash is dependent only upon the value."""
        return hash(str(self))

    def __getstate__(self):
        """Pickler"""
        return str(self)

    def __setstate__(self, state):
        """Unpickler"""
        self.set(state)

    def __len__(self):
        """Logical length of this media type.
        For example:
           len('*/*')  -> 0
           len('image/*') -> 1
           len('image/png') -> 2
           len('text/plain; charset=utf-8')  -> 3
           len('text/plain; charset=utf-8; filename=xyz.txt') -> 4

        """
        if self.major == '*':
            return 0
        elif self.minor == '*':
            return 1
        else:
            return 2 + len(self.parmdict)

    def __eq__(self, other):
        """Equality test.

        Note that this is an exact match, including any parameters if any.
        """
        return self.major == other.major and \
                   self.minor == other.minor and \
                   self.parmdict == other.parmdict

    def __ne__(self, other):
        """Inequality test."""
        return not self.__eq__(other)
            
    def _get_media_type(self):
        """Returns the media 'type/subtype' string, without parameters."""
        return '%s/%s' % (self.major, self.minor)

    media_type = property(_get_media_type, doc="Returns the just the media type 'type/subtype' without any paramters (read-only).")

    def is_wildcard(self):
        """Returns True if this is a 'something/*' media type.
        """
        return self.minor == '*'

    def is_universal_wildcard(self):
        """Returns True if this is the unspecified '*/*' media type.
        """
        return self.major == '*' and self.minor == '*'

    def is_composite(self):
        """Is this media type composed of multiple parts.
        """
        return self.major == 'multipart' or self.major == 'message'

    def is_xml(self):
        """Returns True if this media type is XML-based.

        Note this does not consider text/html to be XML, but
        application/xhtml+xml is.
        """
        return self.minor == 'xml' or self.minor.endswith('+xml')

# Some common media types
content_formdata = content_type('multipart/form-data')
content_urlencoded = content_type('application/x-www-form-urlencoded')
content_byteranges = content_type('multipart/byteranges') # RFC 2616 sect 14.16
content_opaque = content_type('application/octet-stream')
content_html = content_type('text/html')
content_xhtml = content_type('application/xhtml+xml')


def acceptable_content_type( accept_header, content_types, ignore_wildcard=True ):
    """Determines if the given content type is acceptable to the user agent.

    The accept_header should be the value present in the HTTP
    "Accept:" header.  In mod_python this is typically obtained from
    the req.http_headers_in table; in WSGI it is environ["Accept"];
    other web frameworks may provide other methods of obtaining it.

    Optionally the accept_header parameter can be pre-parsed, as
    returned from the parse_accept_header() function in this module.

    The content_types argument should either be a single MIME media
    type string, or a sequence of them.  It represents the set of
    content types that the caller (server) is willing to send.
    Generally, the server content_types should not contain any
    wildcarded values.

    This function determines which content type which is the most
    preferred and is acceptable to both the user agent and the server.
    If one is negotiated it will return a four-valued tuple like:

        (server_content_type, ua_content_range, qvalue, accept_parms)

    The first tuple value is one of the server's content_types, while
    the remaining tuple values descript which of the client's
    acceptable content_types was matched.  In most cases accept_parms
    will be an empty list (see description of parse_accept_header()
    for more details).

    If no content type could be negotiated, then this function will
    return None (and the caller should typically cause an HTTP 406 Not
    Acceptable as a response).

    Note that the wildcarded content type "*/*" sent by the client
    will be ignored, since it is often incorrectly sent by web
    browsers that don't really mean it.  To override this, call with
    ignore_wildcard=False.  Partial wildcards such as "image/*" will
    always be processed, but be at a lower priority than a complete
    matching type.

    See also: RFC 2616 section 14.1, and
    <http://www.iana.org/assignments/media-types/>

    """
    if _is_string(accept_header):
        accept_list = parse_accept_header(accept_header)
    else:
        accept_list = accept_header

    if _is_string(content_types):
        content_types = [content_types]

    server_ctlist = [content_type(ct) for ct in content_types]
    del ct

    #print 'AC', repr(accept_list)
    #print 'SV', repr(server_ctlist)

    best = None   # (content_type, qvalue, accept_parms, matchlen)

    for server_ct in server_ctlist:
        best_for_this = None
        for client_ct, qvalue, aargs in accept_list:
            if ignore_wildcard and client_ct.is_universal_wildcard():
                continue  # */* being ignored

            matchlen = 0 # how specifically this one matches (0 is a non-match)
            if client_ct.is_universal_wildcard():
                matchlen = 1   # */* is a 1
            elif client_ct.major == server_ct.major:
                if client_ct.minor == '*':  # something/* is a 2
                    matchlen = 2
                elif client_ct.minor == server_ct.minor: # something/something is a 3
                    matchlen = 3
                    # must make sure all the parms match too
                    for pname, pval in client_ct.parmdict.items():
                        sval = server_ct.parmdict.get(pname)
                        if pname == 'charset':
                            # special case for charset to match aliases
                            pval = canonical_charset(pval)
                            sval = canonical_charset(sval)
                        if sval == pval:
                            matchlen = matchlen + 1
                        else:
                            matchlen = 0
                            break
                else:
                    matchlen = 0

            #print 'S',server_ct,'  C',client_ct,'  M',matchlen,'Q',qvalue
            if matchlen > 0:
                if not best_for_this \
                       or matchlen > best_for_this[-1] \
                       or (matchlen == best_for_this[-1] and qvalue > best_for_this[2]):
                    # This match is better
                    best_for_this = (server_ct, client_ct, qvalue, aargs, matchlen)
                    #print 'BEST2 NOW', repr(best_for_this)
        if not best or \
               (best_for_this and best_for_this[2] > best[2]):
            best = best_for_this
            #print 'BEST NOW', repr(best)
    if not best or best[1] <= 0:
        return None
    return best[:-1]


# Aliases of common charsets, see <http://www.iana.org/assignments/character-sets>.
character_set_aliases = {
    'ASCII': 'US-ASCII',
    'ISO646-US': 'US-ASCII',
    'IBM367': 'US-ASCII',
    'CP367': 'US-ASCII',
    'CSASCII': 'US-ASCII',
    'ANSI_X3.4-1968': 'US-ASCII',
    'ISO_646.IRV:1991': 'US-ASCII',

    'UTF7': 'UTF-7',

    'UTF8': 'UTF-8',

    'UTF16': 'UTF-16',
    'UTF16LE': 'UTF-16LE',
    'UTF16BE': 'UTF-16BE',

    'UTF32': 'UTF-32',
    'UTF32LE': 'UTF-32LE',
    'UTF32BE': 'UTF-32BE',

    'UCS2': 'ISO-10646-UCS-2',
    'UCS_2': 'ISO-10646-UCS-2',
    'UCS-2': 'ISO-10646-UCS-2',
    'CSUNICODE': 'ISO-10646-UCS-2',

    'UCS4': 'ISO-10646-UCS-4',
    'UCS_4': 'ISO-10646-UCS-4',
    'UCS-4': 'ISO-10646-UCS-4',
    'CSUCS4': 'ISO-10646-UCS-4',

    'ISO_8859-1': 'ISO-8859-1',
    'LATIN1': 'ISO-8859-1',
    'CP819': 'ISO-8859-1',
    'IBM819': 'ISO-8859-1',

    'ISO_8859-2': 'ISO-8859-2',
    'LATIN2': 'ISO-8859-2',

    'ISO_8859-3': 'ISO-8859-3',
    'LATIN3': 'ISO-8859-3',

    'ISO_8859-4': 'ISO-8859-4',
    'LATIN4': 'ISO-8859-4',

    'ISO_8859-5': 'ISO-8859-5',
    'CYRILLIC': 'ISO-8859-5',

    'ISO_8859-6': 'ISO-8859-6',
    'ARABIC': 'ISO-8859-6',
    'ECMA-114': 'ISO-8859-6',

    'ISO_8859-6-E': 'ISO-8859-6-E',
    'ISO_8859-6-I': 'ISO-8859-6-I',

    'ISO_8859-7': 'ISO-8859-7',
    'GREEK': 'ISO-8859-7',
    'GREEK8': 'ISO-8859-7',
    'ECMA-118': 'ISO-8859-7',

    'ISO_8859-8': 'ISO-8859-8',
    'HEBREW': 'ISO-8859-8',

    'ISO_8859-8-E': 'ISO-8859-8-E',
    'ISO_8859-8-I': 'ISO-8859-8-I',

    'ISO_8859-9': 'ISO-8859-9',
    'LATIN5': 'ISO-8859-9',

    'ISO_8859-10': 'ISO-8859-10',
    'LATIN6': 'ISO-8859-10',

    'ISO_8859-13': 'ISO-8859-13',

    'ISO_8859-14': 'ISO-8859-14',
    'LATIN8': 'ISO-8859-14',

    'ISO_8859-15': 'ISO-8859-15',
    'LATIN9': 'ISO-8859-15',

    'ISO_8859-16': 'ISO-8859-16',
    'LATIN10': 'ISO-8859-16',
    }

def canonical_charset( charset ):
    """Returns the canonical or preferred name of a charset.

    Additional character sets can be recognized by this function by
    altering the character_set_aliases dictionary in this module.
    Charsets which are not recognized are simply converted to
    upper-case (as charset names are always case-insensitive).
    
    See <http://www.iana.org/assignments/character-sets>.

    """
    # It would be nice to use Python's codecs modules for this, but
    # there is no fixed public interface to it's alias mappings.
    if not charset:
        return charset
    uc = charset.upper()
    uccon = character_set_aliases.get( uc, uc )
    return uccon


def acceptable_charset( accept_charset_header, charsets, ignore_wildcard=True, default='ISO-8859-1' ):
    """
    Determines if the given charset is acceptable to the user agent.

    The accept_charset_header should be the value present in the HTTP
    "Accept-Charset:" header.  In mod_python this is typically
    obtained from the req.http_headers table; in WSGI it is
    environ["Accept-Charset"]; other web frameworks may provide other
    methods of obtaining it.

    Optionally the accept_charset_header parameter can instead be the
    list returned from the parse_accept_header() function in this
    module.

    The charsets argument should either be a charset identifier string,
    or a sequence of them.

    This function returns the charset identifier string which is the
    most prefered and is acceptable to both the user agent and the
    caller.  It will return the default value if no charset is negotiable.
    
    Note that the wildcarded charset "*" will be ignored.  To override
    this, call with ignore_wildcard=False.

    See also: RFC 2616 section 14.2, and
    <http://www.iana.org/assignments/character-sets>

    """
    if default:
        default = _canonical_charset(default)

    if _is_string(accept_charset_header):
        accept_list = parse_accept_header(accept_charset_header)
    else:
        accept_list = accept_charset_header

    if _is_string(charsets):
        charsets = [_canonical_charset(charsets)]
    else:
        charsets = [_canonical_charset(c) for c in charsets]

    # Note per RFC that 'ISO-8859-1' is special, and is implictly in the
    # accept list with q=1; unless it is already in the list, or '*' is in the list.

    best = None
    for c, qvalue, junk in accept_list:
        if c == '*':
            default = None
            if ignore_wildcard:
                continue
            if not best or qvalue > best[1]:
                best = (c, qvalue)
        else:
            c = _canonical_charset(c)
            for test_c in charsets:
                if c == default:
                    default = None
                if c == test_c and (not best or best[0]=='*' or qvalue > best[1]):
                    best = (c, qvalue)
    if default and default in [test_c.upper() for test_c in charsets]:
        best = (default, 1)
    if best[0] == '*':
        best = (charsets[0], best[1])
    return best



class language_tag(object):
    """This class represents an RFC 3066 language tag.

    Initialize objects of this class with a single string representing
    the language tag, such as "en-US".
        
    Case is insensitive. Wildcarded subtags are ignored or stripped as
    they have no significance, so that "en-*" is the same as "en".
    However the universal wildcard "*" language tag is kept as-is.

    Note that although relational operators such as < are defined,
    they only form a partial order based upon specialization.

    Thus for example,
         "en" <= "en-US"
    but,
         not "en" <= "de", and
         not "de" <= "en".

    """

    def __init__(self, tagname):
        """Initialize objects of this class with a single string representing
        the language tag, such as "en-US".  Case is insensitive.

        """

        self.parts = tagname.lower().split('-')
        while len(self.parts) > 1 and self.parts[-1] == '*':
            del self.parts[-1]

    def __len__(self):
        """Number of subtags in this tag."""
        if len(self.parts) == 1 and self.parts[0] == '*':
            return 0
        return len(self.parts)

    def __str__(self):
        """The standard string form of this language tag."""
        a = []
        if len(self.parts) >= 1:
            a.append(self.parts[0])
        if len(self.parts) >= 2:
            if len(self.parts[1]) == 2:
                a.append( self.parts[1].upper() )
            else:
                a.append( self.parts[1] )
        a.extend( self.parts[2:] )
        return '-'.join(a)

    def __unicode__(self):
        """The unicode string form of this language tag."""
        # Probably unnecessary in Python 3
        if PY3 :
            return str(self.__str__())
        else :
            return unicode(self.__str__())

    def __repr__(self):
        """The python representation of this language tag."""
        s = '%s("%s")' % (self.__class__.__name__, self.__str__())
        return s

    def superior(self):
        """Returns another instance of language_tag which is the superior.

        Thus en-US gives en, and en gives *.

        """
        if len(self) <= 1:
            return self.__class__('*')
        return self.__class__( '-'.join(self.parts[:-1]) )

    def all_superiors(self, include_wildcard=False):
        """Returns a list of this language and all it's superiors.

        If include_wildcard is False, then "*" will not be among the
        output list, unless this language is itself "*".

        """
        langlist = [ self ]
        l = self
        while not l.is_universal_wildcard():
            l = l.superior()
            if l.is_universal_wildcard() and not include_wildcard:
                continue
            langlist.append(l)
        return langlist
                
    def is_universal_wildcard(self):
        """Returns True if this language tag represents all possible
        languages, by using the reserved tag of "*".

        """
        return len(self.parts) == 1 and self.parts[0] == '*'

    def dialect_of(self, other, ignore_wildcard=True):
        """Is this language a dialect (or subset/specialization) of another.

        This method returns True if this language is the same as or a
        specialization (dialect) of the other language_tag.

        If ignore_wildcard is False, then all languages will be
        considered to be a dialect of the special language tag of "*".

        """
        if not ignore_wildcard and self.is_universal_wildcard():
            return True
        for i in range( min(len(self), len(other)) ):
            if self.parts[i] != other.parts[i]:
                return False
        if len(self) >= len(other):
            return True
        return False

    def __eq__(self, other):
        """== operator. Are the two languages the same?"""

        return self.parts == other.parts

    def __neq__(self, other):
        """!= operator. Are the two languages different?"""

        return not self.__eq__(other)

    def __lt__(self, other):
        """< operator. Returns True if the other language is a more
        specialized dialect of this one."""

        return other.dialect_of(self) and self != other

    def __le__(self, other):
        """<= operator. Returns True if the other language is the same
        as or a more specialized dialect of this one."""
        return other.dialect_of(self)

    def __gt__(self, other):
        """> operator.  Returns True if this language is a more
        specialized dialect of the other one."""

        return self.dialect_of(other) and self != other

    def __ge__(self, other):
        """>= operator.  Returns True if this language is the same as
        or a more specialized dialect of the other one."""

        return self.dialect_of(other)


def parse_accept_language_header( header_value ):
    """Parses the Accept-Language header.

    Returns a list of tuples, each like:

        (language_tag, qvalue, accept_parameters)

    """
    alist, k = parse_qvalue_accept_list( header_value)
    if k < len(header_value):
        raise ParseError('Accept-Language header is invalid',header_value,k)

    langlist = []
    for token, langparms, q, acptparms in alist:
        if langparms:
            raise ParseError('Language tag may not have any parameters',header_value,0)
        lang = language_tag( token )
        langlist.append( (lang, q, acptparms) )

    return langlist


def acceptable_language( accept_header, server_languages, ignore_wildcard=True, assume_superiors=True ):
    """Determines if the given language is acceptable to the user agent.

    The accept_header should be the value present in the HTTP
    "Accept-Language:" header.  In mod_python this is typically
    obtained from the req.http_headers_in table; in WSGI it is
    environ["Accept-Language"]; other web frameworks may provide other
    methods of obtaining it.

    Optionally the accept_header parameter can be pre-parsed, as
    returned by the parse_accept_language_header() function defined in
    this module.

    The server_languages argument should either be a single language
    string, a language_tag object, or a sequence of them.  It
    represents the set of languages that the server is willing to
    send to the user agent.

    Note that the wildcarded language tag "*" will be ignored.  To
    override this, call with ignore_wildcard=False, and even then
    it will be the lowest-priority choice regardless of it's
    quality factor (as per HTTP spec).

    If the assume_superiors is True then it the languages that the
    browser accepts will automatically include all superior languages.
    Any superior languages which must be added are done so with one
    half the qvalue of the language which is present.  For example, if
    the accept string is "en-US", then it will be treated as if it
    were "en-US, en;q=0.5".  Note that although the HTTP 1.1 spec says
    that browsers are supposed to encourage users to configure all
    acceptable languages, sometimes they don't, thus the ability
    for this function to assume this.  But setting assume_superiors
    to False will insure strict adherence to the HTTP 1.1 spec; which
    means that if the browser accepts "en-US", then it will not
    be acceptable to send just "en" to it.

    This function returns the language which is the most prefered and
    is acceptable to both the user agent and the caller.  It will
    return None if no language is negotiable, otherwise the return
    value is always an instance of language_tag.

    See also: RFC 3066 <http://www.ietf.org/rfc/rfc3066.txt>, and
    ISO 639, links at <http://en.wikipedia.org/wiki/ISO_639>, and
    <http://www.iana.org/assignments/language-tags>.
    
    """
    # Note special instructions from RFC 2616 sect. 14.1:
    #   "The language quality factor assigned to a language-tag by the
    #   Accept-Language field is the quality value of the longest
    #   language- range in the field that matches the language-tag."

    if _is_string(accept_header):
        accept_list = parse_accept_language_header(accept_header)
    else:
        accept_list = accept_header

    # Possibly add in any "missing" languages that the browser may
    # have forgotten to include in the list. Insure list is sorted so
    # more general languages come before more specific ones.

    accept_list.sort()
    all_tags = [a[0] for a in accept_list]
    if assume_superiors:
        to_add = []
        for langtag, qvalue, aargs in accept_list:
            if len(langtag) >= 2:
                for suptag in langtag.all_superiors( include_wildcard=False ):
                    if suptag not in all_tags:
                        # Add in superior at half the qvalue
                        to_add.append( (suptag, qvalue / 2, '') )
                        all_tags.append( suptag )
        accept_list.extend( to_add )

    # Convert server_languages to a list of language_tags
    if _is_string(server_languages):
        server_languages = [language_tag(server_languages)]
    elif isinstance(server_languages, language_tag):
        server_languages = [server_languages]
    else:
        server_languages = [language_tag(lang) for lang in server_languages]

    # Select the best one
    best = None  # tuple (langtag, qvalue, matchlen)
    
    for langtag, qvalue, aargs in accept_list:
        # aargs is ignored for Accept-Language
        if qvalue <= 0:
            continue # UA doesn't accept this language

        if ignore_wildcard and langtag.is_universal_wildcard():
            continue  # "*" being ignored

        for svrlang in server_languages:
            # The best match is determined first by the quality factor,
            # and then by the most specific match.

            matchlen = -1 # how specifically this one matches (0 is a non-match)
            if svrlang.dialect_of( langtag, ignore_wildcard=ignore_wildcard ):
                matchlen = len(langtag)
                if not best \
                       or matchlen > best[2] \
                       or (matchlen == best[2] and qvalue > best[1]):
                    # This match is better
                    best = (langtag, qvalue, matchlen)
    if not best:
        return None
    return best[0]


# Clean up global namespace
try:
    if __emulating_set:
        del set
        del frozenset
except NameError:
    pass

# end of file
