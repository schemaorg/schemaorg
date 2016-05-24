"""
N-Triples RDF graph serializer for RDFLib.
See <http://www.w3.org/TR/rdf-testcases/#ntriples> for details about the
format.
"""
from rdflib.term import Literal
from rdflib.serializer import Serializer
from rdflib.py3compat import b
import warnings

__all__ = ['NTSerializer']


class NTSerializer(Serializer):
    """
    Serializes RDF graphs to NTriples format.
    """

    def serialize(self, stream, base=None, encoding=None, **args):
        if base is not None:
            warnings.warn("NTSerializer does not support base.")
        if encoding is not None:
            warnings.warn("NTSerializer does not use custom encoding.")
        encoding = self.encoding
        for triple in self.store:
            stream.write(_nt_row(triple).encode(encoding, "replace"))
        stream.write(b("\n"))


def _nt_row(triple):
    if isinstance(triple[2], Literal):
        return u"%s %s %s .\n" % (
            triple[0].n3(),
            triple[1].n3(),
            _xmlcharref_encode(_quoteLiteral(triple[2])))
    else:
        return u"%s %s %s .\n" % (triple[0].n3(),
                                  triple[1].n3(),
                                  _xmlcharref_encode(triple[2].n3()))


def _quoteLiteral(l):
    '''
    a simpler version of term.Literal.n3()
    '''

    encoded = _quote_encode(l)

    if l.language:
        if l.datatype:
            raise Exception("Literal has datatype AND language!")
        return '%s@%s' % (encoded, l.language)
    elif l.datatype:
        return '%s^^<%s>' % (encoded, l.datatype)
    else:
        return '%s' % encoded


def _quote_encode(l):
    return '"%s"' % l.replace('\\', '\\\\')\
        .replace('\n', '\\n')\
        .replace('"', '\\"')\
        .replace('\r', '\\r')


# from <http://code.activestate.com/recipes/303668/>
def _xmlcharref_encode(unicode_data, encoding="ascii"):
    """Emulate Python 2.3's 'xmlcharrefreplace' encoding error handler."""
    res = ""

    # Step through the unicode_data string one character at a time in
    # order to catch unencodable characters:
    for char in unicode_data:
        try:
            char.encode(encoding, 'strict')
        except UnicodeError:
            if ord(char) <= 0xFFFF:
                res += '\\u%04X' % ord(char)
            else:
                res += '\\U%08X' % ord(char)
        else:
            res += char

    return res
