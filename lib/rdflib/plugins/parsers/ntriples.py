#!/usr/bin/env python
__doc__ = """
N-Triples Parser
License: GPL 2, W3C, BSD, or MIT
Author: Sean B. Palmer, inamidst.com
"""

import re
import codecs

from rdflib.term import URIRef as URI
from rdflib.term import BNode as bNode
from rdflib.term import Literal

from rdflib.py3compat import cast_bytes, decodeUnicodeEscape

__all__ = ['unquote', 'uriquote', 'Sink', 'NTriplesParser']

uriref = r'<([^:]+:[^\s"<>]+)>'
literal = r'"([^"\\]*(?:\\.[^"\\]*)*)"'
litinfo = r'(?:@([a-z]+(?:-[a-zA-Z0-9]+)*)|\^\^' + uriref + r')?'

r_line = re.compile(r'([^\r\n]*)(?:\r\n|\r|\n)')
r_wspace = re.compile(r'[ \t]*')
r_wspaces = re.compile(r'[ \t]+')
r_tail = re.compile(r'[ \t]*\.[ \t]*(#.*)?')
r_uriref = re.compile(uriref)
r_nodeid = re.compile(r'_:([A-Za-z0-9]*)')
r_literal = re.compile(literal + litinfo)

bufsiz = 2048
validate = False


class Node(unicode):
    pass


class ParseError(Exception):
    pass


class Sink(object):
    def __init__(self):
        self.length = 0

    def triple(self, s, p, o):
        self.length += 1
        print (s, p, o)

quot = {'t': u'\t', 'n': u'\n', 'r': u'\r', '"': u'"', '\\':
        u'\\'}
r_safe = re.compile(r'([\x20\x21\x23-\x5B\x5D-\x7E]+)')
r_quot = re.compile(r'\\(t|n|r|"|\\)')
r_uniquot = re.compile(r'\\u([0-9A-F]{4})|\\U([0-9A-F]{8})')


def unquote(s):
    """Unquote an N-Triples string."""
    if not validate:

        if isinstance(s, unicode): # nquads
            s = decodeUnicodeEscape(s)
        else:
            s = s.decode('unicode-escape')

        return s
    else:
        result = []
        while s:
            m = r_safe.match(s)
            if m:
                s = s[m.end():]
                result.append(m.group(1))
                continue

            m = r_quot.match(s)
            if m:
                s = s[2:]
                result.append(quot[m.group(1)])
                continue

            m = r_uniquot.match(s)
            if m:
                s = s[m.end():]
                u, U = m.groups()
                codepoint = int(u or U, 16)
                if codepoint > 0x10FFFF:
                    raise ParseError("Disallowed codepoint: %08X" % codepoint)
                result.append(unichr(codepoint))
            elif s.startswith('\\'):
                raise ParseError("Illegal escape at: %s..." % s[:10])
            else:
                raise ParseError("Illegal literal character: %r" % s[0])
        return u''.join(result)

r_hibyte = re.compile(ur'([\x80-\xFF])')


def uriquote(uri):
    if not validate:
        return uri
    else:
        return r_hibyte.sub(
            lambda m: '%%%02X' % ord(m.group(1)), uri)


