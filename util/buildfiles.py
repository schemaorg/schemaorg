#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import sys
if not (sys.version_info.major == 3 and sys.version_info.minor > 5):
    print("Python version %s.%s not supported version 3.6 or above required - exiting" % (sys.version_info.major,sys.version_info.minor))
    sys.exit(1)

import os
import io
for path in [os.getcwd(),"Util","SchemaPages","SchemaExamples"]:
  sys.path.insert( 1, path ) #Pickup libs from local  directories

from buildsite import *
from sdotermsource import SdoTermSource
from sdoterm import *
from localmarkdown import Markdown
VOCABURI = SdoTermSource.vocabUri()
###################################################
#MARKDOWN INITIALISE
###################################################
Markdown.setWikilinkCssClass("localLink")
Markdown.setWikilinkPrePath("https://schema.org/")
    #Production site uses no suffix in link - mapping to file done in server config
Markdown.setWikilinkPostPath("")
 


def fileName(fn):
    ret =  OUTPUTDIR + '/' + fn
    checkFilePath(os.path.dirname(ret))
    return ret

CACHECONTEXT = None
def jsonldcontext(page):
    global CACHECONTEXT
    from sdojsonldcontext import createcontext
    if not CACHECONTEXT:
        CACHECONTEXT = createcontext()
    return CACHECONTEXT
    
        
import json
def jsonldtree(page):
    global VISITLIST
    VISITLIST=[]
    
    term = {}
    context = {}
    context['rdfs'] = "http://www.w3.org/2000/01/rdf-schema#"
    context['schema'] = "https://schema.org"
    context['rdfs:subClassOf'] = { "@type": "@id" }
    context['description'] = "rdfs:comment"
    context['children'] = { "@reverse": "rdfs:subClassOf" }
    term['@context'] = context
    data = _jsonldtree("Thing",term)
    return json.dumps(data,indent=3)

def _jsonldtree(tid,term=None):
    termdesc = SdoTermSource.getTerm(tid)
    if not term:
        term = {}
    term['@type'] = "rdfs:Class"
    term['@id'] = "schema:" + termdesc.id
    term['name'] = termdesc.label
    if termdesc.supers:
        sups = []
        for sup in termdesc.supers:
            sups.append("schema:" + sup)
        if len(sups) == 1:
            term['rdfs:subClassOf'] = sups[0]
        else:
            term['rdfs:subClassOf'] = sups
    term['description'] = ShortenOnSentence(StripHtmlTags(termdesc.comment))
    if termdesc.pending:
        term['pending'] = True
    if termdesc.retired:
        term['attic'] = True
    if tid not in VISITLIST:
        VISITLIST.append(tid)
        if termdesc.subs:
            subs = []
            for sub in termdesc.subs:
                subs.append(_jsonldtree(sub))
            term['children'] = subs
    return term

def owl(page):
    from sdoowl import OwlBuild
    return OwlBuild().getContent()

def sitemap(page):
    node = """ <url>
   <loc>https://schema.org/%s</loc>
   <lastmod>%s</lastmod>
 </url>
"""
    STATICPAGES = ["docs/schemas.html",
                    "docs/full.html",
                    "docs/gs.html",
                    "docs/about.html",
                    "docs/howwework.html",
                    "docs/releases.html",
                    "docs/faq.html",
                    "docs/datamodel.html",
                    "docs/developers.html",
                    "docs/extension.html",
                    "docs/meddocs.html",
                    "docs/hotels.html"]

    output = []
    output.append("""<?xml version="1.0" encoding="utf-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
""")
    terms = SdoTermSource.getAllTerms(supressSourceLinks=True)
    ver = getVersionDate(getVersion())
    for term in terms:
        if not (term.startswith("http://") or term.startswith("https://")):
            output.append(node % (term,ver))
    for term in STATICPAGES:
        output.append(node % (term,ver))
    output.append("</urlset>\n")
    return "".join(output)

def prtocolswap(content,protocol,altprotocol):
    ret = content.replace("%s://schema.org" % protocol,"%s://schema.org" % altprotocol)
    for ext in ["attic","auto","bib","health-lifesci","meta","pending"]:
        ret = ret.replace("%s://%s.schema.org" % (protocol,ext),"%s://%s.schema.org" % (altprotocol,ext))
    return ret
   
