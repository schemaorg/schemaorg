from rdflib.plugins.serializers.xmlwriter import XMLWriter

from rdflib.namespace import Namespace, RDF, RDFS  # , split_uri

from rdflib.term import URIRef, Literal, BNode
from rdflib.util import first, more_than
from rdflib.collection import Collection
from rdflib.serializer import Serializer

# from rdflib.exceptions import Error

from rdflib.py3compat import b

from xml.sax.saxutils import quoteattr, escape
import xml.dom.minidom

from xmlwriter import ESCAPE_ENTITIES

__all__ = ['fix', 'XMLSerializer', 'PrettyXMLSerializer']


class XMLSerializer(Serializer):

    def __init__(self, store):
        super(XMLSerializer, self).__init__(store)

    def __bindings(self):
        store = self.store
        nm = store.namespace_manager
        bindings = {}

        for predicate in set(store.predicates()):
            prefix, namespace, name = nm.compute_qname(predicate)
            bindings[prefix] = URIRef(namespace)

        RDFNS = URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#")

        if "rdf" in bindings:
            assert bindings["rdf"] == RDFNS
        else:
            bindings["rdf"] = RDFNS

        for prefix, namespace in bindings.iteritems():
            yield prefix, namespace

    def serialize(self, stream, base=None, encoding=None, **args):
        self.base = base
        self.__stream = stream
        self.__serialized = {}
        encoding = self.encoding
        self.write = write = lambda uni: stream.write(
            uni.encode(encoding, 'replace'))

        # startDocument
        write('<?xml version="1.0" encoding="%s"?>\n' % self.encoding)

        # startRDF
        write('<rdf:RDF\n')

        # If provided, write xml:base attribute for the RDF
        if "xml_base" in args:
            write('   xml:base="%s"\n' % args['xml_base'])
        # TODO:
        # assert(
        #    namespaces["http://www.w3.org/1999/02/22-rdf-syntax-ns#"]=='rdf')
        bindings = list(self.__bindings())
        bindings.sort()

        for prefix, namespace in bindings:
            if prefix:
                write('   xmlns:%s="%s"\n' % (prefix, namespace))
            else:
                write('   xmlns="%s"\n' % namespace)
        write('>\n')

        # write out triples by subject
        for subject in self.store.subjects():
            self.subject(subject, 1)

        # endRDF
        write("</rdf:RDF>\n")

        # Set to None so that the memory can get garbage collected.
        # self.__serialized = None
        del self.__serialized

    def subject(self, subject, depth=1):
        if not subject in self.__serialized:
            self.__serialized[subject] = 1

            if isinstance(subject, (BNode, URIRef)):
                write = self.write
                indent = "  " * depth
                element_name = "rdf:Description"

                if isinstance(subject, BNode):
                    write('%s<%s rdf:nodeID="%s"' % (
                        indent, element_name, subject))
                else:
                    uri = quoteattr(self.relativize(subject))
                    write("%s<%s rdf:about=%s" % (indent, element_name, uri))

                if (subject, None, None) in self.store:
                    write(">\n")

                    for predicate, object in self.store.predicate_objects(
                            subject):
                        self.predicate(predicate, object, depth + 1)
                    write("%s</%s>\n" % (indent, element_name))

                else:
                    write("/>\n")

    def predicate(self, predicate, object, depth=1):
        write = self.write
        indent = "  " * depth
        qname = self.store.namespace_manager.qname(predicate)

        if isinstance(object, Literal):
            attributes = ""

            if object.language:
                attributes += ' xml:lang="%s"' % object.language

            if object.datatype:
                attributes += ' rdf:datatype="%s"' % object.datatype

            write("%s<%s%s>%s</%s>\n" %
                  (indent, qname, attributes,
                   escape(object, ESCAPE_ENTITIES), qname))
        else:

            if isinstance(object, BNode):
                write('%s<%s rdf:nodeID="%s"/>\n' %
                      (indent, qname, object))
            else:
                write("%s<%s rdf:resource=%s/>\n" %
                      (indent, qname, quoteattr(self.relativize(object))))

XMLLANG = "http://www.w3.org/XML/1998/namespacelang"
XMLBASE = "http://www.w3.org/XML/1998/namespacebase"
OWL_NS = Namespace('http://www.w3.org/2002/07/owl#')


# TODO:
def fix(val):
    "strip off _: from nodeIDs... as they are not valid NCNames"
    if val.startswith("_:"):
        return val[2:]
    else:
        return val


