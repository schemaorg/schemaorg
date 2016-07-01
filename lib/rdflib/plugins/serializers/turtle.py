"""
Turtle RDF graph serializer for RDFLib.
See <http://www.w3.org/TeamSubmission/turtle/> for syntax specification.
"""

from collections import defaultdict

from rdflib.term import BNode, Literal, URIRef
from rdflib.exceptions import Error
from rdflib.serializer import Serializer
from rdflib.namespace import RDF, RDFS

__all__ = ['RecursiveSerializer', 'TurtleSerializer']


class RecursiveSerializer(Serializer):

    topClasses = [RDFS.Class]
    predicateOrder = [RDF.type, RDFS.label]
    maxDepth = 10
    indentString = u"  "

    def __init__(self, store):

        super(RecursiveSerializer, self).__init__(store)
        self.stream = None
        self.reset()

    def addNamespace(self, prefix, uri):
        self.namespaces[prefix] = uri

    def checkSubject(self, subject):
        """Check to see if the subject should be serialized yet"""
        if ((self.isDone(subject))
            or (subject not in self._subjects)
            or ((subject in self._topLevels) and (self.depth > 1))
            or (isinstance(subject, URIRef)
                and (self.depth >= self.maxDepth))):
            return False
        return True

    def isDone(self, subject):
        """Return true if subject is serialized"""
        return subject in self._serialized

    def orderSubjects(self):
        seen = {}
        subjects = []

        for classURI in self.topClasses:
            members = list(self.store.subjects(RDF.type, classURI))
            members.sort()

            for member in members:
                subjects.append(member)
                self._topLevels[member] = True
                seen[member] = True

        recursable = [
            (isinstance(subject, BNode),
             self._references[subject], subject)
            for subject in self._subjects if subject not in seen]

        recursable.sort()
        subjects.extend([subject for (isbnode, refs, subject) in recursable])

        return subjects

    def preprocess(self):
        for triple in self.store.triples((None, None, None)):
            self.preprocessTriple(triple)

    def preprocessTriple(self, (s, p, o)):
        self._references[o]+=1
        self._subjects[s] = True

    def reset(self):
        self.depth = 0
        self.lists = {}
        self.namespaces = {}
        self._references = defaultdict(int)
        self._serialized = {}
        self._subjects = {}
        self._topLevels = {}

        for prefix, ns in self.store.namespaces():
            self.addNamespace(prefix, ns)

    def buildPredicateHash(self, subject):
        """
        Build a hash key by predicate to a list of objects for the given
        subject
        """
        properties = {}
        for s, p, o in self.store.triples((subject, None, None)):
            oList = properties.get(p, [])
            oList.append(o)
            properties[p] = oList
        return properties

    def sortProperties(self, properties):
        """Take a hash from predicate uris to lists of values.
           Sort the lists of values.  Return a sorted list of properties."""
        # Sort object lists
        for prop, objects in properties.items():
            objects.sort()

        # Make sorted list of properties
        propList = []
        seen = {}
        for prop in self.predicateOrder:
            if (prop in properties) and (prop not in seen):
                propList.append(prop)
                seen[prop] = True
        props = properties.keys()
        props.sort()
        for prop in props:
            if prop not in seen:
                propList.append(prop)
                seen[prop] = True
        return propList

    def subjectDone(self, subject):
        """Mark a subject as done."""
        self._serialized[subject] = True

    def indent(self, modifier=0):
        """Returns indent string multiplied by the depth"""
        return (self.depth + modifier) * self.indentString

    def write(self, text):
        """Write text in given encoding."""
        self.stream.write(text.encode(self.encoding, 'replace'))


SUBJECT = 0
VERB = 1
OBJECT = 2

_GEN_QNAME_FOR_DT = False
_SPACIOUS_OUTPUT = False