def protocols():
    protocol="http"
    altprotocol="https"
    if VOCABURI.startswith("https"):
        protocol="https"
        altprotocol="http"
    return protocol,altprotocol

import rdflib
from rdflib.serializer import Serializer
import rdflib_jsonld
rdflib.plugin.register("json-ld", Serializer, "rdflib_jsonld.serializer", "JsonLDSerializer")
allGraph = None
currentGraph = None
def exportrdf(exportType):
    global allGraph, currentGraph
    
    if not allGraph:
        allGraph = rdflib.Graph()
        currentGraph = rdflib.Graph()
        allGraph += SdoTermSource.sourceGraph()
        deloddtriples = """DELETE {?s ?p ?o}
            WHERE {
                ?s ?p ?o.
                FILTER (! (strstarts(str(?s), "http://schema.org") || strstarts(str(?s), "http://schema.org") )).
            }"""
        allGraph.update(deloddtriples)
        currentGraph += allGraph
    
        protocol, altprotocol = protocols()
    
        delattic="""PREFIX schema: <%s://schema.org/>
        DELETE {?s ?p ?o}
        WHERE{
            ?s ?p ?o;
                schema:isPartOf <%s://attic.schema.org>.
        }""" % (protocol,protocol)
        currentGraph.update(delattic)
 
    formats =  ["json-ld", "turtle", "nt", "nquads", "rdf"]
    extype = exportType[len("RDFExport."):]
    if exportType == "RDFExports":
        for format in sorted(formats):
            _exportrdf(format,allGraph,currentGraph)
    elif extype in formats:
        _exportrdf(extype,allGraph,currentGraph)
    else:
        raise Exception("Unknown export format: %s" % exportType)
        

completed = []        
def _exportrdf(format,all,current):
    global completed
    exts = {"xml":".xml","rdf":".rdf","nquads":".nq","nt": ".nt","json-ld": ".jsonld", "turtle":".ttl"}
    protocol, altprotocol = protocols()
    
    if format in completed:
        return
    else:
        completed.append(format)
        
    for ver in ["current","all"]:
        if ver == "all":
            g = all
        else:
            g = current
        if format == "nquads":
            gr = rdflib.Dataset()
            qg = gr.graph(URIRef("%s://schema.org/%s" % (protocol,getVersion())))
            qg += g
            g = gr
        fn = fileName("releases/%s/schemaorg-%s-%s%s" % (getVersion(),ver,protocol,exts[format]))
        afn = fileName("releases/%s/schemaorg-%s-%s%s" % (getVersion(),ver,altprotocol,exts[format]))
        fmt = format
        if format == "rdf":
            fmt = "pretty-xml"
        f = open(fn,"w")
        af = open(afn,"w")
        kwargs = {'sort_keys': True}
        out = g.serialize(format=fmt,auto_compact=True,**kwargs).decode()
        f.write(out)
        print(fn)
        af.write(prtocolswap(out,protocol=protocol,altprotocol=altprotocol))
        print(afn)
        f.close()
        af.close()

def array2str(ar):
    if not ar or not len(ar):
        return ""
    buf = []
    first = True
    for i in ar:
        if first:
            first = False
        else:
            buf.append(', ')
        buf.append(i)
    return "".join(buf)

def uriwrap(ids):
    single = False
    if not isinstance(ids, list):
        single = True
        ids = [ids]
    ret = []
    for i in ids:
        if i and len(i):
            ret.append(VOCABURI + i)
        else:
            ret.append("")
    if single:
        return ret[0]
    if not len(ret):
        return ""
    return array2str(ret)

