#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import sys
if not (sys.version_info.major == 3 and sys.version_info.minor > 5):
    print("Python version %s.%s not supported version 3.6 or above required - exiting" % (sys.version_info.major,sys.version_info.minor))
    sys.exit(1)

import os
for path in [os.getcwd(),"Util","SchemaPages","SchemaExamples"]:
  sys.path.insert( 1, path ) #Pickup libs from local  directories

from buildsite import *
from sdotermsource import SdoTermSource
from sdoterm import *

def fileName(fn):
    name = OUTPUTDIR + "/" +fn
    checkFilePath(os.path.dirname(name))
    return name


def docsTemplateRender(template,extra_vars=None):
    tvars = {
        'docsdir': DOCSDOCSDIR
    }
    if extra_vars:
        tvars.update(extra_vars)
    return templateRender(template,tvars)

def schemasPage(page):
    extra_vars = {
        'home_page': "False",
        'title': SITENAME + ' - Schemas',
        'termcounts': SdoTermSource.termCounts()
    }
    return docsTemplateRender("docs/Schemas.j2",extra_vars)

def homePage(page):
    global STRCLASSVAL
    title = SITENAME
    template = "docs/Home.j2"
    filt = None
    overrideclassval = None
    if page == "PendingHome":
        title += " - Pending"
        template = "docs/PendingHome.j2"
        filt = "pending"
        overrideclassval = 'class="ext ext-pending"'
    elif page == "AtticHome":
        title += " - Retired"
        template = "docs/AtticHome.j2"
        filt="attic"
        overrideclassval = 'class="ext ext-attic"'
    sectionterms={}
    termcount=0
    if filt:
        terms = SdoTermSource.getAllTerms(layer=filt,expanded=True)
        terms.sort(key = lambda u: (u.category, u.id))
        first = True
        cat = None
        for t in terms:
            if first or t.category != cat:
                first = False
                cat = t.category 
                ttypes = {}
                sectionterms[cat] = ttypes
                ttypes[SdoTerm.TYPE] = []
                ttypes[SdoTerm.PROPERTY] = []
                ttypes[SdoTerm.DATATYPE] = []
                ttypes[SdoTerm.ENUMERATION] = []
                ttypes[SdoTerm.ENUMERATIONVALUE] = []
            if t.termType == SdoTerm.REFERENCE:
                continue
            ttypes[t.termType].append(t)
            termcount += 1
    
    extra_vars = {
        'home_page': "True",
        'title': SITENAME,
        'termcount': termcount,
        'sectionterms': sectionterms
    }
    STRCLASSVAL = overrideclassval
    ret =  docsTemplateRender(template,extra_vars)
    STRCLASSVAL = None
    return ret

VISITLIST=[]
class listingNode():
    
    def __init__(self,term,depth=0,title="",parent=None):
        global VISITLIST
        termdesc = SdoTermSource.getTerm(term)
        if parent == None:
            VISITLIST=[]
        self.repeat = False
        self.subs = []
        self.parent = parent
        self.title = title
        self.id = termdesc.label
        self.termType = termdesc.termType
        self.depth = depth
        self.retired = termdesc.retired
        self.pending = termdesc.pending
        if not self.id in VISITLIST:
            VISITLIST.append(self.id)
            if termdesc.termType == SdoTerm.ENUMERATION:
                for enum in sorted(termdesc.enumerationMembers):
                    self.subs.append(listingNode(enum,depth=depth+1,parent=self))
            for sub in sorted(termdesc.subs):
                self.subs.append(listingNode(sub,depth=depth+1,parent=self))
                
        else: #Visited this node before so don't parse children
            self.repeat = True
        #log.info("%s %s %s"%("  "*depth,term,len(self.subs)))
        
def StripHtmlTags(source):
    if source and len(source) > 0:
        return re.sub('<[^<]+?>', '', source)
    return ""

def ShortenOnSentence(source,lengthHint=250):
    if source and len(source) > lengthHint:
        source = source.strip()
        sentEnd = re.compile('[.!?]')
        sentList = sentEnd.split(source)
        com=""
        count = 0
        while count < len(sentList):
            if(count > 0 ):
                if len(com) < len(source):
                    com += source[len(com)]
            com += sentList[count]
            count += 1
            if count == len(sentList):
                if len(com) < len(source):
                    com += source[len(source) - 1]
            if len(com) > lengthHint:
                if len(com) < len(source):
                    com += source[len(com)]
                break
                
        if len(source) > len(com) + 1:
            com += ".."
        source = com
    return source

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
    
listings = None
def fullPage(page):
    global listings
    if not listings:
        listings = []
        listings.append(listingNode("Thing",title="Types:"))
        listings.append(listingNode("DataType",title="DataTypes:"))
    extra_vars = {
        'home_page': "False",
        'title': SITENAME,
        'listings': listings
    }

    return docsTemplateRender("docs/%s.j2" % page,extra_vars)

def fullReleasePage(page):
    listings = []
    listings.append(listingNode("Thing",title="Type hierarchy"))
    types = SdoTermSource.getAllEnumerationvalues(expanded=True)
    types.extend(SdoTermSource.getAllTypes(expanded=True))
    types = SdoTermSource.expandTerms(types)
    types = sorted(types, key=lambda t: t.id)
    extra_vars = {
        'home_page': "False",
        'title': "Full Release Summary",
        'version': getVersion(),
        'date': getCurrentVersionDate(),
        'listings': listings,
        'types': types,
        'properties': SdoTermSource.getAllProperties(expanded=True)
    }
    return docsTemplateRender("docs/FullRelease.j2",extra_vars)

    

PAGELIST = {"Home": (homePage,["docs/home.html"]),
             "PendingHome": (homePage,["docs/pending.home.html"]),
             "AtticHome": (homePage,["docs/attic.home.html"]),
             "Schemas": (schemasPage,["docs/schemas.html"]),
             "Full": (fullPage,["docs/full.html"]),
             "FullBeta": (fullPage,["docs/full.beta.html","docs/full4.html"]),
             "FullRelease": (fullReleasePage,["docs/fullrelease.html","releases/%s/schema-all.html" % getVersion()]),
             "Tree": (jsonldtree,["docs/tree.jsonld"])
         }

def buildDocs(pages):
    all = ["ALL","All","all"]
    for a in all:
        if a in pages:
            pages = sorted(PAGELIST.keys())
            break


    for p in pages:
        print("%s:"%p)
        func, filenames = PAGELIST.get(p,None)
        if func:
            content = func(p)
            for filename in filenames:
                fn = fileName(filename)
                f = open(fn,"w")
                f.write(content)
                f.close()
                print("Created %s" % fn)
        else:
            print("Unknown page name: %s" % p)
