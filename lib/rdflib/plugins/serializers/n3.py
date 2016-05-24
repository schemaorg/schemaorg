"""
Notation 3 (N3) RDF graph serializer for RDFLib.
"""
from rdflib.graph import Graph
from rdflib.namespace import Namespace, OWL
from rdflib.plugins.serializers.turtle import (
    TurtleSerializer, SUBJECT, OBJECT)

__all__ = ['N3Serializer']

SWAP_LOG = Namespace("http://www.w3.org/2000/10/swap/log#")


class N3Serializer(TurtleSerializer):

    short_name = "n3"

    def __init__(self, store, parent=None):
        super(N3Serializer, self).__init__(store)
        self.keywords.update({
            OWL.sameAs: '=',
            SWAP_LOG.implies: '=>'
        })
        self.parent = parent

    def reset(self):
        super(N3Serializer, self).reset()
        self._stores = {}

    def subjectDone(self, subject):
        super(N3Serializer, self).subjectDone(subject)
        if self.parent:
            self.parent.subjectDone(subject)

    def isDone(self, subject):
        return (super(N3Serializer, self).isDone(subject)
                and (not self.parent or self.parent.isDone(subject)))

    def startDocument(self):
        super(N3Serializer, self).startDocument()
        # if not isinstance(self.store, N3Store):
        #    return
        #
        # all_list = [self.label(var) for var in
        #        self.store.get_universals(recurse=False)]
        # all_list.sort()
        # some_list = [self.label(var) for var in
        #        self.store.get_existentials(recurse=False)]
        # some_list.sort()
        #
        # for var in all_list:
        #    self.write('\n'+self.indent()+'@forAll %s. '%var)
        # for var in some_list:
        #    self.write('\n'+self.indent()+'@forSome %s. '%var)
        #
        # if (len(all_list) + len(some_list)) > 0:
        #    self.write('\n')

    def endDocument(self):
        if not self.parent:
            super(N3Serializer, self).endDocument()

    def indent(self, modifier=0):
        indent = super(N3Serializer, self).indent(modifier)
        if self.parent is not None:
            indent += self.parent.indent()  # modifier)
        return indent

    def preprocessTriple(self, triple):
        super(N3Serializer, self).preprocessTriple(triple)
        if isinstance(triple[0], Graph):
            for t in triple[0]:
                self.preprocessTriple(t)
        if isinstance(triple[2], Graph):
            for t in triple[2]:
                self.preprocessTriple(t)

    def getQName(self, uri, gen_prefix=True):
        qname = None
        if self.parent is not None:
            qname = self.parent.getQName(uri, gen_prefix)
        if qname is None:
            qname = super(N3Serializer, self).getQName(uri, gen_prefix)
        return qname

    def statement(self, subject):
        self.subjectDone(subject)
        properties = self.buildPredicateHash(subject)
        if len(properties) == 0:
            return False
        return (self.s_clause(subject)
                or super(N3Serializer, self).statement(subject))

    def path(self, node, position, newline=False):
        if not self.p_clause(node, position):
            super(N3Serializer, self).path(node, position, newline)

    def s_clause(self, subject):
        if isinstance(subject, Graph):
            self.write('\n' + self.indent())
            self.p_clause(subject, SUBJECT)
            self.predicateList(subject)
            self.write(' .')
            return True
        else:
            return False

    def p_clause(self, node, position):
        if isinstance(node, Graph):
            self.subjectDone(node)
            if position is OBJECT:
                self.write(' ')
            self.write('{')
            self.depth += 1
            serializer = N3Serializer(node, parent=self)
            serializer.serialize(self.stream)
            self.depth -= 1
            self.write(self.indent() + '}')
            return True
        else:
            return False
