"""
TODO:
"""

__all__ = ['Error', 'TypeCheckError', 'SubjectTypeError',
           'PredicateTypeError', 'ObjectTypeError', 'ContextTypeError',
           'ParserError']


class Error(Exception):
    """Base class for rdflib exceptions."""
    def __init__(self, msg=None):
        Exception.__init__(self, msg)
        self.msg = msg


class TypeCheckError(Error):
    """Parts of assertions are subject to type checks."""

    def __init__(self, node):
        Error.__init__(self, node)
        self.type = type(node)
        self.node = node


class SubjectTypeError(TypeCheckError):
    """Subject of an assertion must be an instance of URIRef."""
    def __init__(self, node):
        TypeCheckError.__init__(self, node)
        self.msg = "Subject must be instance of URIRef or BNode: %s(%s)" \
            % (self.node, self.type)


class PredicateTypeError(TypeCheckError):
    """Predicate of an assertion must be an instance of URIRef."""
    def __init__(self, node):
        TypeCheckError.__init__(self, node)
        self.msg = "Predicate must be a URIRef instance: %s(%s)" \
            % (self.node, self.type)


class ObjectTypeError(TypeCheckError):
    """Object of an assertion must be an instance of URIRef, Literal,
    or BNode."""
    def __init__(self, node):
        TypeCheckError.__init__(self, node)
        self.msg = "\
Object must be instance of URIRef, Literal, or BNode: %s(%s)" % \
            (self.node, self.type)


class ContextTypeError(TypeCheckError):
    """Context of an assertion must be an instance of URIRef."""
    def __init__(self, node):
        TypeCheckError.__init__(self, node)
        self.msg = "Context must be instance of URIRef or BNode: %s(%s)" \
            % (self.node, self.type)


class ParserError(Error):
    """RDF Parser error."""
    def __init__(self, msg):
        Error.__init__(self, msg)
        self.msg = msg

    def __str__(self):
        return self.msg


class UniquenessError(Error):
    """A uniqueness assumption was made in the context, and that is not true"""
    def __init__(self, values):
        Error.__init__(self, "\
Uniqueness assumption is not fulfilled. Multiple values are: %s" % values)
