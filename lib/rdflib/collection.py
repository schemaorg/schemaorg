from rdflib.namespace import RDF
from rdflib.term import BNode
from rdflib.term import Literal
from rdflib.graph import Graph
from rdflib.py3compat import format_doctest_out

__all__ = ['Collection']


class Collection(object):
    __doc__ = format_doctest_out("""
    See 3.3.5 Emulating container types:
    http://docs.python.org/ref/sequence-types.html#l2h-232

    >>> from rdflib.graph import Graph
    >>> from pprint import pprint
    >>> listName = BNode()
    >>> g = Graph('IOMemory')
    >>> listItem1 = BNode()
    >>> listItem2 = BNode()
    >>> g.add((listName, RDF.first, Literal(1)))
    >>> g.add((listName, RDF.rest, listItem1))
    >>> g.add((listItem1, RDF.first, Literal(2)))
    >>> g.add((listItem1, RDF.rest, listItem2))
    >>> g.add((listItem2, RDF.rest, RDF.nil))
    >>> g.add((listItem2, RDF.first, Literal(3)))
    >>> c = Collection(g,listName)
    >>> pprint([term.n3() for term in c])
    [%(u)s'"1"^^<http://www.w3.org/2001/XMLSchema#integer>',
     %(u)s'"2"^^<http://www.w3.org/2001/XMLSchema#integer>',
     %(u)s'"3"^^<http://www.w3.org/2001/XMLSchema#integer>']

    >>> Literal(1) in c
    True
    >>> len(c)
    3
    >>> c._get_container(1) == listItem1
    True
    >>> c.index(Literal(2)) == 1
    True
    """)

    def __init__(self, graph, uri, seq=[]):
        self.graph = graph
        self.uri = uri or BNode()
        for item in seq:
            self.append(item)

    def n3(self):
        """
        >>> from rdflib.graph import Graph
        >>> listName = BNode()
        >>> g = Graph('IOMemory')
        >>> listItem1 = BNode()
        >>> listItem2 = BNode()
        >>> g.add((listName, RDF.first, Literal(1)))
        >>> g.add((listName, RDF.rest, listItem1))
        >>> g.add((listItem1, RDF.first, Literal(2)))
        >>> g.add((listItem1, RDF.rest, listItem2))
        >>> g.add((listItem2, RDF.rest, RDF.nil))
        >>> g.add((listItem2, RDF.first, Literal(3)))
        >>> c = Collection(g, listName)
        >>> print(c.n3()) #doctest: +NORMALIZE_WHITESPACE
        ( "1"^^<http://www.w3.org/2001/XMLSchema#integer>
          "2"^^<http://www.w3.org/2001/XMLSchema#integer>
          "3"^^<http://www.w3.org/2001/XMLSchema#integer> )
        """
        return "( %s )" % (' '.join([i.n3() for i in self]))

    def _get_container(self, index):
        """Gets the first, rest holding node at index."""
        assert isinstance(index, int)
        graph = self.graph
        container = self.uri
        i = 0
        while i < index:
            i += 1
            container = graph.value(container, RDF.rest)
            if container is None:
                break
        return container

    def __len__(self):
        """length of items in collection."""
        count = 0
        links = set()
        for item in self.graph.items(self.uri):
            assert item not in links, \
                "There is a loop in the RDF list! " + \
                "(%s has been processed before)" % item
            links.add(item)
            count += 1
        return count

    def index(self, item):
        """
        Returns the 0-based numerical index of the item in the list
        """
        listName = self.uri
        index = 0
        while True:
            if (listName, RDF.first, item) in self.graph:
                return index
            else:
                newLink = list(self.graph.objects(listName, RDF.rest))
                index += 1
                if newLink == [RDF.nil]:
                    raise ValueError("%s is not in %s" % (item, self.uri))
                elif not newLink:
                    raise Exception("Malformed RDF Collection: %s" % self.uri)
                else:
                    assert len(newLink) == 1, \
                        "Malformed RDF Collection: %s" % self.uri
                    listName = newLink[0]

    def __getitem__(self, key):
        """TODO"""
        c = self._get_container(key)
        if c:
            v = self.graph.value(c, RDF.first)
            if v:
                return v
            else:
                raise KeyError(key)
        else:
            raise IndexError(key)

    def __setitem__(self, key, value):
        """TODO"""
        c = self._get_container(key)
        if c:
            self.graph.add((c, RDF.first, value))
        else:
            raise IndexError(key)

    def __delitem__(self, key):
        """
        >>> from rdflib.namespace import RDF, RDFS
        >>> from rdflib import Graph
        >>> from pprint import pformat
        >>> g = Graph()
        >>> a = BNode('foo')
        >>> b = BNode('bar')
        >>> c = BNode('baz')
        >>> g.add((a, RDF.first, RDF.type))
        >>> g.add((a, RDF.rest, b))
        >>> g.add((b, RDF.first, RDFS.label))
        >>> g.add((b, RDF.rest, c))
        >>> g.add((c, RDF.first, RDFS.comment))
        >>> g.add((c, RDF.rest, RDF.nil))
        >>> len(g)
        6
        >>> def listAncestry(node, graph):
        ...   for i in graph.subjects(RDF.rest, node):
        ...     yield i
        >>> [str(node.n3())
        ...   for node in g.transitiveClosure(listAncestry, RDF.nil)]
        ['_:baz', '_:bar', '_:foo']
        >>> lst = Collection(g, a)
        >>> len(lst)
        3
        >>> b == lst._get_container(1)
        True
        >>> c == lst._get_container(2)
        True
        >>> del lst[1]
        >>> len(lst)
        2
        >>> len(g)
        4

        """
        self[key]  # to raise any potential key exceptions
        graph = self.graph
        current = self._get_container(key)
        assert current
        if len(self) == 1 and key > 0:
            pass
        elif key == len(self) - 1:
            # the tail
            priorLink = self._get_container(key - 1)
            self.graph.set((priorLink, RDF.rest, RDF.nil))
            graph.remove((current, None, None))
        else:
            next = self._get_container(key + 1)
            prior = self._get_container(key - 1)
            assert next and prior
            graph.remove((current, None, None))
            graph.set((prior, RDF.rest, next))

    def __iter__(self):
        """Iterator over items in Collections"""
        return self.graph.items(self.uri)

    def append(self, item):
        """
        >>> from rdflib.graph import Graph
        >>> listName = BNode()
        >>> g = Graph()
        >>> c = Collection(g,listName,[Literal(1),Literal(2)])
        >>> links = [
        ...     list(g.subjects(object=i, predicate=RDF.first))[0] for i in c]
        >>> len([i for i in links if (i,RDF.rest, RDF.nil) in g])
        1

        """
        container = self.uri
        graph = self.graph
        # iterate to the end of the linked list
        rest = graph.value(container, RDF.rest)
        while rest:
            if rest == RDF.nil:
                # the end, append to the end of the linked list
                node = BNode()
                graph.set((container, RDF.rest, node))
                container = node
                break
            else:
                # move down one link
                if container != self.uri:
                    rest = graph.value(rest, RDF.rest)
                if not rest == RDF.nil:
                    container = rest
        graph.add((container, RDF.first, item))
        graph.add((container, RDF.rest, RDF.nil))

    def clear(self):
        container = self.uri
        graph = self.graph
        while container:
            rest = graph.value(container, RDF.rest)
            graph.remove((container, RDF.first, None))
            graph.remove((container, RDF.rest, None))
            container = rest


def test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    test()

    g = Graph()

    c = Collection(g, BNode())

    assert len(c) == 0

    c = Collection(
        g, BNode(), [Literal("1"), Literal("2"), Literal("3"), Literal("4")])

    assert len(c) == 4

    assert c[1] == Literal("2"), c[1]

    del c[1]

    assert list(c) == [Literal("1"), Literal("3"), Literal("4")], list(c)

    try:
        del c[500]
    except IndexError, i:
        pass

    c.append(Literal("5"))

    print(list(c))

    for i in c:
        print(i)

    del c[3]

    c.clear()

    assert len(c) == 0
