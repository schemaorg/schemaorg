# -*- coding: utf-8 -*-
#
"""
This is an RDFLib store around Ivan Herman et al.'s SPARQL service wrapper.
This was first done in layer-cake, and then ported to RDFLib

"""

# Defines some SPARQL keywords
LIMIT = 'LIMIT'
OFFSET = 'OFFSET'
ORDERBY = 'ORDER BY'

import re
import collections
import urllib2

# import warnings
try:
    from SPARQLWrapper import SPARQLWrapper, XML, POST, GET, URLENCODED, POSTDIRECTLY
except ImportError:
    raise Exception(
        "SPARQLWrapper not found! SPARQL Store will not work." +
        "Install with 'easy_install SPARQLWrapper'")

import sys
if getattr(sys, 'pypy_version_info', None) is not None \
    or sys.platform.startswith('java') \
        or sys.version_info[:2] < (2, 6):
    # import elementtree as etree
    from elementtree import ElementTree
    assert ElementTree
else:
    try:
        from xml.etree import ElementTree
        assert ElementTree
    except ImportError:
        from elementtree import ElementTree

from rdflib.plugins.stores.regexmatching import NATIVE_REGEX

from rdflib.store import Store
from rdflib.query import Result
from rdflib import Variable, Namespace, BNode, URIRef, Literal
from rdflib.graph import DATASET_DEFAULT_GRAPH_ID

import httplib
import urlparse

class NSSPARQLWrapper(SPARQLWrapper):
    nsBindings = {}

    def setNamespaceBindings(self, bindings):
        """
        A shortcut for setting namespace bindings that will be added
        to the prolog of the query

        @param bindings: A dictionary of prefixs to URIs
        """
        self.nsBindings.update(bindings)

    def setQuery(self, query):
        """
        Set the SPARQL query text. Note: no check is done on the
        validity of the query (syntax or otherwise) by this module,
        except for testing the query type (SELECT, ASK, etc).

        Syntax and validity checking is done by the SPARQL service itself.

        @param query: query text
        @type query: string
        @bug: #2320024
        """
        self.queryType = self._parseQueryType(query)
        self.queryString = self.injectPrefixes(query)

    def injectPrefixes(self, query):
        return '\n'.join(
            ['\n'.join(['PREFIX %s: <%s>' % (key, val)
                        for key, val in self.nsBindings.items()]),
             query])

BNODE_IDENT_PATTERN = re.compile('(?P<label>_\:[^\s]+)')
SPARQL_NS = Namespace('http://www.w3.org/2005/sparql-results#')
sparqlNsBindings = {u'sparql': SPARQL_NS}
ElementTree._namespace_map["sparql"] = SPARQL_NS


def TraverseSPARQLResultDOM(doc, asDictionary=False):
    """
    Returns a generator over tuples of results
    """
    # namespace handling in elementtree xpath sub-set is not pretty :(
    vars = [Variable(v.attrib["name"]) for v in doc.findall(
            './{http://www.w3.org/2005/sparql-results#}head/' +
            '{http://www.w3.org/2005/sparql-results#}variable')]
    for result in doc.findall(
            './{http://www.w3.org/2005/sparql-results#}results/' +
            '{http://www.w3.org/2005/sparql-results#}result'):
        currBind = {}
        values = []
        for binding in result.findall(
                '{http://www.w3.org/2005/sparql-results#}binding'):
            varVal = binding.attrib["name"]
            var = Variable(varVal)
            term = CastToTerm(binding.findall('*')[0])
            values.append(term)
            currBind[var] = term
        if asDictionary:
            yield currBind, vars
        else:
            def __locproc(values):
                if len(values) == 1:
                    return values[0]
                else:
                    return tuple(values)
            yield __locproc(values), vars


def localName(qname):
    # wtf - elementtree cant do this for me
    return qname[qname.index("}") + 1:]