class NTriplesParser(object):
    """An N-Triples Parser.

    Usage::

          p = NTriplesParser(sink=MySink())
          sink = p.parse(f) # file; use parsestring for a string
    """

    _bnode_ids = {}

    def __init__(self, sink=None):
        if sink is not None:
            self.sink = sink
        else:
            self.sink = Sink()

    def parse(self, f):
        """Parse f as an N-Triples file."""
        if not hasattr(f, 'read'):
            raise ParseError("Item to parse must be a file-like object.")

        # since N-Triples 1.1 files can and should be utf-8 encoded
        f = codecs.getreader('utf-8')(f)

        self.file = f
        self.buffer = ''
        while True:
            self.line = self.readline()
            if self.line is None:
                break
            try:
                self.parseline()
            except ParseError:
                raise ParseError("Invalid line: %r" % self.line)
        return self.sink

    def parsestring(self, s):
        """Parse s as an N-Triples string."""
        if not isinstance(s, basestring):
            raise ParseError("Item to parse must be a string instance.")
        try:
            from io import BytesIO
            assert BytesIO
        except ImportError:
            from cStringIO import StringIO as BytesIO
            assert BytesIO
        f = BytesIO()
        f.write(cast_bytes(s))
        f.seek(0)
        self.parse(f)

    def readline(self):
        """Read an N-Triples line from buffered input."""
        # N-Triples lines end in either CRLF, CR, or LF
        # Therefore, we can't just use f.readline()
        if not self.buffer:
            buffer = self.file.read(bufsiz)
            if not buffer:
                return None
            self.buffer = buffer

        while True:
            m = r_line.match(self.buffer)
            if m:  # the more likely prospect
                self.buffer = self.buffer[m.end():]
                return m.group(1)
            else:
                buffer = self.file.read(bufsiz)
                if not buffer and not self.buffer.isspace():
                    # Last line does not need to be terminated with a newline
                    buffer += "\n"
                elif not buffer:
                    return None
                self.buffer += buffer

    def parseline(self):
        self.eat(r_wspace)
        if (not self.line) or self.line.startswith('#'):
            return  # The line is empty or a comment

        subject = self.subject()
        self.eat(r_wspaces)

        predicate = self.predicate()
        self.eat(r_wspaces)

        object = self.object()
        self.eat(r_tail)

        if self.line:
            raise ParseError("Trailing garbage")
        self.sink.triple(subject, predicate, object)

    def peek(self, token):
        return self.line.startswith(token)

    def eat(self, pattern):
        m = pattern.match(self.line)
        if not m:  # @@ Why can't we get the original pattern?
            # print(dir(pattern))
            # print repr(self.line), type(self.line)
            raise ParseError("Failed to eat %s at %s" % (pattern, self.line))
        self.line = self.line[m.end():]
        return m

    def subject(self):
        # @@ Consider using dictionary cases
        subj = self.uriref() or self.nodeid()
        if not subj:
            raise ParseError("Subject must be uriref or nodeID")
        return subj

    def predicate(self):
        pred = self.uriref()
        if not pred:
            raise ParseError("Predicate must be uriref")
        return pred

    def object(self):
        objt = self.uriref() or self.nodeid() or self.literal()
        if objt is False:
            raise ParseError("Unrecognised object type")
        return objt

    def uriref(self):
        if self.peek('<'):
            uri = self.eat(r_uriref).group(1)
            uri = unquote(uri)
            uri = uriquote(uri)
            return URI(uri)
        return False

    def nodeid(self):
        if self.peek('_'):
            # Fix for https://github.com/RDFLib/rdflib/issues/204
            bnode_id = self.eat(r_nodeid).group(1)
            new_id = self._bnode_ids.get(bnode_id, None)
            if new_id is not None:
                # Re-map to id specfic to this doc
                return bNode(new_id)
            else:
                # Replace with freshly-generated document-specific BNode id
                bnode = bNode()
                # Store the mapping
                self._bnode_ids[bnode_id] = bnode
                return bnode
        return False

    def literal(self):
        if self.peek('"'):
            lit, lang, dtype = self.eat(r_literal).groups()
            if lang:
                lang = lang
            else:
                lang = None
            if dtype:
                dtype = dtype
            else:
                dtype = None
            if lang and dtype:
                raise ParseError("Can't have both a language and a datatype")
            lit = unquote(lit)
            return Literal(lit, lang, dtype)
        return False

# # Obsolete, unused
# def parseURI(uri):
#     import urllib
#     parser = NTriplesParser()
#     u = urllib.urlopen(uri)
#     sink = parser.parse(u)
#     u.close()
#     # for triple in sink:
#     #     print triple
#     print 'Length of input:', sink.length