class PrettyXMLSerializer(Serializer):

    def __init__(self, store, max_depth=3):
        super(PrettyXMLSerializer, self).__init__(store)
        self.forceRDFAbout = set()

    def serialize(self, stream, base=None, encoding=None, **args):
        self.__serialized = {}
        store = self.store
        self.base = base
        self.max_depth = args.get("max_depth", 3)
        assert self.max_depth > 0, "max_depth must be greater than 0"

        self.nm = nm = store.namespace_manager
        self.writer = writer = XMLWriter(stream, nm, encoding)
        namespaces = {}

        possible = set(store.predicates()).union(
            store.objects(None, RDF.type))

        for predicate in possible:
            prefix, namespace, local = nm.compute_qname(predicate)
            namespaces[prefix] = namespace

        namespaces["rdf"] = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"

        writer.push(RDF.RDF)

        if "xml_base" in args:
            writer.attribute(XMLBASE, args["xml_base"])

        writer.namespaces(namespaces.iteritems())

        # Write out subjects that can not be inline
        for subject in store.subjects():
            if (None, None, subject) in store:
                if (subject, None, subject) in store:
                    self.subject(subject, 1)
            else:
                self.subject(subject, 1)

        # write out anything that has not yet been reached
        # write out BNodes last (to ensure they can be inlined where possible)
        bnodes = set()

        for subject in store.subjects():
            if isinstance(subject, BNode):
                bnodes.add(subject)
                continue
            self.subject(subject, 1)

        # now serialize only those BNodes that have not been serialized yet
        for bnode in bnodes:
            if bnode not in self.__serialized:
                self.subject(subject, 1)

        writer.pop(RDF.RDF)
        stream.write(b("\n"))

        # Set to None so that the memory can get garbage collected.
        self.__serialized = None

    def subject(self, subject, depth=1):
        store = self.store
        writer = self.writer

        if subject in self.forceRDFAbout:
            writer.push(RDF.Description)
            writer.attribute(RDF.about, self.relativize(subject))
            writer.pop(RDF.Description)
            self.forceRDFAbout.remove(subject)

        elif not subject in self.__serialized:
            self.__serialized[subject] = 1
            type = first(store.objects(subject, RDF.type))

            try:
                self.nm.qname(type)
            except:
                type = None

            element = type or RDF.Description
            writer.push(element)

            if isinstance(subject, BNode):
                def subj_as_obj_more_than(ceil):
                    return True
                    # more_than(store.triples((None, None, subject)), ceil)

                # here we only include BNode labels if they are referenced
                # more than once (this reduces the use of redundant BNode
                # identifiers)
                if subj_as_obj_more_than(1):
                    writer.attribute(RDF.nodeID, fix(subject))

            else:
                writer.attribute(RDF.about, self.relativize(subject))

            if (subject, None, None) in store:
                for predicate, object in store.predicate_objects(subject):
                    if not (predicate == RDF.type and object == type):
                        self.predicate(predicate, object, depth + 1)

            writer.pop(element)

        elif subject in self.forceRDFAbout:
            writer.push(RDF.Description)
            writer.attribute(RDF.about, self.relativize(subject))
            writer.pop(RDF.Description)
            self.forceRDFAbout.remove(subject)

    def predicate(self, predicate, object, depth=1):
        writer = self.writer
        store = self.store
        writer.push(predicate)

        if isinstance(object, Literal):
            if object.language:
                writer.attribute(XMLLANG, object.language)

            if (object.datatype == RDF.XMLLiteral and
                    isinstance(object.value, xml.dom.minidom.Document)):
                writer.attribute(RDF.parseType, "Literal")
                writer.text(u"")
                writer.stream.write(object)
            else:
                if object.datatype:
                    writer.attribute(RDF.datatype, object.datatype)
                writer.text(object)

        elif object in self.__serialized or not (object, None, None) in store:

            if isinstance(object, BNode):
                if more_than(store.triples((None, None, object)), 0):
                    writer.attribute(RDF.nodeID, fix(object))
            else:
                writer.attribute(RDF.resource, self.relativize(object))

        else:
            if first(store.objects(object, RDF.first)):  # may not have type
                                                         # RDF.List

                self.__serialized[object] = 1

                # Warn that any assertions on object other than
                # RDF.first and RDF.rest are ignored... including RDF.List
                import warnings
                warnings.warn(
                    "Assertions on %s other than RDF.first " % repr(object) +
                    "and RDF.rest are ignored ... including RDF.List",
                    UserWarning, stacklevel=2)
                writer.attribute(RDF.parseType, "Collection")

                col = Collection(store, object)

                for item in col:

                    if isinstance(item, URIRef):
                        self.forceRDFAbout.add(item)
                    self.subject(item)

                    if not isinstance(item, URIRef):
                        self.__serialized[item] = 1
            else:
                if first(store.triples_choices(
                    (object, RDF.type, [OWL_NS.Class, RDFS.Class]))) \
                        and isinstance(object, URIRef):
                    writer.attribute(RDF.resource, self.relativize(object))

                elif depth <= self.max_depth:
                    self.subject(object, depth + 1)

                elif isinstance(object, BNode):

                    if not object in self.__serialized \
                            and (object, None, None) in store \
                            and len(list(store.subjects(object=object))) == 1:
                        # inline blank nodes if they haven't been serialized yet
                        # and are only referenced once (regardless of depth)
                        self.subject(object, depth + 1)
                    else:
                        writer.attribute(RDF.nodeID, fix(object))

                else:
                    writer.attribute(RDF.resource, self.relativize(object))

        writer.pop(predicate)