def exportcsv(page):
    protocol, altprotocol = protocols()

    typeFields = ["id","label","comment","subTypeOf","enumerationtype","equivalentClass","properties","subTypes","supersedes","supersededBy","isPartOf"]
    propFields = ["id","label","comment","subPropertyOf","equivalentProperty","subproperties","domainIncludes","rangeIncludes","inverseOf","supersedes","supersededBy","isPartOf"]
    typedata = []
    typedataAll = []
    propdata = []
    propdataAll = []
    terms = SdoTermSource.getAllTerms(expanded=True,supressSourceLinks=True)
    for term in terms:
        if term.termType == SdoTerm.REFERENCE or term.id.startswith("http://") or term.id.startswith("https://"):
            continue
        row = {}
        row["id"] = term.uri 
        row["label"] = term.label
        row["comment"] = term.comment
        row["supersedes"] = uriwrap(term.supersedes)
        row["supersededBy"] = uriwrap(term.supersededBy)
        #row["isPartOf"] = term.isPartOf
        row["isPartOf"] = ""
        if term.termType == SdoTerm.PROPERTY:
            row["subPropertyOf"] = uriwrap(term.supers)
            row["equivalentProperty"] = array2str(term.equivalents)
            row["subproperties"] = uriwrap(term.subs)
            row["domainIncludes"] = uriwrap(term.domainIncludes)
            row["rangeIncludes"] = uriwrap(term.rangeIncludes)
            row["inverseOf"] = uriwrap(term.inverse)
            propdataAll.append(row)
            if not term.retired:
                propdata.append(row)
        else:
            row["subTypeOf"] = uriwrap(term.supers)
            if term.termType == SdoTerm.ENUMERATIONVALUE:
                row["enumerationtype"] = uriwrap(term.enumerationParent)
            else:
                row["properties"] = uriwrap(term.allproperties)
            row["equivalentClass"] = array2str(term.equivalents)
            row["subTypes"] = uriwrap(term.subs)
            typedataAll.append(row)
            if not term.retired:
                typedata.append(row)
    
    writecsvout(propdata,propFields,"current",protocol,altprotocol)
    writecsvout(propdataAll,propFields,"all",protocol,altprotocol)
    writecsvout(typedata,typeFields,"current",protocol,altprotocol)
    writecsvout(typedataAll,typeFields,"all",protocol,altprotocol)

def writecsvout(data,fields,ver,protocol,altprotocol):
    import csv
    fn = fileName("releases/%s/schemaorg-%s-%s-properties.csv" % (getVersion(),ver,protocol))
    afn = fileName("releases/%s/schemaorg-%s-%s-properties.csv" % (getVersion(),ver,altprotocol))
    csvout = io.StringIO()
    csvfile = open(fn,'w')
    acsvfile = open(afn,'w')
    writer = csv.DictWriter(csvout, fieldnames=fields)
    writer.writeheader()
    for row in data:
        writer.writerow(row)
    csvfile.write(csvout.getvalue())
    print(fn)
    csvfile.close()
    acsvfile.write(prtocolswap(csvout.getvalue(),protocol=protocol,altprotocol=altprotocol))
    print(afn)
    acsvfile.close()
    csvout.close()

def examples(page):
    return SchemaExamples.allExamplesSerialised()

FILELIST = { "Context": (jsonldcontext,["docs/jsonldcontext.jsonld",
                "docs/jsonldcontext.json","docs/jsonldcontext.json.txt",
                "releases/%s/schemaorgcontext.jsonld" % getVersion()]),
            "Tree": (jsonldtree,["docs/tree.jsonld"]),
            "Owl": (owl,["docs/schemaorg.owl","releases/%s/schemaorg.owl" % getVersion()]),
            "Sitemap": (sitemap,["docs/sitemap.xml"]),
            "RDFExports": (exportrdf,[""]),
            "RDFExport.turtle": (exportrdf,[""]),
            "RDFExport.rdf": (exportrdf,[""]),
            "RDFExport.nt": (exportrdf,[""]),
            "RDFExport.nquads": (exportrdf,[""]),
            "RDFExport.json-ld": (exportrdf,[""]),
            "CSVExports": (exportcsv,[""]),
            "Examples": (examples,["releases/%s/all_examples.txt" % getVersion()])
         }

def buildFiles(files):
    all = ["ALL","All","all"]
    for a in all:
        if a in files:
            files = sorted(FILELIST.keys())
            break


    for p in files:
        print("%s:"%p)
        func, filenames = FILELIST.get(p,None)
        if func:
            content = func(p)
            if content:
                for filename in filenames:
                    fn = fileName(filename)
                    f = open(fn,"w")
                    f.write(content)
                    f.close()
                    print("Created %s" % fn)
        else:
            print("Unknown files name: %s" % p)
