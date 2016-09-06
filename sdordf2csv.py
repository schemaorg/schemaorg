import csv
import rdflib
from rdflib.namespace import RDFS, RDF, OWL
from rdflib.term import URIRef
import threading

from apimarkdown import Markdown
from apirdflib import RDFLIBLOCK

import logging
logging.basicConfig(level=logging.INFO) # dev_appserver.py --log_level debug .
log = logging.getLogger(__name__)

class sdordf2csv():
    
    def __init__(self, queryGraph=None, fullGraph=None, markdownComments=True,excludeAttic=False):
        self.setqueryGraph(queryGraph) 
        self.setfullGraph(fullGraph)
        self.setexcludeAttic(excludeAttic)
        self.setmarkdownComments(markdownComments)
    
    def setqueryGraph(self,graph=None):
        self.queryGraph = graph
    
    def setfullGraph(self,graph=None):
        self.fullGraph = graph
        
    def setexcludeAttic(self,state):
        self.excludeAttic = state
        
    def setmarkdownComments(self,state):
        self.markdown = state
        
    def doQuery(self,graph=None,query=None):
        res = None
        try:
            RDFLIBLOCK.acquire()
            res = list(graph.query(query))
        finally:
            RDFLIBLOCK.release()
        return res    

    def outputCSVtypes(self,file):
        atticfilter = ""
        if self.excludeAttic:
            atticfilter = "FILTER NOT EXISTS {?term schema:isPartOf <http://attic.schema.org>}."
        query= ('''select ?term where { 
           ?term a rdfs:Class.
           BIND(STR(?term) AS ?strVal)
           FILTER(STRLEN(?strVal) >= 18 && SUBSTR(?strVal, 1, 18) = "http://schema.org/")
           %s
        }
        ORDER BY ?term
         ''') % atticfilter
        try:
            RDFLIBLOCK.acquire()
            types = list(self.queryGraph.query(query))
        finally:
            RDFLIBLOCK.release()
        #log.info( "Types: %s" % len(types))
        self.type2CSV(header=True,out=file)
        for t in types:
            self.type2CSV(term=t.term,header=False,out=file,graph=self.queryGraph)
        
    def outputCSVproperties(self,file):
        atticfilter = ""
        if self.excludeAttic:
            atticfilter = "FILTER NOT EXISTS {?term schema:isPartOf <http://attic.schema.org>}."
        query= ('''select ?term where { 
           ?term a rdf:Property.
           FILTER EXISTS {?term rdfs:label ?l}.
           BIND(STR(?term) AS ?strVal).
           FILTER(STRLEN(?strVal) >= 18 && SUBSTR(?strVal, 1, 18) = "http://schema.org/").
           %s           
        }
        ORDER BY ?term''') % atticfilter
        props = list(self.queryGraph.query(query))
        self.prop2CSV(header=True,out=file)
        for t in props:
            self.prop2CSV(term=t.term,header=False,out=file,graph=self.queryGraph)

    def outputCSVenums(self,file):
        atticfilter = ""
        if self.excludeAttic:
            atticfilter = "FILTER NOT EXISTS {?term schema:isPartOf <http://attic.schema.org>.}"
        query= ('''select ?term where{
         ?term a ?type. 
         ?type rdfs:subClassOf* <http://schema.org/Enumeration>.
         %s 
        }
        ORDER BY ?term''') % atticfilter
        allenums = list(self.fullGraph.query(query))

        query= ('''select DISTINCT ?term where{
         ?term ?p ?o. 
         FILTER NOT EXISTS {?term a rdfs:Class}. 
         FILTER NOT EXISTS {?term a rdf:Property}.
         %s 
        }
        ORDER BY ?term''') % atticfilter
        terms = list(self.queryGraph.query(query))
        enums = []
        for t in terms:
            if t in allenums:
                enums.append(t)
        self.enum2CSV(header=True,out=file)
        for t in enums:
            self.enum2CSV(term=t.term,header=False,out=file,graph=self.queryGraph)
        
    def enum2CSV(self,term=None,header=True,out=None,graph=None):
        cols = ["id","label","comment","enumerationtype","supersedes","supersededBy","isPartOf"]
        if not out:
            return
        writer = csv.writer(out,quoting=csv.QUOTE_ALL,lineterminator='\n')
        if header:
            writer.writerow(cols)
            return
        if not graph:
            graph = self.queryGraph
        if term == None or graph == None:
            return
        row = [str(term)]
        row.append(self.graphValueToCSV(subject=term,predicate=RDFS.label,graph=graph))
        row.append(self.getCSVComment(term,graph=self.fullGraph))
        row.append(self.graphValueToCSV(subject=term,predicate=RDF.type,graph=graph))
        row.append(self.getCSVsuperseds(term,graph=self.fullGraph))
        row.append(self.getCSVSupersededBy(term,graph=self.fullGraph))
        row.append(self.graphValueToCSV(subject=term,predicate=URIRef("http://schema.org/isPartOf"),graph=graph))

        row=[s.encode('utf-8') for s in row]
        writer.writerow(row)

    def prop2CSV(self,term=None,header=True,out=None,graph=None):
        cols = ["id","label","comment","subPropertyOf","equivalentProperty","subproperties","domainIncludes","rangeIncludes","inversOf","supersedes","supersededBy","isPartOf"]
        if not out:
            return
        writer = csv.writer(out,quoting=csv.QUOTE_ALL,lineterminator='\n')
        if header:
            writer.writerow(cols)
            return
        if not graph:
            graph = self.queryGraph
        if term == None or graph == None:
            return
        row = [str(term)]
        row.append(self.graphValueToCSV(subject=term,predicate=RDFS.label,graph=graph))
        row.append(self.getCSVComment(term,graph=self.fullGraph))
        row.append(self.getCSVSuperProperties(term,graph=self.fullGraph))
        row.append(self.graphValueToCSV(subject=term,predicate=OWL.equivalentProperty,graph=graph))
        row.append(self.getCSVSubProperties(term,graph=self.fullGraph))
        row.append(self.getCSVDomainIncludes(term,graph=self.fullGraph))
        row.append(self.getCSVRangeIncludes(term,graph=self.fullGraph))
        row.append(self.graphValueToCSV(subject=term,predicate=URIRef("http://schema.org/inverseOf"),graph=graph))
        row.append(self.getCSVsuperseds(term,graph=self.fullGraph))
        row.append(self.getCSVSupersededBy(term,graph=self.fullGraph))

        row=[s.encode('utf-8') for s in row]
        writer.writerow(row)
        
        #print term

    def type2CSV(self,term=None,header=True,out=None,graph=None):
        cols = ["id","label","comment","subTypeOf","equivalentClass","properties","subTypes","supersedes","supersededBy","isPartOf"]
        if not out:
            return
        writer = csv.writer(out,quoting=csv.QUOTE_ALL,lineterminator='\n')
        if header:
            writer.writerow(cols)
            return
        if not graph:
            graph = self.queryGraph
        if term == None or graph == None:
            return
            
        if not isinstance(term, URIRef):
            term = URIRef(term)
        row = [str(term)]
        row.append(self.graphValueToCSV(subject=term,predicate=RDFS.label,graph=graph))
        row.append(self.getCSVComment(term,graph=self.fullGraph))
        row.append(self.getCSVSupertypes(term,graph=self.fullGraph))
        row.append(self.graphValueToCSV(subject=term,predicate=OWL.equivalentClass,graph=graph))
        row.append(self.getCSVTypeProperties(term,graph=self.fullGraph))
        row.append(self.getCSVSubtypes(term,graph=self.fullGraph))
        row.append(self.getCSVsuperseds(term,graph=self.fullGraph))
        row.append(self.getCSVSupersededBy(term,graph=self.fullGraph))
        row.append(self.graphValueToCSV(subject=term,predicate=URIRef("http://schema.org/isPartOf"),graph=graph))
        
        row=[s.encode('utf-8') for s in row]
        writer.writerow(row)


    def graphValueToCSV(self, subject=None, predicate= None, object= None, graph=None):
        ret = ""
        try:
            RDFLIBLOCK.acquire()
            ret = str(graph.value(subject=subject,predicate=predicate,object=object))
        finally:
            RDFLIBLOCK.release()
        
        if ret == None or ret == "None":
            ret = ""
        return ret
        
    def getCSVSupertypes(self,term=None,graph=None):
        query='''select ?sup where{
         <%s> rdfs:subClassOf ?sup.
         BIND(STR(?sup) AS ?strVal)
         FILTER(STRLEN(?strVal) >= 18 && SUBSTR(?strVal, 1, 18) = "http://schema.org/")
        }
        ORDER BY ?sup''' % term
        
        res = self.doQuery(graph,query)
        ret = ', '.join([x.sup for x in res])
        return ret

    def getCSVTypeProperties(self,term=None,graph=None):
        atticfilter = ""
        if self.excludeAttic:
            atticfilter = "FILTER NOT EXISTS {?prop schema:isPartOf <http://attic.schema.org>.}"
        query='''select * where{
         ?term (^rdfs:subClassOf*) <%s>.
         ?prop <http://schema.org/domainIncludes> ?term.
         %s
        }
        ORDER BY ?prop''' % (term,atticfilter)
        res = self.doQuery(graph,query)
        ret = ', '.join([x.prop for x in res])
        
        return ret

    def getCSVSubtypes(self,term=None,graph=None):
        atticfilter = ""
        if self.excludeAttic:
            atticfilter = "FILTER NOT EXISTS {?sub schema:isPartOf <http://attic.schema.org>.}"
        query='''select ?sub where{
         ?sub rdfs:subClassOf <%s>.
         %s
        }
        ORDER BY ?sub''' % (term,atticfilter)
        res = self.doQuery(graph,query)
        ret = ', '.join([x.sub for x in res])
        #print "SUBTYPES of %s: '%s'" % (term,ret)
        return ret

    def getCSVSupersededBy(self,term=None,graph=None):
        atticfilter = ""
        if self.excludeAttic:
            atticfilter = "FILTER NOT EXISTS {?sub schema:isPartOf <http://attic.schema.org>.}"
        query='''select ?sup where{
         <%s> schema:supersededBy ?sup.
         %s
        }
        ORDER BY ?sup''' % (term,atticfilter)
        res = self.doQuery(graph,query)
        ret = ', '.join([x.sup for x in res])
        #print "%s supercededBy: '%s'" % (term,ret)
        return ret
        
    def getCSVsuperseds(self,term=None,graph=None):
        atticfilter = ""
        if self.excludeAttic:
            atticfilter = "FILTER NOT EXISTS {?sup schema:isPartOf <http://attic.schema.org>.}"
        query='''select ?sup where{
         ?sup schema:supersededBy <%s>.
         %s
        }
        ORDER BY ?sup''' % (term,atticfilter)
        res = self.doQuery(graph,query)
        ret = ', '.join([x.sup for x in res])
        #print "%s superseds: '%s'" % (term,ret)
        return ret
        
    def getCSVSuperProperties(self,term=None,graph=None):
        query='''select ?sup where{
         <%s> rdfs:subPropertyOf ?sup.
         BIND(STR(?sup) AS ?strVal)
         FILTER(STRLEN(?strVal) >= 18 && SUBSTR(?strVal, 1, 18) = "http://schema.org/")
        }
        ORDER BY ?sup''' % term
        res = self.doQuery(graph,query)
        ret = ', '.join([x.sup for x in res])
        #print "%s subtypeof: '%s'" % (term,ret)
        return ret

    def getCSVSubProperties(self,term=None,graph=None):
        atticfilter = ""
        if self.excludeAttic:
            atticfilter = "FILTER NOT EXISTS {?sub schema:isPartOf <http://attic.schema.org>.}"
        query='''select ?sub where{
         ?sub rdfs:subPropertyOf <%s>.
         %s
        }
        ORDER BY ?sub''' % (term,atticfilter)
        res = self.doQuery(graph,query)
        ret = ', '.join([x.sub for x in res])
        #print "SUBTYPES of %s: '%s'" % (term,ret)
        return ret

    def getCSVDomainIncludes(self,term=None,graph=None):
        atticfilter = ""
        if self.excludeAttic:
            atticfilter = "FILTER NOT EXISTS {?type schema:isPartOf <http://attic.schema.org>.}"
        query='''select ?type where{
         <%s> <http://schema.org/domainIncludes> ?type.
         %s
        }
        ORDER BY ?type''' % (term,atticfilter)
        res = self.doQuery(graph,query)
        ret = ', '.join([x.type for x in res])
        #print "SUBTYPES of %s: '%s'" % (term,ret)
        return ret

    def getCSVRangeIncludes(self,term=None,graph=None):
        atticfilter = ""
        if self.excludeAttic:
            atticfilter = "FILTER NOT EXISTS {?type schema:isPartOf <http://attic.schema.org>.}"
        query='''select ?type where{
         <%s> <http://schema.org/rangeIncludes> ?type.
         %s
        }
        ORDER BY ?type''' % (term,atticfilter)
        res = self.doQuery(graph,query)
        ret = ', '.join([x.type for x in res])
        #print "SUBTYPES of %s: '%s'" % (term,ret)
        return ret

    def getCSVComment(self,term=None,graph=None):
        query='''select ?com where{
         <%s> rdfs:comment ?com.
        }''' % term
        res = self.doQuery(graph,query)
        ret = ', '.join([x.com for x in res])
        #print "SUBTYPES of %s: '%s'" % (term,ret)
        if self.markdown:
            Markdown.setPre("http://schema.org/")
            ret = Markdown.parse(ret)
            Markdown.setPre()
        return ret