def CastToTerm(node):
    """
    Helper function that casts XML node in SPARQL results
    to appropriate rdflib term
    """
    if node.tag == '{%s}bnode' % SPARQL_NS:
        return BNode(node.text)
    elif node.tag == '{%s}uri' % SPARQL_NS:
        return URIRef(node.text)
    elif node.tag == '{%s}literal' % SPARQL_NS:
        value = node.text if node.text is not None else ''
        if 'datatype' in node.attrib:
            dT = URIRef(node.attrib['datatype'])
            return Literal(value, datatype=dT)
        elif '{http://www.w3.org/XML/1998/namespace}lang' in node.attrib:
            return Literal(value, lang=node.attrib[
                "{http://www.w3.org/XML/1998/namespace}lang"])
        else:
            return Literal(value)
    else:
        raise Exception('Unknown answer type')


class SPARQLStore(NSSPARQLWrapper, Store):
    """
    An RDFLib store around a SPARQL endpoint

    This is in theory context-aware and should work as expected
    when a context is specified.

    For ConjunctiveGraphs, reading is done from the "default graph". Exactly
    what this means depends on your endpoint, because SPARQL does not offer a
    simple way to query the union of all graphs as it would be expected for a
    ConjuntiveGraph. This is why we recommend using Dataset instead, which is
    motivated by the SPARQL 1.1.

    Fuseki/TDB has a flag for specifying that the default graph
    is the union of all graphs (tdb:unionDefaultGraph in the Fuseki config).

    .. warning:: The SPARQL Store does not support blank-nodes!

                 As blank-nodes act as variables in SPARQL queries
                 there is no way to query for a particular blank node.

                 See http://www.w3.org/TR/sparql11-query/#BGPsparqlBNodes


    """
    formula_aware = False
    transaction_aware = False
    graph_aware = True
    regex_matching = NATIVE_REGEX

    def __init__(self,
                 endpoint=None, bNodeAsURI=False,
                 sparql11=True, context_aware=True,
                 **sparqlwrapper_kwargs):
        """
        """
        super(SPARQLStore, self).__init__(endpoint, returnFormat=XML, **sparqlwrapper_kwargs)
        self.setUseKeepAlive()
        self.bNodeAsURI = bNodeAsURI
        self.nsBindings = {}
        self.sparql11 = sparql11
        self.context_aware = context_aware
        self.graph_aware = context_aware

    # Database Management Methods
    def create(self, configuration):
        raise TypeError('The SPARQL store is read only')

    def open(self, configuration, create=False):
        """
        sets the endpoint URL for this SPARQLStore
        if create==True an exception is thrown.
        """
        if create:
            raise Exception("Cannot create a SPARQL Endpoint")

        self.query_endpoint = configuration

    def __set_query_endpoint(self, queryEndpoint):
        super(SPARQLStore, self).__init__(queryEndpoint, returnFormat=XML)
        self.endpoint = queryEndpoint

    def __get_query_endpoint(self):
        return self.endpoint

    query_endpoint = property(__get_query_endpoint, __set_query_endpoint)

    def destroy(self, configuration):
        raise TypeError('The SPARQL store is read only')

    # Transactional interfaces
    def commit(self):
        raise TypeError('The SPARQL store is read only')

    def rollback(self):
        raise TypeError('The SPARQL store is read only')

    def add(self, (subject, predicate, obj), context=None, quoted=False):
        raise TypeError('The SPARQL store is read only')

    def addN(self, quads):
        raise TypeError('The SPARQL store is read only')

    def remove(self, (subject, predicate, obj), context):
        raise TypeError('The SPARQL store is read only')

    def query(self, query,
              initNs={},
              initBindings={},
              queryGraph=None,
              DEBUG=False):
        self.debug = DEBUG
        assert isinstance(query, basestring)
        self.setNamespaceBindings(initNs)
        if initBindings:
            if not self.sparql11:
                raise Exception(
                    "initBindings not supported for SPARQL 1.0 Endpoints.")
            v = list(initBindings)

            # VALUES was added to SPARQL 1.1 on 2012/07/24
            query += "\nVALUES ( %s )\n{ ( %s ) }\n"\
                % (" ".join("?" + str(x) for x in v),
                   " ".join(initBindings[x].n3() for x in v))

        self.resetQuery()
        if self._is_contextual(queryGraph):
            self.addDefaultGraph(queryGraph)
        self.setQuery(query)

        return Result.parse(SPARQLWrapper.query(self).response)

    def triples(self, (s, p, o), context=None):
        """
        - tuple **(s, o, p)**
            the triple used as filter for the SPARQL select.
            (None, None, None) means anything.
        - context **context**
            the graph effectively calling this method.

        Returns a tuple of triples executing essentially a SPARQL like
        SELECT ?subj ?pred ?obj WHERE { ?subj ?pred ?obj }

        **context** may include three parameter
        to refine the underlying query:
         * LIMIT: an integer to limit the number of results
         * OFFSET: an integer to enable paging of results
         * ORDERBY: an instance of Variable('s'), Variable('o') or Variable('p')
        or, by default, the first 'None' from the given triple

        .. warning::
        - Using LIMIT or OFFSET automatically include ORDERBY otherwise this is
        because the results are retrieved in a not deterministic way (depends on
        the walking path on the graph)
        - Using OFFSET without defining LIMIT will discard the first OFFSET - 1
        results

        ``
        a_graph.LIMIT = limit
        a_graph.OFFSET = offset
        triple_generator = a_graph.triples(mytriple):
            #do something
        #Removes LIMIT and OFFSET if not required for the next triple() calls
        del a_graph.LIMIT
        del a_graph.OFFSET
        ``
        """

        if ( isinstance(s, BNode) or
             isinstance(p, BNode) or
             isinstance(o, BNode) ):
            raise Exception("SPARQLStore does not support Bnodes! "
                            "See http://www.w3.org/TR/sparql11-query/#BGPsparqlBNodes")

        vars = []
        if not s:
            s = Variable('s')
            vars.append(s)

        if not p:
            p = Variable('p')
            vars.append(p)
        if not o:
            o = Variable('o')
            vars.append(o)

        if vars:
            v = ' '.join([term.n3() for term in vars])
        else:
            v = '*'

        query = "SELECT %s WHERE { %s %s %s }" % \
            (v, s.n3(), p.n3(), o.n3())

        # The ORDER BY is necessary
        if hasattr(context, LIMIT) or hasattr(context, OFFSET) \
            or hasattr(context, ORDERBY):
            var = None
            if isinstance(s, Variable):
                var = s
            elif isinstance(p, Variable):
                var = p
            elif isinstance(o, Variable):
                var = o
            elif hasattr(context, ORDERBY) \
                    and isinstance(getattr(context, ORDERBY), Variable):
                var = getattr(context, ORDERBY)
            query = query + ' %s %s' % (ORDERBY, var.n3())

        try:
            query = query + ' LIMIT %s' % int(getattr(context, LIMIT))
        except (ValueError, TypeError, AttributeError):
            pass
        try:
            query = query + ' OFFSET %s' % int(getattr(context, OFFSET))
        except (ValueError, TypeError, AttributeError):
            pass

        self.resetQuery()
        if self._is_contextual(context):
            self.addDefaultGraph(context.identifier)
        self.setQuery(query)

        doc = ElementTree.parse(SPARQLWrapper.query(self).response)
        # ElementTree.dump(doc)
        for rt, vars in TraverseSPARQLResultDOM(doc, asDictionary=True):
            yield (rt.get(s, s),
                   rt.get(p, p),
                   rt.get(o, o)), None

    def triples_choices(self, (subject, predicate, object_), context=None):
        """
        A variant of triples that can take a list of terms instead of a
        single term in any slot.  Stores can implement this to optimize
        the response time from the import default 'fallback' implementation,
        which will iterate over each term in the list and dispatch to
        triples.
        """
        raise NotImplementedError('Triples choices currently not supported')

    def __len__(self, context=None):
        if not self.sparql11:
            raise NotImplementedError(
                "For performance reasons, this is not" +
                "supported for sparql1.0 endpoints")
        else:
            self.resetQuery()
            q = "SELECT (count(*) as ?c) WHERE {?s ?p ?o .}"
            if self._is_contextual(context):
                self.addDefaultGraph(context.identifier)
            self.setQuery(q)
            doc = ElementTree.parse(SPARQLWrapper.query(self).response)
            rt, vars = iter(
                TraverseSPARQLResultDOM(doc, asDictionary=True)).next()
            return int(rt.get(Variable("c")))

    def contexts(self, triple=None):
        """
        Iterates over results to "SELECT ?NAME { GRAPH ?NAME { ?s ?p ?o } }"
        or "SELECT ?NAME { GRAPH ?NAME {} }" if triple is `None`.

        Returns instances of this store with the SPARQL wrapper
        object updated via addNamedGraph(?NAME).

        This causes a named-graph-uri key / value  pair to be sent over
        the protocol.

        Please note that some SPARQL endpoints are not able to find empty named
        graphs.
        """
        self.resetQuery()

        if triple:
            s, p, o = triple
            params = ((s if s else Variable('s')).n3(),
                      (p if p else Variable('p')).n3(),
                      (o if o else Variable('o')).n3())
            self.setQuery('SELECT ?name WHERE { GRAPH ?name { %s %s %s }}' % params)
        else:
            self.setQuery('SELECT ?name WHERE { GRAPH ?name {} }')

        doc = ElementTree.parse(SPARQLWrapper.query(self).response)

        return (rt.get(Variable("name"))
                for rt, vars in TraverseSPARQLResultDOM(doc, asDictionary=True))

    # Namespace persistence interface implementation
    def bind(self, prefix, namespace):
        self.nsBindings[prefix] = namespace

    def prefix(self, namespace):
        """ """
        return dict(
            [(v, k) for k, v in self.nsBindings.items()]
        ).get(namespace)

    def namespace(self, prefix):
        return self.nsBindings.get(prefix)

    def namespaces(self):
        for prefix, ns in self.nsBindings.items():
            yield prefix, ns

    def add_graph(self, graph):
        raise TypeError('The SPARQL store is read only')

    def remove_graph(self, graph):
        raise TypeError('The SPARQL store is read only')

    def _is_contextual(self, graph):
        """ Returns `True` if the "GRAPH" keyword must appear
        in the final SPARQL query sent to the endpoint.
        """
        if (not self.context_aware) or (graph is None):
            return False
        if isinstance(graph, basestring):
            return graph != '__UNION__'
        else:
            return graph.identifier != DATASET_DEFAULT_GRAPH_ID