class TurtleSerializer(RecursiveSerializer):

    short_name = "turtle"
    indentString = '    '

    def __init__(self, store):
        self._ns_rewrite = {}
        super(TurtleSerializer, self).__init__(store)
        self.keywords = {
            RDF.type: 'a'
        }
        self.reset()
        self.stream = None
        self._spacious = _SPACIOUS_OUTPUT

    def addNamespace(self, prefix, namespace):
        # Turtle does not support prefix that start with _
        # if they occur in the graph, rewrite to p_blah
        # this is more complicated since we need to make sure p_blah
        # does not already exist. And we register namespaces as we go, i.e.
        # we may first see a triple with prefix _9 - rewrite it to p_9
        # and then later find a triple with a "real" p_9 prefix

        # so we need to keep track of ns rewrites we made so far.

        if (prefix > '' and prefix[0] == '_') \
                or self.namespaces.get(prefix, namespace) != namespace:

            if prefix not in self._ns_rewrite:
                p = "p" + prefix
                while p in self.namespaces:
                    p = "p" + p
                self._ns_rewrite[prefix] = p

        prefix = self._ns_rewrite.get(prefix, prefix)
        super(TurtleSerializer, self).addNamespace(prefix, namespace)
        return prefix

    def reset(self):
        super(TurtleSerializer, self).reset()
        self._shortNames = {}
        self._started = False
        self._ns_rewrite = {}

    def serialize(self, stream, base=None, encoding=None,
                  spacious=None, **args):
        self.reset()
        self.stream = stream
        self.base = base

        if spacious is not None:
            self._spacious = spacious

        self.preprocess()
        subjects_list = self.orderSubjects()

        self.startDocument()

        firstTime = True
        for subject in subjects_list:
            if self.isDone(subject):
                continue
            if firstTime:
                firstTime = False
            if self.statement(subject) and not firstTime:
                self.write('\n')

        self.endDocument()
        stream.write(u"\n".encode('ascii'))

    def preprocessTriple(self, triple):
        super(TurtleSerializer, self).preprocessTriple(triple)
        for i, node in enumerate(triple):
            if node in self.keywords:
                continue
            # Don't use generated prefixes for subjects and objects
            self.getQName(node, gen_prefix=(i == VERB))
            if isinstance(node, Literal) and node.datatype:
                self.getQName(node.datatype, gen_prefix=_GEN_QNAME_FOR_DT)
        p = triple[1]
        if isinstance(p, BNode): # hmm - when is P ever a bnode?
            self._references[p]+=1

    def getQName(self, uri, gen_prefix=True):
        if not isinstance(uri, URIRef):
            return None

        parts = None

        try:
            parts = self.store.compute_qname(uri, generate=gen_prefix)
        except:

            # is the uri a namespace in itself?
            pfx = self.store.store.prefix(uri)

            if pfx is not None:
                parts = (pfx, uri, '')
            else:
                # nothing worked
                return None

        prefix, namespace, local = parts

        # QName cannot end with .
        if local.endswith("."): return None

        prefix = self.addNamespace(prefix, namespace)

        return u'%s:%s' % (prefix, local)

    def startDocument(self):
        self._started = True
        ns_list = sorted(self.namespaces.items())
        for prefix, uri in ns_list:
            self.write(self.indent() + '@prefix %s: <%s> .\n' % (prefix, uri))
        if ns_list and self._spacious:
            self.write('\n')

    def endDocument(self):
        if self._spacious:
            self.write('\n')

    def statement(self, subject):
        self.subjectDone(subject)
        return self.s_squared(subject) or self.s_default(subject)

    def s_default(self, subject):
        self.write('\n' + self.indent())
        self.path(subject, SUBJECT)
        self.predicateList(subject)
        self.write(' .')
        return True

    def s_squared(self, subject):
        if (self._references[subject] > 0) or not isinstance(subject, BNode):
            return False
        self.write('\n' + self.indent() + '[]')
        self.predicateList(subject)
        self.write(' .')
        return True

    def path(self, node, position, newline=False):
        if not (self.p_squared(node, position, newline)
                or self.p_default(node, position, newline)):
            raise Error("Cannot serialize node '%s'" % (node, ))

    def p_default(self, node, position, newline=False):
        if position != SUBJECT and not newline:
            self.write(' ')
        self.write(self.label(node, position))
        return True

    def label(self, node, position):
        if node == RDF.nil:
            return '()'
        if position is VERB and node in self.keywords:
            return self.keywords[node]
        if isinstance(node, Literal):
            return node._literal_n3(
                use_plain=True,
                qname_callback=lambda dt: self.getQName(
                    dt, _GEN_QNAME_FOR_DT))
        else:
            node = self.relativize(node)

            return self.getQName(node, position == VERB) or node.n3()

    def p_squared(self, node, position, newline=False):
        if (not isinstance(node, BNode)
                or node in self._serialized
                or self._references[node] > 1
                or position == SUBJECT):
            return False

        if not newline:
            self.write(' ')

        if self.isValidList(node):
            # this is a list
            self.write('(')
            self.depth += 1  # 2
            self.doList(node)
            self.depth -= 1  # 2
            self.write(' )')
        else:
            self.subjectDone(node)
            self.depth += 2
            # self.write('[\n' + self.indent())
            self.write('[')
            self.depth -= 1
            # self.predicateList(node, newline=True)
            self.predicateList(node, newline=False)
            # self.write('\n' + self.indent() + ']')
            self.write(' ]')
            self.depth -= 1

        return True

    def isValidList(self, l):
        """
        Checks if l is a valid RDF list, i.e. no nodes have other properties.
        """
        try:
            if not self.store.value(l, RDF.first):
                return False
        except:
            return False
        while l:
            if l != RDF.nil and len(
                    list(self.store.predicate_objects(l))) != 2:
                return False
            l = self.store.value(l, RDF.rest)
        return True

    def doList(self, l):
        while l:
            item = self.store.value(l, RDF.first)
            if item is not None:
                self.path(item, OBJECT)
                self.subjectDone(l)
            l = self.store.value(l, RDF.rest)

    def predicateList(self, subject, newline=False):
        properties = self.buildPredicateHash(subject)
        propList = self.sortProperties(properties)
        if len(propList) == 0:
            return
        self.verb(propList[0], newline=newline)
        self.objectList(properties[propList[0]])
        for predicate in propList[1:]:
            self.write(' ;\n' + self.indent(1))
            self.verb(predicate, newline=True)
            self.objectList(properties[predicate])

    def verb(self, node, newline=False):
        self.path(node, VERB, newline)

    def objectList(self, objects):
        count = len(objects)
        if count == 0:
            return
        depthmod = (count == 1) and 0 or 1
        self.depth += depthmod
        self.path(objects[0], OBJECT)
        for obj in objects[1:]:
            self.write(',\n' + self.indent(1))
            self.path(obj, OBJECT, newline=True)
        self.depth -= depthmod