class SPARQLUpdateStore(SPARQLStore):
    """A store using SPARQL queries for reading and SPARQL Update for changes.

    This can be context-aware, if so, any changes will be to the given named
    graph only.

    In favor of the SPARQL 1.1 motivated Dataset, we advise against using this
    with ConjunctiveGraphs, as it reads and writes from and to the
    "default graph". Exactly what this means depends on the endpoint and can
    result in confusion.

    For Graph objects, everything works as expected.

    .. warning:: The SPARQL Update Store does not support blank-nodes!

                 As blank-nodes acts as variables in SPARQL queries
                 there is no way to query for a particular blank node.

                 See http://www.w3.org/TR/sparql11-query/#BGPsparqlBNodes



    """

    where_pattern = re.compile(r"""(?P<where>WHERE\s*{)""", re.IGNORECASE)

    ##################################################################
    ### Regex for injecting GRAPH blocks into updates on a context ###
    ##################################################################

    # Observations on the SPARQL grammar (http://www.w3.org/TR/2013/REC-sparql11-query-20130321/):
    # 1. Only the terminals STRING_LITERAL1, STRING_LITERAL2,
    #    STRING_LITERAL_LONG1, STRING_LITERAL_LONG2, and comments can contain
    #    curly braces.
    # 2. The non-terminals introduce curly braces in pairs only.
    # 3. Unescaped " can occur only in strings and comments.
    # 3. Unescaped ' can occur only in strings, comments, and IRIRefs.
    # 4. \ always escapes the following character, especially \", \', and
    #    \\ denote literal ", ', and \ respectively.
    # 5. # always starts a comment outside of string and IRI
    # 6. A comment ends at the next newline
    # 7. IRIREFs need to be detected, as they may contain # without starting a comment
    # 8. PrefixedNames do not contain a #
    # As a consequence, it should be rather easy to detect strings and comments
    # in order to avoid unbalanced curly braces.

    # From the SPARQL grammar
    STRING_LITERAL1 = ur"'([^'\\]|\\.)*'"
    STRING_LITERAL2 = ur'"([^"\\]|\\.)*"'
    STRING_LITERAL_LONG1 = ur"'''(('|'')?([^'\\]|\\.))*'''"
    STRING_LITERAL_LONG2 = ur'"""(("|"")?([^"\\]|\\.))*"""'
    String = u'(%s)|(%s)|(%s)|(%s)' % (STRING_LITERAL1, STRING_LITERAL2, STRING_LITERAL_LONG1, STRING_LITERAL_LONG2)
    IRIREF = ur'<([^<>"{}|^`\]\\\[\x00-\x20])*>'
    COMMENT = ur'#[^\x0D\x0A]*([\x0D\x0A]|\Z)'

    # Simplified grammar to find { at beginning and } at end of blocks
    BLOCK_START = u'{'
    BLOCK_END = u'}'
    ESCAPED = ur'\\.'

    # Match anything that doesn't start or end a block:
    BlockContent = u'(%s)|(%s)|(%s)|(%s)' % (String, IRIREF, COMMENT, ESCAPED)
    BlockFinding = u'(?P<block_start>%s)|(?P<block_end>%s)|(?P<block_content>%s)' % (BLOCK_START, BLOCK_END, BlockContent)
    BLOCK_FINDING_PATTERN = re.compile(BlockFinding)

    # Note that BLOCK_FINDING_PATTERN.finditer() will not cover the whole
    # string with matches. Everything that is not matched will have to be
    # part of the modified query as is.

    ##################################################################


    def __init__(self,
                 queryEndpoint=None, update_endpoint=None,
                 bNodeAsURI=False, sparql11=True,
                 context_aware=True,
                 postAsEncoded=True, autocommit=True):

        SPARQLStore.__init__(self,
                             queryEndpoint, bNodeAsURI, sparql11, context_aware, updateEndpoint=update_endpoint)

        self.postAsEncoded = postAsEncoded
        self.autocommit = autocommit
        self._edits = None

    def query(self,*args, **kwargs):
        if not self.autocommit:
            self.commit()
        return SPARQLStore.query(self,*args, **kwargs)
	
    def triples(self,*args, **kwargs):
        if not self.autocommit:
            self.commit()
        return SPARQLStore.triples(self,*args, **kwargs)
	
    def contexts(self,*args, **kwargs):
        if not self.autocommit:
            self.commit()
        return SPARQLStore.contexts(self,*args, **kwargs)
	
    def __len__(self,*args, **kwargs):
        if not self.autocommit:
            self.commit()
        return SPARQLStore.__len__(self,*args, **kwargs)

    def open(self, configuration, create=False):
        """
        sets the endpoint URLs for this SPARQLStore
        :param configuration: either a tuple of (queryEndpoint, update_endpoint),
            or a string with the query endpoint
        :param create: if True an exception is thrown.
        """

        if create:
            raise Exception("Cannot create a SPARQL Endpoint")

        if isinstance(configuration, tuple):
            self.endpoint = configuration[0]
            if len(configuration) > 1:
                self.updateEndpoint = configuration[1]
        else:
            self.endpoint = configuration

        if not self.updateEndpoint:
            self.updateEndpoint = self.endpoint

    def _transaction(self):
        if self._edits == None:
            self._edits = []
        return self._edits

    def __set_update_endpoint(self, update_endpoint):
        self.updateEndpoint = update_endpoint

    def __get_update_endpoint(self):
        return self.updateEndpoint

    update_endpoint = property(
        __get_update_endpoint,
        __set_update_endpoint,
        doc='the HTTP URL for the Update endpoint, typically' +
            'something like http://server/dataset/update')

    # Transactional interfaces
    def commit(self):
        """ add(), addN(), and remove() are transactional to reduce overhead of many small edits. 
            Read and update() calls will automatically commit any outstanding edits. 
            This should behave as expected most of the time, except that alternating writes 
            and reads can degenerate to the original call-per-triple situation that originally existed.
        """
        if self._edits and len(self._edits) > 0:
            r = self._do_update('\n;\n'.join(self._edits))
            self._edits = None
            return r

    def rollback(self):
        self._edits = None

    def add(self, spo, context=None, quoted=False):
        """ Add a triple to the store of triples. """

        if not self.endpoint:
            raise Exception("UpdateEndpoint is not set - call 'open'")

        assert not quoted
        (subject, predicate, obj) = spo

        if ( isinstance(subject, BNode) or
             isinstance(predicate, BNode) or
             isinstance(obj, BNode) ):
            raise Exception("SPARQLStore does not support Bnodes! "
                            "See http://www.w3.org/TR/sparql11-query/#BGPsparqlBNodes")


        triple = "%s %s %s ." % (subject.n3(), predicate.n3(), obj.n3())
        if self._is_contextual(context):
            q = "INSERT DATA { GRAPH %s { %s } }" % (
                context.identifier.n3(), triple)
        else:
            q = "INSERT DATA { %s }" % triple
        self._transaction().append(q)
        if self.autocommit:
            self.commit()

    def addN(self, quads):
        """ Add a list of quads to the store. """
        if not self.endpoint:
            raise Exception("UpdateEndpoint is not set - call 'open'")

        contexts = collections.defaultdict(list)
        for subject, predicate, obj, context in quads:
            contexts[context].append((subject,predicate,obj))
        data = []
        for context in contexts:
            triples = ["%s %s %s ." % (x[0].n3(), x[1].n3(), x[2].n3()) for x in contexts[context]]
            data.append("INSERT DATA { GRAPH <%s> { %s } }\n" % (context.identifier, '\n'.join(triples)))
        self._transaction().extend(data)
        if self.autocommit:
            self.commit()

    def remove(self, spo, context):
        """ Remove a triple from the store """
        if not self.endpoint:
            raise Exception("UpdateEndpoint is not set - call 'open'")

        (subject, predicate, obj) = spo
        if not subject:
            subject = Variable("S")
        if not predicate:
            predicate = Variable("P")
        if not obj:
            obj = Variable("O")

        triple = "%s %s %s ." % (subject.n3(), predicate.n3(), obj.n3())
        if self._is_contextual(context):
            q = "DELETE { GRAPH %s { %s } } WHERE { GRAPH %s { %s } }" % (
                context.identifier.n3(), triple,
                context.identifier.n3(), triple)
        else:
            q = "DELETE { %s } WHERE { %s } " % (triple, triple)
        self._transaction().append(q)
        if self.autocommit:
            self.commit()

    def _do_update(self, update):
        self.resetQuery()
        self.setQuery(update)
        self.setMethod(POST)
        self.setRequestMethod(URLENCODED if self.postAsEncoded else POSTDIRECTLY)

        result = SPARQLWrapper.query(self)
        return result

    def update(self, query,
               initNs={},
               initBindings={},
               queryGraph=None,
               DEBUG=False):
        """
        Perform a SPARQL Update Query against the endpoint,
        INSERT, LOAD, DELETE etc.
        Setting initNs adds PREFIX declarations to the beginning of
        the update. Setting initBindings adds inline VALUEs to the
        beginning of every WHERE clause. By the SPARQL grammar, all
        operations that support variables (namely INSERT and DELETE)
        require a WHERE clause.
        Important: initBindings fails if the update contains the
        substring 'WHERE {' which does not denote a WHERE clause, e.g.
        if it is part of a literal.

        .. admonition:: Context-aware query rewriting

            - **When:**  If context-awareness is enabled and the graph is not the default graph of the store.
            - **Why:** To ensure consistency with the :class:`~rdflib.plugins.memory.IOMemory` store.
              The graph must except "local" SPARQL requests (requests with no GRAPH keyword)
              like if it was the default graph.
            - **What is done:** These "local" queries are rewritten by this store.
              The content of each block of a SPARQL Update operation is wrapped in a GRAPH block
              except if the block is empty.
              This basically causes INSERT, INSERT DATA, DELETE, DELETE DATA and WHERE to operate
              only on the context.
            - **Example:** `"INSERT DATA { <urn:michel> <urn:likes> <urn:pizza> }"` is converted into
              `"INSERT DATA { GRAPH <urn:graph> { <urn:michel> <urn:likes> <urn:pizza> } }"`.
            - **Warning:** Queries are presumed to be "local" but this assumption is **not checked**.
              For instance, if the query already contains GRAPH blocks, the latter will be wrapped in new GRAPH blocks.
            - **Warning:** A simplified grammar is used that should tolerate
              extensions of the SPARQL grammar. Still, the process may fail in
              uncommon situations and produce invalid output.

        """
        if not self.endpoint:
            raise Exception("UpdateEndpoint is not set - call 'open'")

        self.debug = DEBUG
        assert isinstance(query, basestring)
        self.setNamespaceBindings(initNs)
        query = self.injectPrefixes(query)

        if self._is_contextual(queryGraph):
            query = self._insert_named_graph(query, queryGraph)

        if initBindings:
            # For INSERT and DELETE the WHERE clause is obligatory
            # (http://www.w3.org/TR/2013/REC-sparql11-query-20130321/#rModify)
            # Other query types do not allow variables and don't
            # have a WHERE clause.  This also works for updates with
            # more than one INSERT/DELETE.
            v = list(initBindings)
            values = "\nVALUES ( %s )\n{ ( %s ) }\n"\
                % (" ".join("?" + str(x) for x in v),
                   " ".join(initBindings[x].n3() for x in v))

            query = self.where_pattern.sub("WHERE { " + values, query)

        self._transaction().append(query)
        if self.autocommit:
            self.commit()

    def _insert_named_graph(self, query, query_graph):
        """
            Inserts GRAPH <query_graph> {} into blocks of SPARQL Update operations

            For instance,  "INSERT DATA { <urn:michel> <urn:likes> <urn:pizza> }"
            is converted into
            "INSERT DATA { GRAPH <urn:graph> { <urn:michel> <urn:likes> <urn:pizza> } }"
        """
        graph_block_open = " GRAPH <%s> {" % query_graph
        graph_block_close = "} "

        # SPARQL Update supports the following operations:
        # LOAD, CLEAR, DROP, ADD, MOVE, COPY, CREATE, INSERT DATA, DELETE DATA, DELETE/INSERT, DELETE WHERE
        # LOAD, CLEAR, DROP, ADD, MOVE, COPY, CREATE do not make much sense in a context.
        # INSERT DATA, DELETE DATA, and DELETE WHERE require the contents of their block to be wrapped in a GRAPH <?> { }.
        # DELETE/INSERT supports the WITH keyword, which sets the graph to be
        # used for all following DELETE/INSERT instruction including the
        # non-optional WHERE block. Equivalently, a GRAPH block can be added to
        # all blocks.
        #
        # Strategy employed here: Wrap the contents of every top-level block into a `GRAPH <?> { }`.

        level = 0
        modified_query = []
        pos = 0
        for match in self.BLOCK_FINDING_PATTERN.finditer(query):
            if match.group('block_start') is not None:
                level += 1
                if level == 1:
                    modified_query.append(query[pos:match.end()])
                    modified_query.append(graph_block_open)
                    pos = match.end()
            elif match.group('block_end') is not None:
                if level == 1:
                    since_previous_pos = query[pos:match.start()]
                    if modified_query[-1] is graph_block_open and (since_previous_pos == "" or since_previous_pos.isspace()):
                        # In this case, adding graph_block_start and
                        # graph_block_end results in an empty GRAPH block. Some
                        # enpoints (e.g. TDB) can not handle this. Therefore
                        # remove the previously added block_start.
                        modified_query.pop()
                        modified_query.append(since_previous_pos)
                    else:
                        modified_query.append(since_previous_pos)
                        modified_query.append(graph_block_close)
                    pos = match.start()
                level -= 1
        modified_query.append(query[pos:])

        return "".join(modified_query)

    def add_graph(self, graph):
        if not self.graph_aware:
            Store.add_graph(self, graph)
        elif graph.identifier != DATASET_DEFAULT_GRAPH_ID:
            self.update("CREATE GRAPH <%s>" % graph.identifier)

    def remove_graph(self, graph):
        if not self.graph_aware:
            Store.remove_graph(self, graph)
        elif graph.identifier == DATASET_DEFAULT_GRAPH_ID:
            self.update("DROP DEFAULT")
        else:
            self.update("DROP GRAPH <%s>" % graph.identifier)
