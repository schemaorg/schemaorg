#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import logging
logging.basicConfig(level=logging.INFO) # dev_appserver.py --log_level debug .
log = logging.getLogger(__name__)

import os
import re
import webapp2
import jinja2
import logging
import StringIO
import json
import rdflib
#from rdflib.namespace import RDFS, RDF, OWL
#from rdflib.term import URIRef

from markupsafe import Markup, escape # https://pypi.python.org/pypi/MarkupSafe

import threading
import itertools
import datetime, time
from time import gmtime, strftime

from google.appengine.ext import ndb
from google.appengine.ext import blobstore
from google.appengine.api import users
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api import modules
from google.appengine.api import runtime

from api import *
from apirdflib import load_graph, getNss, getRevNss, buildSingleTermGraph, serializeSingleTermGrapth
from apirdflib import countTypes, countProperties, countEnums

from apimarkdown import Markdown

from sdordf2csv import sdordf2csv

SCHEMA_VERSION=3.2

FEEDBACK_FORM_BASE_URL='https://docs.google.com/a/google.com/forms/d/1krxHlWJAO3JgvHRZV9Rugkr9VYnMdrI10xbGsWt733c/viewform?entry.1174568178&entry.41124795={0}&entry.882602760={1}'
# {0}: term URL, {1} category of term.

sitemode = "mainsite" # whitespaced list for CSS tags,
            # e.g. "mainsite testsite" when off expected domains
            # "extensionsite" when in an extension (e.g. blue?)

releaselog = { "2.0": "2015-05-13", "2.1": "2015-08-06", "2.2": "2015-11-05", "3.0": "2016-05-04", "3.1": "2016-08-09" }

silent_skip_list =  [ "favicon.ico" ] # Do nothing for now

all_layers = {}
ext_re = re.compile(r'([^\w,])+')

#TODO: Modes:
# mainsite
# webschemadev
# known extension (not skiplist'd, eg. demo1 on schema.org)

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')),
    extensions=['jinja2.ext.autoescape'], autoescape=True, cache_size=0)

ENABLE_JSONLD_CONTEXT = True
ENABLE_CORS = True
ENABLE_HOSTED_EXTENSIONS = True
DISABLE_NDB_FOR_LOCALHOST = True

#INTESTHARNESS = True #Used to indicate we are being called from tests - use setInTestHarness() & getInTestHarness() to manage value

EXTENSION_SUFFIX = "" # e.g. "*"

CORE = 'core'
ATTIC = 'attic'
ENABLED_EXTENSIONS = [ATTIC, 'auto', 'bib', 'health-lifesci', 'pending', 'meta', 'iot' ]
#### Following 2 lines look odd - leave them as is - just go with it!
ALL_LAYERS = [CORE,'']
ALL_LAYERS += ENABLED_EXTENSIONS
####
ALL_LAYERS_NO_ATTIC = list(ALL_LAYERS) 
ALL_LAYERS_NO_ATTIC.remove(ATTIC)
setAllLayersList(ALL_LAYERS)

OUTPUTDATATYPES = [".csv",".jsonld",".ttl",".rdf",".xml",".nt"]

FORCEDEBUGGING = False
# FORCEDEBUGGING = True

SHAREDSITEDEBUG = True
if getInTestHarness():
    SHAREDSITEDEBUG = False

LOADEDSOURCES = False

############# Warmup Control ########
WarmedUp = False
WarmupState = "Auto"
if "WARMUPSTATE" in os.environ:
    WarmupState = os.environ["WARMUPSTATE"]
log.info("[%s] WarmupState: %s" % (getInstanceId(short=True),WarmupState))

if WarmupState.lower() == "off":
    WarmedUp = True
elif "SERVER_NAME" in os.environ and ("localhost" in os.environ['SERVER_NAME'] and WarmupState.lower() == "auto"):
    WarmedUp = True

############# Shared values and times ############
#### Memcache functions dissabled in test mode ###
appver = "TestHarness Version"
if "CURRENT_VERSION_ID" in os.environ:
    appver = os.environ["CURRENT_VERSION_ID"]


instance_first = True
instance_num = 0
callCount = 0
global_vars = threading.local()
starttime = datetime.datetime.utcnow()
systarttime = starttime
modtime = starttime
etagSlug = ""

if not getInTestHarness():
    from google.appengine.api import memcache

class SlugEntity(ndb.Model):
    slug = ndb.StringProperty()
    modtime = ndb.DateTimeProperty()

def setmodiftime(sttime):
    global modtime, etagSlug
    if not getInTestHarness():
        modtime = sttime.replace(microsecond=0)
        etagSlug = "24751%s" % modtime.strftime("%y%m%d%H%M%Sa")
        log.debug("set slug: %s" % etagSlug)
        slug = SlugEntity(id="ETagSlug",slug=etagSlug, modtime=modtime)
        slug.put()

def getmodiftime():
    global modtime, etagSlug
    if not getInTestHarness():
        slug = SlugEntity.get_by_id("ETagSlug")
        modtime = slug.modtime
        etagSlug = str(slug.slug)
    return modtime

def getslug():
    global etagSlug
    getmodiftime()
    return etagSlug

    
def tick(): #Keep memcache values fresh so they don't expire
    if not getInTestHarness():
        memcache.set(key="SysStart", value=systarttime)
        memcache.set(key="static-version", value=appver)

if getInTestHarness():
    load_examples_data(ENABLED_EXTENSIONS)
    
else: #Ensure clean start for any memcached or ndb store values...
    if memcache.get("static-version") != appver: #We are a new instance of the app
        memcache.flush_all()
        
        memcache.set(key="app_initialising", value=True)
        log.info("[%s] Detected new code version - resetting memory values %s" % (getInstanceId(short=True),systarttime))
        load_start = datetime.datetime.now()
        systarttime = datetime.datetime.utcnow()
        memcache.set(key="static-version", value=appver)
        memcache.add(key="SysStart", value=systarttime)
        instance_first = True
        cleanmsg = CacheControl.clean()
        log.info("Clean count(s): %s" % cleanmsg)
        log.info(("[%s] Cache clean took %s " % (getInstanceId(short=True),(datetime.datetime.now() - load_start))))
        
        load_start = datetime.datetime.now()
        
        memcache.set(key="app_initialising", value=False)
        
        log.debug("[%s] Awake >>>>>>>>>>>>" % (getInstanceId(short=True)))
    else:
        time.sleep(0.1) #Give time for the initialisation flag (possibly being set in another thread/instance) to be set
        while memcache.get("app_initialising"):
            log.debug("[%s] Waiting for intialisation to end %s" % (getInstanceId(short=True),memcache.get("app_initialising")))
            time.sleep(0.1)
        log.debug("[%s] End of waiting !!!!!!!!!!!" % (getInstanceId(short=True)))
        systarttime = memcache.get("SysStart")
        tick()
    setmodiftime(systarttime)
    
#################################################

def cleanPath(node):
    """Return the substring of a string matching chars approved for use in our URL paths."""
    return re.sub(r'[^a-zA-Z0-9\-/,\.]', '', str(node), flags=re.DOTALL)



class HTMLOutput:
    """Used in place of http response when we're collecting HTML to pass to template engine."""

    def __init__(self):
        self.outputStrings = []

    def write(self, str):
        self.outputStrings.append(str)

    def toHTML(self):
        return Markup ( "".join(self.outputStrings)  )

    def __str__(self):
        return self.toHTML()

# Core API: we have a single schema graph built from triples and units.
# now in api.py


class TypeHierarchyTree:

    def __init__(self, prefix=""):
        self.txt = ""
        self.visited = {}
        self.prefix = prefix

    def emit(self, s):
        self.txt += s + "\n"

    def emit2buff(self, buff, s):
        buff.write(s + "\n")

    def toHTML(self):
        return '%s<ul>%s</ul>' % (self.prefix, self.txt)

    def toJSON(self):
        return self.txt

    def traverseForHTML(self, node, depth = 1, hashorslash="/", layers='core', traverseAllLayers=False, buff=None):

        """Generate a hierarchical tree view of the types. hashorslash is used for relative link prefixing."""

        log.debug("traverseForHTML: node=%s hashorslash=%s" % ( node.id, hashorslash ))

        if node.superseded(layers=layers):
            return False

        localBuff = False
        if buff == None:
            localBuff = True
            buff = StringIO.StringIO()

        urlprefix = ""
        home = node.getHomeLayer()
        gotOutput = False

        if not traverseAllLayers and home not in layers:
            gotOutput = False
            return gotOutput

        if home in ENABLED_EXTENSIONS and home != getHostExt():
            urlprefix = makeUrl(home)

        extclass = ""
        extflag = ""
        tooltip=""
        if home != "core" and home != "":
            extclass = "class=\"ext ext-%s\"" % home
            extflag = EXTENSION_SUFFIX
            tooltip = "title=\"Extended schema: %s.schema.org\" " % home

        # we are a supertype of some kind
        subTypes = node.GetImmediateSubtypes(layers=ALL_LAYERS)
        if len(subTypes) > 0:
            # and we haven't been here before
            if node.id not in self.visited:
                self.visited[node.id] = True # remember our visit
                self.emit2buff(buff, ' %s<li class="tbranch" id="%s"><a %s %s href="%s%s%s">%s</a>%s' % (" " * 4 * depth, node.id,  tooltip, extclass, urlprefix, hashorslash, node.id, node.id, extflag) )
                self.emit2buff(buff, ' %s<ul>' % (" " * 4 * depth))

                # handle our subtypes
                for item in subTypes:
                    subBuff = StringIO.StringIO()
                    got = self.traverseForHTML(item, depth + 1, hashorslash=hashorslash, layers=layers, traverseAllLayers=traverseAllLayers,buff=subBuff)
                    if got:
                        gotOutput = True
                        self.emit2buff(buff,subBuff.getvalue())
                    subBuff.close()
                self.emit2buff(buff, ' %s</ul>' % (" " * 4 * depth))
            else:
                # we are a supertype but we visited this type before, e.g. saw Restaurant via Place then via Organization
                seen = '  <a href="#%s">+</a> ' % node.id
                self.emit2buff(buff, ' %s<li class="tbranch" id="%s"><a %s %s href="%s%s%s">%s</a>%s%s' % (" " * 4 * depth, node.id,  tooltip, extclass, urlprefix, hashorslash, node.id, node.id, extflag, seen) )
        # leaf nodes
        if len(subTypes) == 0:
            if home  in layers:
                gotOutput = True
                if node.id not in self.visited:
                    self.emit2buff(buff, '%s<li class="tleaf" id="%s"><a %s %s href="%s%s%s">%s</a>%s%s' % (" " * depth, node.id, tooltip, extclass, urlprefix, hashorslash, node.id, node.id, extflag, "" ))
            #else:
                #self.visited[node.id] = True # never...
                # we tolerate "VideoGame" appearing under both Game and SoftwareApplication
                # and would only suppress it if it had its own subtypes. Seems legit.

        self.emit2buff(buff, ' %s</li>' % (" " * 4 * depth) )

        if localBuff:
            self.emit(buff.getvalue())
            buff.close()

        return gotOutput

    # based on http://danbri.org/2013/SchemaD3/examples/4063550/hackathon-schema.js  - thanks @gregg, @sandro
    def traverseForJSONLD(self, node, depth = 0, last_at_this_level = True, supertype="None", layers='core'):
        emit_debug = False
        if node.id in self.visited:
            # self.emit("skipping %s - already visited" % node.id)
            return
        self.visited[node.id] = True
        p1 = " " * 4 * depth
        if emit_debug:
            self.emit("%s# @id: %s last_at_this_level: %s" % (p1, node.id, last_at_this_level))
        global namespaces;
        ctx = "{}".format(""""@context": {
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "schema": "http://schema.org/",
    "rdfs:subClassOf": { "@type": "@id" },
    "name": "rdfs:label",
    "description": "rdfs:comment",
    "children": { "@reverse": "rdfs:subClassOf" }
  },\n""" if last_at_this_level and depth==0 else '' )

        unseen_subtypes = []
        for st in node.GetImmediateSubtypes(layers=layers):
            if not st.id in self.visited:
                unseen_subtypes.append(st)
        unvisited_subtype_count = len(unseen_subtypes)
        subtype_count = len( node.GetImmediateSubtypes(layers=layers) )

        supertx = "{}".format( '"rdfs:subClassOf": "schema:%s", ' % supertype.id if supertype != "None" else '' )
        maybe_comma = "{}".format("," if unvisited_subtype_count > 0 else "")
        comment = GetComment(node, layers).strip()
        comment = ShortenOnSentence(StripHtmlTags(comment),60)

        def encode4json(s):
            return json.dumps(s)

        self.emit('\n%s{\n%s\n%s"@type": "rdfs:Class", %s "description": %s,\n%s"name": "%s",\n%s"@id": "schema:%s",\n%s"layer": "%s"%s'
                  % (p1, ctx, p1,                 supertx,            encode4json(comment),     p1,   node.id, p1,        node.id, p1, node.getHomeLayer(), maybe_comma))

        i = 1
        if unvisited_subtype_count > 0:
            self.emit('%s"children": ' % p1 )
            self.emit("  %s["  % p1 )
            inner_lastness = False
            for t in unseen_subtypes:
                if emit_debug:
                    self.emit("%s  # In %s > %s i: %s unvisited_subtype_count: %s" %(p1, node.id, t.id, i, unvisited_subtype_count))
                if i == unvisited_subtype_count:
                    inner_lastness = True
                i = i + 1
                self.traverseForJSONLD(t, depth + 1, inner_lastness, supertype=node, layers=layers)

            self.emit("%s  ]%s" % (p1,  "{}".format( "" if not last_at_this_level else '' ) ) )

        maybe_comma = "{}".format( ',' if not last_at_this_level else '' )
        self.emit('\n%s}%s\n' % (p1, maybe_comma))



def GetExamples(node, layers='core'):
    """Returns the examples (if any) for some Unit node."""
    return LoadNodeExamples(node,layers)

def GetExtMappingsRDFa(node, layers='core'):
    """Self-contained chunk of RDFa HTML markup with mappings for this term."""
    if (node.isClass()):
        equivs = GetTargets(Unit.GetUnit("owl:equivalentClass"), node, layers=layers)
        if len(equivs) > 0:
            markup = ''
            for c in equivs:

                if (c.id.startswith('http')):
                  markup = markup + "<link property=\"owl:equivalentClass\" href=\"%s\"/>\n" % c.id
                else:
                  markup = markup + "<link property=\"owl:equivalentClass\" resource=\"%s\"/>\n" % c.id

            return markup
    if (node.isAttribute()):
        equivs = GetTargets(Unit.GetUnit("owl:equivalentProperty"), node, layers)
        if len(equivs) > 0:
            markup = ''
            for c in equivs:
                markup = markup + "<link property=\"owl:equivalentProperty\" href=\"%s\"/>\n" % c.id
            return markup
    return "<!-- no external mappings noted for this term. -->"

class ShowUnit (webapp2.RequestHandler):
    """ShowUnit exposes schema.org terms via Web RequestHandler
    (HTML/HTTP etc.).
    """

    def emitCacheHeaders(self):
        """Send cache-related headers via HTTP."""
        self.response.headers['Cache-Control'] = "public, max-age=600" # 10m
        self.response.headers['Vary'] = "Accept, Accept-Encoding"

    def write(self, str):
        """Write some text to Web server's output stream."""
        self.outputStrings.append(str)


    def moreInfoBlock(self, node, layer='core'):

        # if we think we have more info on this term, show a bulleted list of extra items.

        # defaults
        bugs = ["No known open issues."]
        mappings = ["No recorded schema mappings."]
        items = bugs + mappings

        nodetype="Misc"

        if node.isEnumeration():
            nodetype = "enumeration"
        elif node.isDataType(layers=layer):
            nodetype = "datatype"
        elif node.isClass(layers=layer):
            nodetype = "type"
        elif node.isAttribute(layers=layer):
            nodetype = "property"
        elif node.isEnumerationValue(layers=layer):
            nodetype = "enumeratedvalue"

        feedback_url = FEEDBACK_FORM_BASE_URL.format("http://schema.org/{0}".format(node.id), nodetype)
        items = [

        "<a href='{0}'>Leave public feedback on this term &#128172;</a>".format(feedback_url),
        "<a href='https://github.com/schemaorg/schemaorg/issues?q=is%3Aissue+is%3Aopen+{0}'>Check for open issues.</a>".format(node.id)

        ]

        for l in all_terms[node.id]:
            l = l.replace("#","")
            if l == "core":
                ext = ""
            else:
                ext = "extension "
            if ENABLE_HOSTED_EXTENSIONS:
                items.append("'{0}' is mentioned in {1}layer: <a href='{2}'>{3}</a>".format( node.id, ext, makeUrl(l,node.id), l ))

        moreinfo = """<div>
        <div id='infobox' style='text-align: right;'><label role="checkbox" for=morecheck><b><span style="cursor: pointer;">[more...]</span></b></label></div>
        <input type='checkbox' checked="checked" style='display: none' id=morecheck><div id='infomsg' style='background-color: #EEEEEE; text-align: left; padding: 0.5em;'>
        <ul>"""

        for i in items:
            moreinfo += "<li>%s</li>" % i

#          <li>mappings to other terms.</li>
#          <li>or links to open issues.</li>

        moreinfo += "</ul>\n</div>\n</div>\n"
        return moreinfo

    def GetParentStack(self, node, layers='core'):
        """Returns a hiearchical structured used for site breadcrumbs."""
        thing = Unit.GetUnit("Thing")
        #log.info("GetParentStack for: %s",node)
        if (node not in self.parentStack):
            self.parentStack.append(node)

        if (Unit.isAttribute(node, layers=layers)):
            self.parentStack.append(Unit.GetUnit("Property"))
            self.parentStack.append(thing)

        sc = Unit.GetUnit("rdfs:subClassOf")
        if GetTargets(sc, node, layers=layers):
            for p in GetTargets(sc, node, layers=layers):
                self.GetParentStack(p, layers=layers)
        else:
            # Enumerations are classes that have no declared subclasses
            sc = Unit.GetUnit("rdf:type")
            for p in GetTargets(sc, node, layers=layers):
                self.GetParentStack(p, layers=layers)

#Put 'Thing' to the end for multiple inheritance classes
        if(thing in self.parentStack):
            self.parentStack.remove(thing)
            self.parentStack.append(thing)


    def ml(self, node, label='', title='', prop='', hashorslash='/'):
        """ml ('make link')
        Returns an HTML-formatted link to the class or property URL

        * label = optional anchor text label for the link
        * title = optional title attribute on the link
        * prop = an optional property value to apply to the A element
        """

        if label=='':
          label = node.id
        if title != '':
          title = " title=\"%s\"" % (title)
        if prop:
            prop = " property=\"%s\"" % (prop)

        rdfalink = ''
        if prop:
            rdfalink = '<link %s href="http://schema.org/%s" />' % (prop,label)

        if(node.id == "DataType"):  #Special case
            return "%s<a href=\"%s\">%s</a>" % (rdfalink,node.id, node.id)

        urlprefix = ""
        home = node.getHomeLayer()

        if home in ENABLED_EXTENSIONS and home != getHostExt():
            port = ""
            if getHostPort() != "80":
                port = ":%s" % getHostPort()
            urlprefix = makeUrl(home)

        extclass = ""
        extflag = ""
        tooltip = ""
        if home != "core" and home != "":
            if home != "meta":
                extclass = "class=\"ext ext-%s\" " % home
            extflag = EXTENSION_SUFFIX
            tooltip = "title=\"Defined in extension: %s.schema.org\" " % home



        return "%s<a %s %s href=\"%s%s%s\"%s>%s</a>%s" % (rdfalink,tooltip, extclass, urlprefix, hashorslash, node.id, title, label, extflag)
        #return "<a %s %s href=\"%s%s%s\"%s%s>%s</a>%s" % (tooltip, extclass, urlprefix, hashorslash, node.id, prop, title, label, extflag)

    def makeLinksFromArray(self, nodearray, tooltip=''):
        """Make a comma separate list of links via ml() function.

        * tooltip - optional text to use as title of all links
        """
        hyperlinks = []
        for f in nodearray:
           hyperlinks.append(self.ml(f, f.id, tooltip))
        return (", ".join(hyperlinks))

    def emitUnitHeaders(self, node, layers='core'):
        """Write out the HTML page headers for this node."""
        self.write("<h1 property=\"rdfs:label\" class=\"page-title\">")
        self.write(node.id)
        self.write("</h1>\n")
        home = node.home
        if home != "core" and home != "":
            if home == ATTIC:
                self.write("Defined in the %s.schema.org archive area.<br/><strong>Use of this term is not advised</strong><br/>" % home)
            else:
                self.write("Defined in the %s.schema.org extension.<br/>" % home)
        self.emitCanonicalURL(node)

        self.BreadCrumbs(node, layers=layers)

        comment = GetComment(node, layers)

        self.write(" <div property=\"rdfs:comment\">%s</div>\n\n" % (comment) + "\n")

        self.write(" <br/><div>Usage: %s</div>\n\n" % (node.UsageStr()) + "\n")

        #was:        self.write(self.moreInfoBlock(node))

        if (node.isClass(layers=layers) and not node.isDataType(layers=layers) and node.id != "DataType"):
            self.write("<table class=\"definition-table\">\n        <thead>\n  <tr><th>Property</th><th>Expected Type</th><th>Description</th>               \n  </tr>\n  </thead>\n\n")

    def emitCanonicalURL(self,node):
        cURL = "http://schema.org/" + node.id
        self.write(" <span class=\"canonicalUrl\">Canonical URL: <a href=\"%s\">%s</a></span>" % (cURL, cURL))

    # Stacks to support multiple inheritance
    crumbStacks = []
    def BreadCrumbs(self, node, layers):
        self.crumbStacks = []
        cstack = []
        self.crumbStacks.append(cstack)
        self.WalkCrumbs(node,cstack,layers=layers)
        if (node.isAttribute(layers=layers)):
            cstack.append(Unit.GetUnit("Property"))
            cstack.append(Unit.GetUnit("Thing"))
        elif(node.isDataType(layers=layers) and node.id != "DataType"):
            cstack.append(Unit.GetUnit("DataType"))
            

        enuma = node.isEnumerationValue(layers=layers)

        crumbsout = []
        for row in range(len(self.crumbStacks)):
           thisrow = ""
           if(":" in self.crumbStacks[row][len(self.crumbStacks[row])-1].id):
                continue
           count = 0
           while(len(self.crumbStacks[row]) > 0):
                propertyval = None
                n = self.crumbStacks[row].pop()
                
                if((len(self.crumbStacks[row]) == 1) and 
                    not ":" in n.id) : #penultimate crumb that is not a non-schema reference
                    if node.isAttribute(layers=layers):
                        if n.isAttribute(layers=layers): #Can only be a subproperty of a property
                            propertyval = "rdfs:subPropertyOf"
                    else:
                        propertyval = "rdfs:subClassOf"  
                
                if(count > 0):
                    if((len(self.crumbStacks[row]) == 0) and enuma): #final crumb
                        thisrow += " :: "
                    else:
                        thisrow += " &gt; "
                elif n.id == "Class": # If Class is first breadcrum suppress it
                        continue
                count += 1
                thisrow += "%s" % (self.ml(n,prop=propertyval))
           crumbsout.append(thisrow)

        self.write("<h4>")
        rowcount = 0
        for crumb in sorted(crumbsout):
           if rowcount > 0:
               self.write("<br/>")
           self.write("<span class='breadcrumbs'>%s</span>\n" % crumb)
           rowcount += 1
        self.write("</h4>\n")

#Walk up the stack, appending crumbs & create new (duplicating crumbs already identified) if more than one parent found
    def WalkCrumbs(self, node, cstack, layers):
        if "http://" in node.id or "https://" in node.id:  #Suppress external class references
            return

        cstack.append(node)
        tmpStacks = []
        tmpStacks.append(cstack)
        subs = []

        if(node.isDataType(layers=layers)):
            #subs = GetTargets(Unit.GetUnit("rdf:type"), node, layers=layers)
            subs += GetTargets(Unit.GetUnit("rdfs:subClassOf"), node, layers=layers)
        elif node.isClass(layers=layers):
            subs = GetTargets(Unit.GetUnit("rdfs:subClassOf"), node, layers=layers)
        elif(node.isAttribute(layers=layers)):
            subs = GetTargets(Unit.GetUnit("rdfs:subPropertyOf"), node, layers=layers)
        else:
            subs = GetTargets(Unit.GetUnit("rdf:type"), node, layers=layers)# Enumerations are classes that have no declared subclasses

        for i in range(len(subs)):
            if(i > 0):
                t = cstack[:]
                tmpStacks.append(t)
                self.crumbStacks.append(t)
        x = 0
        for p in subs:
            self.WalkCrumbs(p,tmpStacks[x],layers=layers)
            x += 1


    def emitSimplePropertiesPerType(self, cl, layers="core", out=None, hashorslash="/"):
        """Emits a simple list of properties applicable to the specified type."""

        if not out:
            out = self

        out.write("<ul class='props4type'>")
        for prop in sorted(GetSources(  Unit.GetUnit("domainIncludes"), cl, layers=layers), key=lambda u: u.id):
            if (prop.superseded(layers=layers)):
                continue
            out.write("<li><a href='%s%s'>%s</a></li>" % ( hashorslash, prop.id, prop.id  ))
        out.write("</ul>\n\n")

    def emitSimplePropertiesIntoType(self, cl, layers="core", out=None, hashorslash="/"):
        """Emits a simple list of properties whose values are the specified type."""

        if not out:
            out = self

        out.write("<ul class='props2type'>")
        for prop in sorted(GetSources(  Unit.GetUnit("rangeIncludes"), cl, layers=layers), key=lambda u: u.id):
            if (prop.superseded(layers=layers)):
                continue
            out.write("<li><a href='%s%s'>%s</a></li>" % ( hashorslash, prop.id, prop.id  ))
        out.write("</ul>\n\n")

    def ClassProperties (self, cl, subclass=False, layers="core", out=None, hashorslash="/"):
        """Write out a table of properties for a per-type page."""
        if not out:
            out = self

        propcount = 0

        headerPrinted = False
        di = Unit.GetUnit("domainIncludes")
        ri = Unit.GetUnit("rangeIncludes")

        for prop in sorted(GetSources(di, cl, layers=layers), key=lambda u: u.id):
            if (prop.superseded(layers=layers)):
                continue
            olderprops = prop.supersedes_all(layers=layers)
            inverseprop = prop.inverseproperty(layers=layers)
            ranges = sorted(GetTargets(ri, prop, layers=layers),key=lambda u: u.id)
            doms = sorted(GetTargets(di, prop, layers=layers), key=lambda u: u.id)
            comment = GetComment(prop, layers=layers)
            if (not headerPrinted):
                class_head = self.ml(cl)
                if subclass:
                    class_head = self.ml(cl)
                out.write("<tr class=\"supertype\">\n     <th class=\"supertype-name\" colspan=\"3\">Properties from %s</th>\n  \n</tr>\n\n<tbody class=\"supertype\">\n  " % (class_head))
                headerPrinted = True

            out.write("<tr typeof=\"rdfs:Property\" resource=\"http://schema.org/%s\">\n    \n      <th class=\"prop-nam\" scope=\"row\">\n\n<code property=\"rdfs:label\">%s</code>\n    </th>\n " % (prop.id, self.ml(prop)))
            out.write("<td class=\"prop-ect\">\n")
            first_range = True
            for r in sorted(ranges,key=lambda u: u.id):
                if (not first_range):
                    out.write(" or <br/> ")
                first_range = False
                out.write(self.ml(r, prop='rangeIncludes'))
                out.write("&nbsp;")
            for d in doms:
                out.write("<link property=\"domainIncludes\" href=\"http://schema.org/%s\">" % d.id)
            out.write("</td>")
            out.write("<td class=\"prop-desc\" property=\"rdfs:comment\">%s" % (comment))
            if (olderprops and len(olderprops) > 0):
                olderprops = sorted(olderprops,key=lambda u: u.id)
                olderlinks = ", ".join([self.ml(o) for o in olderprops])
                out.write(" Supersedes %s." % olderlinks )
            if (inverseprop != None):
                out.write("<br/> Inverse property: %s." % (self.ml(inverseprop)))

            out.write("</td></tr>")
            subclass = False
            propcount += 1

        if subclass: # in case the superclass has no defined attributes
            out.write("<tr><td colspan=\"3\"></td></tr>")

        return propcount

    def emitClassExtensionSuperclasses (self, cl, layers="core", out=None):
       first = True
       count = 0
       if not out:
           out = self

       buff = StringIO.StringIO()
       sc = Unit.GetUnit("rdfs:subClassOf")

       for p in GetTargets(sc, cl, ALL_LAYERS):

          if inLayer(layers,p):
               continue

          if p.id == "http://www.w3.org/2000/01/rdf-schema#Class": #Special case for "DataType"
              p.id = "Class"

          sep = ", "
          if first:
            sep = "<li>"
            first = False

          buff.write("%s%s" % (sep,self.ml(p)))
          count += 1

          if(count > 0):
            buff.write("</li>\n")

       content = buff.getvalue()
       if(len(content) > 0):
           if cl.id == "DataType":
               self.write("<h4>Subclass of:<h4>")
           else:
               self.write("<h4>Available supertypes defined in extensions</h4>")
           self.write("<ul>")
           self.write(content)
           self.write("</ul>")
       buff.close()

    def emitClassExtensionProperties (self, cl, layers="core", out=None):
       if not out:
           out = self

       buff = StringIO.StringIO()

       for p in self.parentStack:
           self._ClassExtensionProperties(buff, p, layers=layers)

       content = buff.getvalue()
       if(len(content) > 0):
           self.write("<h4>Available properties in extensions</h4>")
           self.write("<ul>")
           self.write(content)
           self.write("</ul>")
       buff.close()

    def _ClassExtensionProperties (self, out, cl, layers="core"):
        """Write out a list of properties not displayed as they are in extensions for a per-type page."""

        di = Unit.GetUnit("domainIncludes")

        targetlayers=self.appropriateLayers(layers)
        #log.info("Appropriate targets %s" % targetlayers)
        exts = {}

        for prop in sorted(GetSources(di, cl, targetlayers), key=lambda u: u.id):
            if (prop.superseded(layers=targetlayers)):
                continue
            if inLayer(layers,prop): #Already in the correct layer - no need to report
                continue
            if inLayer("meta",prop): #Suppress mentioning properties from the 'meta' extension.
                continue
            ext = prop.getHomeLayer()
            log.debug("ClassExtensionFound %s from %s" % (prop, ext))
            if not ext in exts.keys():
                exts[ext] = []
            exts[ext].append(prop)

        for e in sorted(exts.keys()):
            count = 0
            first = True
            for p in sorted(exts[e], key=lambda u: u.id):
                sep = ", "
                if first:
                    out.write("<li>For %s in the <a href=\"%s\">%s</a> extension:  " % (self.ml(cl),makeUrl(e,""),e))
                    sep = ""
                    first = False

                out.write("%s%s" % (sep,self.ml(p)))
                count += 1
            if(count > 0):
                out.write("</li>\n")


    def emitClassIncomingProperties (self, cl, layers="core", out=None, hashorslash="/"):
        """Write out a table of incoming properties for a per-type page."""
        if not out:
            out = self
            
        targetlayers=self.appropriateLayers(layers) # Show incomming properties from all layers

        headerPrinted = False
        di = Unit.GetUnit("domainIncludes")
        ri = Unit.GetUnit("rangeIncludes")
        #log.info("Incomming for %s" % cl.id)
        for prop in sorted(GetSources(ri, cl, layers=layers), key=lambda u: u.id):
            if (prop.superseded(layers=layers)):
                continue
            supersedes = prop.supersedes(layers=targetlayers)
            inverseprop = prop.inverseproperty(layers=targetlayers)
            ranges = sorted(GetTargets(di, prop, layers=targetlayers),key=lambda u: u.id)
            comment = GetComment(prop, layers=targetlayers)

            if (not headerPrinted):
                self.write("<br/><br/><div id=\"incoming\">Instances of %s may appear as values for the following properties</div><br/>" % (self.ml(cl)))
                self.write("<table class=\"definition-table\">\n        \n  \n<thead>\n  <tr><th>Property</th><th>On Types</th><th>Description</th>               \n  </tr>\n</thead>\n\n")

                headerPrinted = True

            self.write("<tr>\n<th class=\"prop-nam\" scope=\"row\">\n <code>%s</code>\n</th>\n " % (self.ml(prop)) + "\n")
            self.write("<td class=\"prop-ect\">\n")
            first_range = True
            for r in ranges:
                if (not first_range):
                    self.write(" or<br/> ")
                first_range = False
                self.write(self.ml(r))
                self.write("&nbsp;")
            self.write("</td>")
            self.write("<td class=\"prop-desc\">%s " % (comment))
            if (supersedes != None):
                self.write(" Supersedes %s." % (self.ml(supersedes)))
            if (inverseprop != None):
                self.write("<br/> inverse property: %s." % (self.ml(inverseprop)) )

            self.write("</td></tr>")
        if (headerPrinted):
            self.write("</table>\n")


    def emitRangeTypesForProperty(self, node, layers="core", out=None, hashorslash="/"):
        """Write out simple HTML summary of this property's expected types."""
        if not out:
            out = self

        out.write("<ul class='attrrangesummary'>")
        for rt in sorted(GetTargets(Unit.GetUnit("rangeIncludes"), node, layers=layers), key=lambda u: u.id):
            out.write("<li><a href='%s%s'>%s</a></li>" % ( hashorslash, rt.id, rt.id  ))
        out.write("</ul>\n\n")


    def emitDomainTypesForProperty(self, node, layers="core", out=None, hashorslash="/"):
        """Write out simple HTML summary of types that expect this property."""
        if not out:
            out = self

        out.write("<ul class='attrdomainsummary'>")
        for dt in sorted(GetTargets(Unit.GetUnit("domainIncludes"), node, layers=layers), key=lambda u: u.id):
            out.write("<li><a href='%s%s'>%s</a></li>" % ( hashorslash, dt.id, dt.id  ))
        out.write("</ul>\n\n")



    def emitAttributeProperties(self, node, layers="core", out=None, hashorslash="/"):
        """Write out properties of this property, for a per-property page."""
        if not out:
            out = self
        targetLayers = self.appropriateLayers(layers)
        di = Unit.GetUnit("domainIncludes")
        ri = Unit.GetUnit("rangeIncludes")
        rges = sorted(GetTargets(ri, node, layers=targetLayers), key=lambda u: u.id)
        doms = sorted(GetTargets(di, node, layers=targetLayers), key=lambda u: u.id)
        ranges = []
        eranges = []
        for r in rges:
            if inLayer(layers, r):
                ranges.append(r)
            else:
                eranges.append(r) 
        domains = []
        edomains = []
        for d in doms:
            if inLayer(layers, d):
                domains.append(d)
            else:
                edomains.append(d) 

        inverseprop = node.inverseproperty(layers=targetLayers)
        subprops = sorted(node.subproperties(layers=targetLayers),key=lambda u: u.id)
        superprops = sorted(node.superproperties(layers=targetLayers),key=lambda u: u.id)


        if (inverseprop != None):
            tt = "This means the same thing, but with the relationship direction reversed."
            out.write("<p>Inverse-property: %s.</p>" % (self.ml(inverseprop, inverseprop.id,tt, prop=False, hashorslash=hashorslash)) )

        out.write("<table class=\"definition-table\">\n")
        out.write("<thead>\n  <tr>\n    <th>Values expected to be one of these types</th>\n  </tr>\n</thead>\n\n  <tr>\n    <td>\n      ")

        first_range = True
        for r in ranges:
            if (not first_range):
                out.write("<br/>")
            first_range = False
            tt = "The '%s' property has values that include instances of the '%s' type." % (node.id, r.id)
            out.write(" <code>%s</code> " % (self.ml(r, r.id, tt, prop="rangeIncludes", hashorslash=hashorslash) +"\n"))
        out.write("    </td>\n  </tr>\n</table>\n\n")

        if len(eranges) > 0:
            first_range = True
            out.write("<table class=\"definition-table\">\n")
            out.write("  <thead>\n    <tr>\n      <th>Expected values defined in extensions</th>\n    </tr>\n</thead>\n<tr>\n  <td>")
            for r in eranges:
                if (not first_range):
                    out.write("<br/>")
                first_range = False
                defin = "defined in the <a href=\"%s\">%s</a> extension" % (makeUrl(r.getHomeLayer(),""),r.getHomeLayer())
                tt = "The '%s' property has values that include instances of the '%s' type." % (node.id, r.id)
                out.write("\n    <code>%s</code> - %s" % (self.ml(r, r.id, tt, prop="domainIncludes",hashorslash=hashorslash),defin ))
            out.write("      </td>\n    </tr>\n</table>\n\n")

        first_domain = True
        out.write("<table class=\"definition-table\">\n")
        out.write("  <thead>\n    <tr>\n      <th>Used on these types</th>\n    </tr>\n</thead>\n<tr>\n  <td>")
        for d in domains:
            if (not first_domain):
                out.write("<br/>")
            first_domain = False
            tt = "The '%s' property is used on the '%s' type." % (node.id, d.id)
            out.write("\n    <code>%s</code> " % (self.ml(d, d.id, tt, prop="domainIncludes",hashorslash=hashorslash)+"\n" ))
        out.write("      </td>\n    </tr>\n</table>\n\n")

        if len(edomains) > 0:
            first_domain = True
            out.write("<table class=\"definition-table\">\n")
            out.write("  <thead>\n    <tr>\n      <th>Used on types defined in extensions</th>\n    </tr>\n</thead>\n<tr>\n  <td>")
            for d in edomains:
                if (not first_domain):
                    out.write("<br/>")
                first_domain = False
                defin = "defined in the <a href=\"%s\">%s</a> extension" % (makeUrl(d.getHomeLayer(),""),d.getHomeLayer())
                tt = "The '%s' property is used on the '%s' type." % (node.id, d.id)
                out.write("\n    <code>%s</code> - %s" % (self.ml(d, d.id, tt, prop="domainIncludes",hashorslash=hashorslash),defin ))
            out.write("      </td>\n    </tr>\n</table>\n\n")

        # Sub-properties
        if (subprops != None and len(subprops) > 0):
            out.write("<table class=\"definition-table\">\n")
            out.write("  <thead>\n    <tr>\n      <th>Sub-properties</th>\n    </tr>\n</thead>\n")
            for sp in subprops:
                c = ShortenOnSentence(StripHtmlTags( GetComment(sp,layers=layers) ),60)
                tt = "%s: ''%s''" % ( sp.id, c)
                out.write("\n    <tr><td><code>%s</code></td></tr>\n" % (self.ml(sp, sp.id, tt, hashorslash=hashorslash)))
            out.write("\n</table>\n\n")

        # Super-properties
        if (superprops != None and  len(superprops) > 0):
            out.write("<table class=\"definition-table\">\n")
            out.write("  <thead>\n    <tr>\n      <th>Super-properties</th>\n    </tr>\n</thead>\n")
            for sp in superprops:
                c = ShortenOnSentence(StripHtmlTags( GetComment(sp,layers=layers) ),60)
                tt = "%s: ''%s''" % ( sp.id, c)
                out.write("\n    <tr><td><code>%s</code></td></tr>\n" % (self.ml(sp, sp.id, tt, hashorslash=hashorslash)))
            out.write("\n</table>\n\n")

        self.emitSupersedes(node,layers=layers,out=out,hashorslash=hashorslash)

    def emitSupersedes(self, node, layers="core", out=None, hashorslash="/"):
        """Write out Supersedes and/or Superseded by for this term"""

        if not out:
            out = self
        newerprop = node.supersededBy(layers=layers) # None of one. e.g. we're on 'seller'(new) page, we get 'vendor'(old)
        #olderprop = node.supersedes(layers=layers) # None or one
        olderprops = sorted(node.supersedes_all(layers=layers),key=lambda u: u.id) # list, e.g. 'seller' has 'vendor', 'merchant'.


        # Supersedes
        if (olderprops != None and len(olderprops) > 0):
            out.write("<table class=\"definition-table\">\n")
            out.write("  <thead>\n    <tr>\n      <th>Supersedes</th>\n    </tr>\n</thead>\n")

            for o in olderprops:
                c = ShortenOnSentence(StripHtmlTags( GetComment(o,layers=layers) ),60)
                tt = "%s: ''%s''" % ( o.id, c)
                out.write("\n    <tr><td><code>%s</code></td></tr>\n" % (self.ml(o, o.id, tt)))
                log.info("Super %s" % o.id)
            out.write("\n</table>\n\n")

        # supersededBy (at most one direct successor)
        if (newerprop != None):
            out.write("<table class=\"definition-table\">\n")
            out.write("  <thead>\n    <tr>\n      <th><a href=\"/supersededBy\">supersededBy</a></th>\n    </tr>\n</thead>\n")
            c = ShortenOnSentence(StripHtmlTags( GetComment(newerprop,layers=layers) ),60)
            tt = "%s: ''%s''" % ( newerprop.id, c)
            out.write("\n    <tr><td><code>%s</code></td></tr>\n" % (self.ml(newerprop, newerprop.id, tt)))
            out.write("\n</table>\n\n")

    def rep(self, markup):
        """Replace < and > with HTML escape chars."""
        m1 = re.sub("<", "&lt;", markup)
        m2 = re.sub(">", "&gt;", m1)
        # TODO: Ampersand? Check usage with examples.
        return m2

    def handleHomepage(self, node):
        """Send the homepage, or if no HTML accept header received and JSON-LD was requested, send JSON-LD context file.

        typical browser accept list: ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8')
        # e.g. curl -H "Accept: application/ld+json" http://localhost:8080/
        see also http://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html
        https://github.com/rvguha/schemaorg/issues/5
        https://github.com/rvguha/schemaorg/wiki/JsonLd
        """
        accept_header = self.request.headers.get('Accept')
        if accept_header:
            accept_header = accept_header.split(',')
        else:
            accept_header = ""

        # Homepage is content-negotiated. HTML or JSON-LD.
        mimereq = {}
        for ah in accept_header:
            ah = re.sub( r";q=\d?\.\d+", '', ah).rstrip()
            mimereq[ah] = 1

        html_score = mimereq.get('text/html', 5)
        xhtml_score = mimereq.get('application/xhtml+xml', 5)
        jsonld_score = mimereq.get('application/ld+json', 10)
        # print "accept_header: " + str(accept_header) + " mimereq: "+str(mimereq) + "Scores H:{0} XH:{1} J:{2} ".format(html_score,xhtml_score,jsonld_score)

        if (ENABLE_JSONLD_CONTEXT and (jsonld_score < html_score and jsonld_score < xhtml_score)):
            self.response.set_status(302,"Found")
            self.response.headers['Location'] = makeUrl("","docs/jsonldcontext.json")
            self.emitCacheHeaders()
            return False #don't cache this redirect
        else:
            # Serve a homepage from template
            # the .tpl has responsibility for extension homepages
            # TODO: pass in extension, base_domain etc.
            sitekeyedhomepage = "homepage %s" % getSiteName()
            hp = getPageFromStore(sitekeyedhomepage)
            self.response.headers['Content-Type'] = "text/html"
            self.emitCacheHeaders()
            if hp != None:
                self.response.out.write( hp )
                #log.info("Served datacache homepage.tpl key: %s" % sitekeyedhomepage)
            else:


                template_values = {
                    'ext_contents': self.handleExtensionContents(getHostExt()),
                    'home_page': "True",
                }
                page = templateRender('homepage.tpl',template_values)
                self.response.out.write( page )
                log.debug("Served and cached fresh homepage.tpl key: %s " % sitekeyedhomepage)
                #log.info("Served and cached fresh homepage.tpl key: %s " % sitekeyedhomepage)
                PageStore.put(sitekeyedhomepage, page)
                #            self.response.out.write( open("static/index.html", 'r').read() )
            return False # - Not caching homepage 
        log.info("Warning: got here how?")
        return False

    def getExtendedSiteName(self, layers):
        """Returns site name (domain name), informed by the list of active layers."""
        if layers==["core"]:
            return "schema.org"
        if not layers or len(layers)==0:
            return "schema.org"
        return (getHostExt() + ".schema.org")

    def emitSchemaorgHeaders(self, node, ext_mappings='', sitemode="default", sitename="schema.org", layers="core"):
        """
        Generates, caches and emits HTML headers for class, property and enumeration pages. Leaves <body> open.

        * entry = name of the class or property
        """
        rdfs_type = 'rdfs:Property'
        anode = True
        if isinstance(node, str):
            entry = node
            anode = False
        else:
            entry = node.id

            if node.isEnumeration():
                rdfs_type = 'rdfs:Class'
            elif node.isEnumerationValue():
                rdfs_type = ""
                nodeTypes = GetTargets(Unit.GetUnit("rdf:type"), node, layers=layers)
                typecount = 0
                for type in nodeTypes:
                     if typecount > 0:
                         rdfs_type += " "
                     rdfs_type += type.id
                     typecount += 1

            elif node.isClass():
                rdfs_type = 'rdfs:Class'
            elif node.isAttribute():
                rdfs_type = 'rdfs:Property'

        generated_page_id = "genericTermPageHeader-%s-%s" % ( str(entry), getSiteName() )
        gtp = DataCache.get( generated_page_id )

        if gtp != None:
            self.response.out.write( gtp )
            log.debug("Served recycled genericTermPageHeader.tpl for %s" % generated_page_id )
        else:

            desc = entry
            if anode:
                desc = self.getMetaDescription(node, layers=layers, lengthHint=200)

            template_values = {
                'entry': str(entry),
                'desc' : desc,
                'menu_sel': "Schemas",
                'rdfs_type': rdfs_type,
                'ext_mappings': ext_mappings
            }
            out = templateRender('genericTermPageHeader.tpl',template_values)
            DataCache.put(generated_page_id, out)
            log.debug("Served and cached fresh genericTermPageHeader.tpl for %s" % generated_page_id )

            self.response.write(out)

    def getMetaDescription(self, node, layers="core",lengthHint=250):
        ins = ""
        if node.isEnumeration():
            ins += " Enumeration Type"
        elif node.isClass():
            ins += " Type"
        elif node.isAttribute():
            ins += " Property"
        elif node.isEnumerationValue():
            ins += " Enumeration Value"

        desc = "Schema.org%s: %s - " % (ins, node.id)

        lengthHint -= len(desc)

        comment = GetComment(node, layers)

        desc += ShortenOnSentence(StripHtmlTags(comment),lengthHint)

        return desc

    def appropriateLayers(self,layers="core"):
        if ATTIC in layers:
            return ALL_LAYERS
        return ALL_LAYERS_NO_ATTIC

    def emitExactTermPage(self, node, layers="core"):
        """Emit a Web page that exactly matches this node."""
        log.debug("EXACT PAGE: %s" % node.id)
        self.outputStrings = [] # blank slate
        ext_mappings = GetExtMappingsRDFa(node, layers=layers)

        global sitemode #,sitename
        if ("schema.org" not in self.request.host and sitemode == "mainsite"):
            sitemode = "mainsite testsite"

        self.emitSchemaorgHeaders(node, ext_mappings, sitemode, getSiteName(), layers)

        cached = getPageFromStore(node.id)
            
        if (cached != None):
            log.info("GOT CACHED page for %s" % node.id)
            self.response.write(cached)
            return
        self.parentStack = []
        self.GetParentStack(node, layers=layers)

        self.emitUnitHeaders(node,  layers=layers) # writes <h1><table>...

        if (node.isEnumerationValue(layers=layers)):
            self.write(self.moreInfoBlock(node))

        if (node.isClass(layers=layers)):
            subclass = True
            self.write(self.moreInfoBlock(node))

            for p in self.parentStack:
                self.ClassProperties(p, p==self.parentStack[0], layers=layers)
            if (not node.isDataType(layers=layers) and node.id != "DataType"):
                self.write("\n\n</table>\n\n")
            self.emitClassIncomingProperties(node, layers=layers)

            self.emitClassExtensionSuperclasses(node,layers)

            self.emitClassExtensionProperties(p,layers)

            self.emitSupersedes(node,layers=layers)


        elif (Unit.isAttribute(node, layers=layers)):
            self.write(self.moreInfoBlock(node))
            self.emitAttributeProperties(node, layers=layers)

        if (node.isClass(layers=layers)):
            children = []
            children = GetSources(Unit.GetUnit("rdfs:subClassOf"), node, self.appropriateLayers(layers))# Normal subclasses
            if(node.isDataType() or node.id == "DataType"):
                children += GetSources(Unit.GetUnit("rdf:type"), node, self.appropriateLayers(layers))# Datatypes
            children = sorted(children, key=lambda u: u.id)

            if (len(children) > 0):
                buff = StringIO.StringIO()
                extbuff = StringIO.StringIO()

                firstext=True
                for c in children:
                    if c.superseded(layers=layers):
                        continue
                    if inLayer(layers, c):
                        buff.write("<li> %s </li>" % (self.ml(c)))
                    else:
                        sep = ", "
                        if firstext:
                            sep = ""
                            firstext=False
                        extbuff.write("%s%s" % (sep,self.ml(c)) )

                if (len(buff.getvalue()) > 0):
                    if node.isDataType():
                        self.write("<br/><b>More specific DataTypes</b><ul>")
                    else:
                        self.write("<br/><b>More specific Types</b><ul>")
                    self.write(buff.getvalue())
                    self.write("</ul>")

                if (len(extbuff.getvalue()) > 0):
                    self.write("<h4>More specific Types available in extensions</h4><ul><li>")
                    self.write(extbuff.getvalue())
                    self.write("</li></ul>")
                buff.close()
                extbuff.close()

        if (node.isEnumeration(layers=layers)):

            children = sorted(GetSources(Unit.GetUnit("rdf:type"), node, self.appropriateLayers(layers)), key=lambda u: u.id)
            if (len(children) > 0):
                buff = StringIO.StringIO()
                extbuff = StringIO.StringIO()

                firstext=True
                for c in children:
                    if inLayer(layers, c):
                        buff.write("<li> %s </li>" % (self.ml(c)))
                    else:
                        sep = ","
                        if firstext:
                            sep = ""
                            firstext=False
                        extbuff.write("%s%s" % (sep,self.ml(c)) )

                if (len(buff.getvalue()) > 0):
                    self.write("<br/><br/><b>Enumeration members</b><ul>")
                    self.write(buff.getvalue())
                    self.write("</ul>")

                if (len(extbuff.getvalue()) > 0):
                    self.write("<h4>Enumeration members available in extensions</h4><ul><li>")
                    self.write(extbuff.getvalue())
                    self.write("</li></ul>")
                buff.close()
                extbuff.close()

        ackorgs = GetTargets(Unit.GetUnit("dc:source"), node, layers=layers)
        if (len(ackorgs) > 0):
            sources = []
            acknowledgements =[]
            for ao in ackorgs:
                acks = sorted(GetTargets(Unit.GetUnit("rdfs:comment"), ao, layers))
                if len(acks) == 0:
                    val = str(ao)
                    if val.startswith("http://") or val.startswith("https://"):
                        val = "[%s](%s)" % (val,val) #Put into markdown format
                    sources.append(val)
                else:
                    for ack in acks:
                        acknowledgements.append(ack)

            if len(sources) > 0:
                s = ""
                if len(sources) > 1:
                    s = "s"
                self.write("<h4  id=\"acks\">Source%s</h4>\n" % s)
                for so in sorted(sources):
                    self.write(Markdown.parse(so,True))
            if len(acknowledgements) > 0:
                s = ""
                if len(acknowledgements) > 1:
                    s = "s"
                self.write("<h4  id=\"acks\">Acknowledgement%s</h4>\n" % s)
                for ack in sorted(acknowledgements):
                    self.write(Markdown.parse(str(ack),True))

        examples = GetExamples(node, layers=layers)
        log.debug("Rendering n=%s examples" % len(examples))
        if (len(examples) > 0):
            example_labels = [
              ('Without Markup', 'original_html', 'selected'),
              ('Microdata', 'microdata', ''),
              ('RDFa', 'rdfa', ''),
              ('JSON-LD', 'jsonld', ''),
            ]
            self.write("<br/><br/><b><a id=\"examples\">Examples</a></b><br/><br/>\n\n")
            exNum = 0
            for ex in sorted(examples, key=lambda u: u.keyvalue):
                
                if not ex.egmeta["layer"] in layers: #Example defined in extension we are not in
                    continue
                exNum += 1
                id="example-%s" % exNum
                if "id" in ex.egmeta:
                    id = ex.egmeta["id"]
                self.write("<div title=\"%s\"><a id=\"%s\">Example %s</a></div>" % (id,id,exNum))
                self.write("<div class='ds-selector-tabs ds-selector'>\n")
                self.write("  <div class='selectors'>\n")
                for label, example_type, selected in example_labels:
                    self.write("    <a data-selects='%s' class='%s'>%s</a>\n"
                               % (example_type, selected, label))
                self.write("</div>\n\n")
                for label, example_type, selected in example_labels:
                    self.write("<pre class=\"prettyprint lang-html linenums %s %s\">%s</pre>\n\n"
                               % (example_type, selected, self.rep(ex.get(example_type))))
                self.write("</div>\n\n")

        self.write("<p class=\"version\"><b>Schema Version %s</b></p>\n\n" % SCHEMA_VERSION)
        # TODO: add some version info regarding the extension

        # Analytics
	self.write("""<script>(function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
	  (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
	  m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
	  })(window,document,'script','//www.google-analytics.com/analytics.js','ga');
	  ga('create', 'UA-52672119-1', 'auto');ga('send', 'pageview');</script>""")

        self.write(" \n\n</div>\n</body>\n</html>")
        
        page = "".join(self.outputStrings)
        PageStore.put(node.id,page)

#        self.response.write(self.AddCachedText(node, self.outputStrings, layers))
        self.response.write(page)

    def emitHTTPHeaders(self, node):
        if ENABLE_CORS:
            self.response.headers.add_header("Access-Control-Allow-Origin", "*") # entire site is public.
            # see http://en.wikipedia.org/wiki/Cross-origin_resource_sharing

    def setupExtensionLayerlist(self, node):
        # Identify which extension layer(s) are requested
        # TODO: add subdomain support e.g. bib.schema.org/Globe
        # instead of Globe?ext=bib which is more for debugging.

        # 1. get a comma list from ?ext=foo,bar URL notation
        extlist = cleanPath( self.request.get("ext")  )# for debugging
        extlist = re.sub(ext_re, '', extlist).split(',')
        log.debug("?ext= extension list: %s " % ", ".join(extlist))

        # 2. Ignore ?ext=, start with 'core' only.
        layerlist = [ "core"]

        # 3. Use host_ext if set, e.g. 'bib' from bib.schema.org
        if getHostExt() != None:
            log.debug("Host: %s host_ext: %s" % ( self.request.host , getHostExt() ) )
            extlist.append(getHostExt())

        # Report domain-requested extensions
        for x in extlist:
            log.debug("Ext filter found: %s" % str(x))
            if x  in ["core", "localhost", ""]:
                continue
            layerlist.append("%s" % str(x))
        layerlist = list(set(layerlist))   # dedup
        #log.info("layerlist: %s" % layerlist)
        return layerlist

    def handleJSONContext(self, node):
        """Handle JSON-LD Context non-homepage requests (including refuse if not enabled)."""

        if not ENABLE_JSONLD_CONTEXT:
            self.error(404)
            self.response.out.write('<title>404 Not Found.</title><a href="/">404 Not Found (JSON-LD Context not enabled.)</a><br/><br/>')
            return True
            
        jsonldcontext = ""
        if getPageFromStore("JSONLDCONTEXT"):
            jsonldcontext = getPageFromStore("JSONLDCONTEXT")
        else:
            jsonldcontext = GetJsonLdContext(layers=ALL_LAYERS)
            PageStore.put("JSONLDCONTEXT",jsonldcontext)
            
        if (node=="docs/jsonldcontext.json.txt"):
            self.response.headers['Content-Type'] = "text/plain"
            self.emitCacheHeaders()
            self.response.out.write( jsonldcontext )
            return True
        if (node=="docs/jsonldcontext.json"):
            self.response.headers['Content-Type'] = "application/ld+json"
            self.emitCacheHeaders()
            self.response.out.write( jsonldcontext )
            return True
        return False
        # see also handleHomepage for conneg'd version.

    def handleSchemasPage(self, node,  layerlist='core'):
        self.response.headers['Content-Type'] = "text/html"
        self.emitCacheHeaders()

        if getPageFromStore('SchemasPage'):
            self.response.out.write( getPageFromStore('SchemasPage') )
            log.debug("Serving recycled SchemasPage.")
            return True
        else:
            extensions = []
            for ex in sorted(ENABLED_EXTENSIONS):
                if ex != ATTIC:
                    extensions.append("<a href=\"%s\">%s.schema.org</a>" % (makeUrl(ex,""),ex))

            page = templateRender('schemas.tpl',{'counts': self.getCounts(),
                                    'extensions': extensions,
                                    'attic': "<a href=\"%s\">%s.schema.org</a>" % (makeUrl(ATTIC,""),ATTIC),
                                    'menu_sel': "Schemas"})

            self.response.out.write( page )
            log.debug("Serving fresh SchemasPage.")
            PageStore.put("SchemasPage",page)

            return True

    def handleDumpsPage(self, node,  layerlist='core'):
        self.response.headers['Content-Type'] = "text/html"
        self.emitCacheHeaders()

        if getPageFromStore('DumpsPage'):
            self.response.out.write( getPageFromStore('DumpsPage') )
            log.debug("Serving recycled DumpsPage.")
            return True
        else:
            extensions = sorted(ENABLED_EXTENSIONS)

            page = templateRender('developers.tpl',{'extensions': extensions,
                                    'version': SCHEMA_VERSION,
                                    'menu_sel': "Schemas"})

            self.response.out.write( page )
            log.debug("Serving fresh DumpsPage.")
            PageStore.put("DumpsPage",page)

            return True

    def getCounts(self):
        typesCount = getPageFromStore('typesCount-core')
        if not typesCount:
            typesCount = str(countTypes(extension="core"))
            PageStore.put('typesCount-core',typesCount)

        propsCount = getPageFromStore('propsCount-core')
        if not propsCount:
            propsCount = str(countProperties(extension="core"))
            PageStore.put('propsCount-core',propsCount)

        enumCount = getPageFromStore('enumCount-core')
        if not enumCount:
            enumCount = str(countEnums(extension="core"))
            PageStore.put('enumCount-core',enumCount)

        text = ""
        text += "The core vocabulary currently consists of %s Types, " % typesCount
        text += " %s Properties, " % propsCount
        text += "and %s Enumeration values." % enumCount
        return text


    def handleFullHierarchyPage(self, node,  layerlist='core'):
        self.response.headers['Content-Type'] = "text/html"
        self.emitCacheHeaders()

        if getPageFromStore('FullTreePage'):
            self.response.out.write( getPageFromStore('FullTreePage') )
            log.debug("Serving recycled FullTreePage.")
            return True
        else:
            template = JINJA_ENVIRONMENT.get_template('full.tpl')


            extlist=""
            extonlylist=[]
            count=0
            for i in layerlist:
                if i != "core":
                    sep = ""
                    if count > 0:
                        sep = ", "
                    extlist += "'%s'%s" % (i, sep)
                    extonlylist.append(i)
                    count += 1
            local_button = ""
            local_label = "<h3>Core plus %s extension vocabularies</h3>" % extlist
            if count == 0:
                local_button = "Core vocabulary"
            elif count == 1:
                local_button = "Core plus %s extension" % extlist
            else:
                local_button = "Core plus %s extensions" % extlist

            ext_button = ""
            if count == 1:
                ext_button = "Extension %s" % extlist
            elif count > 1:
                ext_button = "Extensions %s" % extlist


            uThing = Unit.GetUnit("Thing")
            uDataType = Unit.GetUnit("DataType")

            mainroot = TypeHierarchyTree(local_label)
            mainroot.traverseForHTML(uThing, layers=layerlist)
            thing_tree = mainroot.toHTML()

            fullmainroot = TypeHierarchyTree("<h3>Core plus all extension vocabularies</h3>")
            fullmainroot.traverseForHTML(uThing, layers=ALL_LAYERS_NO_ATTIC)
            full_thing_tree = fullmainroot.toHTML()

            ext_thing_tree = None
            if len(extonlylist) > 0:
                extroot = TypeHierarchyTree("<h3>Extension: %s</h3>" % extlist)
                extroot.traverseForHTML(uThing, layers=extonlylist, traverseAllLayers=True)
                ext_thing_tree = extroot.toHTML()

            dtroot = TypeHierarchyTree("<h4>Data Types</h4>")
            dtroot.traverseForHTML(uDataType, layers=layerlist)
            datatype_tree = dtroot.toHTML()

            full_button = "Core plus all extensions"

            page = templateRender('full.tpl',{ 'thing_tree': thing_tree,
                                    'full_thing_tree': full_thing_tree,
                                    'ext_thing_tree': ext_thing_tree,
                                    'datatype_tree': datatype_tree,
                                    'local_button': local_button,
                                    'full_button': full_button,
                                    'ext_button': ext_button,
                                    'menu_sel': "Schemas"})

            self.response.out.write( page )
            log.debug("Serving fresh FullTreePage.")
            PageStore.put("FullTreePage",page)

            return True

    def handleJSONSchemaTree(self, node, layerlist='core'):
        """Handle a request for a JSON-LD tree representation of the schemas (RDFS-based)."""

        self.response.headers['Content-Type'] = "application/ld+json"
        self.emitCacheHeaders()

        if getPageFromStore('JSONLDThingTree'):
            self.response.out.write( getPageFromStore('JSONLDThingTree') )
            log.debug("Serving recycled JSONLDThingTree.")
            return True
        else:
            uThing = Unit.GetUnit("Thing")
            mainroot = TypeHierarchyTree()
            mainroot.traverseForJSONLD(Unit.GetUnit("Thing"), layers=layerlist)
            thing_tree = mainroot.toJSON()
            self.response.out.write( thing_tree )
            log.debug("Serving fresh JSONLDThingTree.")
            PageStore.put("JSONLDThingTree",thing_tree)
            return True
        return False

    def checkConneg(self,node):
        accept_header = self.request.headers.get('Accept')
        if accept_header:
            accept_header = accept_header.split(',')
        else:
            accept_header = ""
        target = None
        for ah in accept_header:
            if target:
                break
            ah = re.sub( r";q=\d?\.\d+", '', ah).rstrip()
            log.debug("ACCEPT %s" % ah)
            if ah == "text/html":
                return False
            elif ah == "application/ld+json":
                target = ".jsonld"
            elif ah == "application/x-turtle":
                target = ".ttl"
            elif ah == "application/rdf+xml":
                target = ".rdf"
            elif ah == "text/plain":
                target = ".nt"
            elif ah == "text/csv":
                target = ".csv"
        if target:
            self.response.set_status(303,"See Other")
            self.response.headers['Location'] = makeUrl("","%s%s" % (node,target))
            self.emitCacheHeaders()
            return True
        return False

    def handleExactTermPage(self, node, layers='core'):
        """Handle with requests for specific terms like /Person, /fooBar. """
        dataext = os.path.splitext(node)
        if dataext[1] in OUTPUTDATATYPES:
            ret = self.handleExactTermDataOutput(dataext[0],dataext[1])
            if ret == True:
                return True
        if self.checkConneg(node):
            return True

        self.response.headers['Content-Type'] = "text/html"
        self.emitCacheHeaders()
        schema_node = Unit.GetUnit(node) # e.g. "Person", "CreativeWork".
        if inLayer(layers, schema_node):
            self.emitExactTermPage(schema_node, layers=layers)
            return True
        else:
            # log.info("Looking for node: %s in layers: %s" % (node.id, ",".join(all_layers.keys() )) )
            if not ENABLE_HOSTED_EXTENSIONS:
                return False
            if schema_node is not None and schema_node.id in all_terms:# look for it in other layers
                log.debug("TODO: layer toc: %s" % all_terms[schema_node.id] )
                # self.response.out.write("Layers should be listed here. %s " %  all_terms[node.id] )

                extensions = []
                ext = {}
                ext['href'] = makeUrl(schema_node.getHomeLayer(),schema_node.id)
                ext['text'] = schema_node.getHomeLayer()
                extensions.append(ext)
                    #self.response.out.write("<li><a href='%s'>%s</a></li>" % (makeUrl(x,schema_node.id), x) )

                template = JINJA_ENVIRONMENT.get_template('wrongExt.tpl')
                page = templateRender('wrongExt.tpl',
                                        {'target': schema_node.id,
                                        'extensions': extensions,
                                        'sitename': "schema.org"})

                self.response.out.write( page )
                log.debug("Serving fresh wrongExtPage.")
                return True
            return False

    def handleExactTermDataOutput(self, node=None, outputtype=None):
        log.info("handleExactTermDataOutput Node: '%s'  Outputtype: '%s'" % (node, outputtype))
        ret = False
        file = None
        if node and outputtype:
            schema_node = Unit.GetUnit(node)
            if schema_node:
                ret = True
                index = "%s.%s" % (outputtype,node)
                data = getPageFromStore(index)

                excludeAttic=True
                if getHostExt()== ATTIC:
                    excludeAttic=False
                if outputtype == ".csv":
                    self.response.headers['Content-Type'] = "text/csv; charset=utf-8"
                    if not data:
                        data = self.emitcsvTerm(schema_node,excludeAttic)
                else:
                    format = None
                    if outputtype == ".jsonld":
                        self.response.headers['Content-Type'] = "application/ld+json; charset=utf-8"
                        format = "json-ld"
                    elif outputtype == ".ttl":
                        self.response.headers['Content-Type'] = "application/x-turtle; charset=utf-8"
                        format = "turtle"
                    elif outputtype == ".rdf" or outputtype == ".xml" :
                        self.response.headers['Content-Type'] = "application/rdf+xml; charset=utf-8"
                        format = "pretty-xml"
                    elif outputtype == ".nt":
                        self.response.headers['Content-Type'] = "text/plain; charset=utf-8"
                        format = "nt"
                    
                    if format:
                        if not data:
                            data = serializeSingleTermGrapth(node=node, format=format, excludeAttic=True)
                            PageStore.put(index,data)
                if data:
                    self.emitCacheHeaders()
                    self.response.out.write( data )
                    ret = True
        return ret
        
    def emitcsvTerm(self,schema_node,excludeAttic=True):
        csv = sdordf2csv(queryGraph=getQueryGraph(),fullGraph=getQueryGraph(),markdownComments=True,excludeAttic=excludeAttic)
        file = StringIO.StringIO()
        term = "http://schema.org/" + schema_node.id
        if schema_node.isClass():
            csv.type2CSV(header=True,out=file)
            csv.type2CSV(term=term,header=False,out=file)
        elif schema_node.isAttribute():
            csv.prop2CSV(header=True,out=file)
            csv.prop2CSV(term=term,header=False,out=file)
        elif schema_node.isEnumerationValue():
            csv.enum2CSV(header=True,out=file)
            csv.enum2CSV(term=term,header=False,out=file)
        data = file.getvalue()
        file.close()
        return data


    def handle404Failure(self, node, layers="core", extrainfo=None):
        self.error(404)
        self.emitSchemaorgHeaders("404%20Missing")
        self.response.out.write('<h3>404 Not Found.</h3><p><br/>Page not found. Please <a href="/">try the homepage.</a><br/><br/></p>')


        clean_node = cleanPath(node)

        log.debug("404: clean_node: clean_node: %s node: %s" % (clean_node, node))

        base_term = Unit.GetUnit( node.rsplit('/')[0] )
        if base_term != None :
            self.response.out.write('<div>Perhaps you meant: <a href="/%s">%s</a></div> <br/><br/> ' % ( base_term.id, base_term.id ))

        base_actionprop = Unit.GetUnit( node.rsplit('-')[0] )
        if base_actionprop != None :
            self.response.out.write('<div>Looking for an <a href="/Action">Action</a>-related property? Note that xyz-input and xyz-output have <a href="/docs/actions.html">special meaning</a>. See also: <a href="/%s">%s</a></div> <br/><br/> ' % ( base_actionprop.id, base_actionprop.id ))
        
        if extrainfo:
            self.response.out.write("<div>%s</div>" % extrainfo)

        self.response.out.write("</div>\n</body>\n</html>\n")

        return True

    def handleFullReleasePage(self, node,  layerlist='core'):

        """Deal with a request for a full release summary page. Lists all terms and their descriptions inline in one long page.
        version/latest/ is from current schemas, others will need to be loaded and emitted from stored HTML snapshots (for now)."""

        # http://jinja.pocoo.org/docs/dev/templates/

        global releaselog
        clean_node = cleanPath(node)
        self.response.headers['Content-Type'] = "text/html"
        self.emitCacheHeaders()

        requested_version = clean_node.rsplit('/')[1]
        requested_format = clean_node.rsplit('/')[-1]
        if len( clean_node.rsplit('/') ) == 2:
            requested_format=""

        log.info("Full release page for: node: '%s' cleannode: '%s' requested_version: '%s' requested_format: '%s' l: %s" % (node, clean_node, requested_version, requested_format, len(clean_node.rsplit('/')) ) )

        # Full release page for: node: 'version/' cleannode: 'version/' requested_version: '' requested_format: '' l: 2
        # /version/
        log.debug("clean_node: %s requested_version: %s " %  (clean_node, requested_version))
        if (clean_node=="version/" or clean_node=="version") and requested_version=="" and requested_format=="":
            log.info("Table of contents should be sent instead, then succeed.")
            if getPageFromStore('tocVersionPage'):
                self.response.out.write( getPageFromStore('tocVersionPage'))
                return True
            else:
                log.debug("Serving tocversionPage from cache.")
                page = templateRender('tocVersionPage.tpl',
                        {"releases": sorted(releaselog.iterkeys()),
                         "menu_sel": "Schemas"})

                self.response.out.write( page )
                log.debug("Serving fresh tocVersionPage.")
                PageStore.put("tocVersionPage",page)
                return True

        if requested_version in releaselog:
            log.info("Version '%s' was released on %s. Serving from filesystem." % ( node, releaselog[requested_version] ))

            version_rdfa = "data/releases/%s/schema.rdfa" % requested_version
            version_allhtml = "data/releases/%s/schema-all.html" % requested_version
            version_nt = "data/releases/%s/schema.nt" % requested_version
            if requested_format=="":
                self.response.out.write( open(version_allhtml, 'r').read() )
                return True
                # log.info("Skipping filesystem for now.")

            if requested_format=="schema.rdfa":
                self.response.headers['Content-Type'] = "application/octet-stream" # It is HTML but ... not really.
                self.response.headers['Content-Disposition']= "attachment; filename=schemaorg_%s.rdfa.html" % requested_version
                self.response.out.write( open(version_rdfa, 'r').read() )
                return True

            if requested_format=="schema.nt":
                self.response.headers['Content-Type'] = "application/n-triples" # It is HTML but ... not really.
                self.response.headers['Content-Disposition']= "attachment; filename=schemaorg_%s.rdfa.nt" % requested_version
                self.response.out.write( open(version_nt, 'r').read() )
                return True

            if requested_format != "":
                return False # Turtle, csv etc.

        else:
            log.info("Unreleased version requested. We only understand requests for latest if unreleased.")

            if requested_version != "build-latest":
                return False
                log.info("giving up to 404.")
            else:
                log.info("generating a live view of this latest release.")


        if getPageFromStore('FullReleasePage'):
            self.response.out.write( getPageFromStore('FullReleasePage') )
            log.debug("Serving recycled FullReleasePage.")
            return True
        else:
            mainroot = TypeHierarchyTree()
            mainroot.traverseForHTML(Unit.GetUnit("Thing"), hashorslash="#term_", layers=layerlist)
            thing_tree = mainroot.toHTML()
            base_href = "/version/%s/" % requested_version

            az_types = GetAllTypes()
            az_types.sort( key=lambda u: u.id)
            az_type_meta = {}

            az_props = GetAllProperties()
            az_props.sort( key = lambda u: u.id)
            az_prop_meta = {}


#TODO: ClassProperties (self, cl, subclass=False, layers="core", out=None, hashorslash="/"):

            # TYPES
            for t in az_types:
                props4type = HTMLOutput() # properties applicable for a type
                props2type = HTMLOutput() # properties that go into a type

                self.emitSimplePropertiesPerType(t, out=props4type, hashorslash="#term_" )
                self.emitSimplePropertiesIntoType(t, out=props2type, hashorslash="#term_" )

                #self.ClassProperties(t, out=typeInfo, hashorslash="#term_" )
                tcmt = Markup(GetComment(t))
                az_type_meta[t]={}
                az_type_meta[t]['comment'] = tcmt
                az_type_meta[t]['props4type'] = props4type.toHTML()
                az_type_meta[t]['props2type'] = props2type.toHTML()

            # PROPERTIES
            for pt in az_props:
                attrInfo = HTMLOutput()
                rangeList = HTMLOutput()
                domainList = HTMLOutput()
                # self.emitAttributeProperties(pt, out=attrInfo, hashorslash="#term_" )
                # self.emitSimpleAttributeProperties(pt, out=rangedomainInfo, hashorslash="#term_" )

                self.emitRangeTypesForProperty(pt, out=rangeList, hashorslash="#term_" )
                self.emitDomainTypesForProperty(pt, out=domainList, hashorslash="#term_" )

                cmt = Markup(GetComment(pt))
                az_prop_meta[pt] = {}
                az_prop_meta[pt]['comment'] = cmt
                az_prop_meta[pt]['attrinfo'] = attrInfo.toHTML()
                az_prop_meta[pt]['rangelist'] = rangeList.toHTML()
                az_prop_meta[pt]['domainlist'] = domainList.toHTML()

            if requested_version == "build-latest":
                requested_version = SCHEMA_VERSION
                releasedate = "XXXX-XX-XX    (UNRELEASED PREVIEW VERSION)"
            else:
                releasedate = releaselog[str(SCHEMA_VERSION)]

            page = templateRender('fullReleasePage.tpl',
                    {"base_href": base_href,
                    'thing_tree': thing_tree,
                    'liveversion': SCHEMA_VERSION,
                    'requested_version': requested_version,
                    'releasedate': releasedate,
                    'az_props': az_props, 'az_types': az_types,
                    'az_prop_meta': az_prop_meta, 'az_type_meta': az_type_meta,
                    'menu_sel': "Documentation"})

            self.response.out.write( page )
            log.debug("Serving fresh FullReleasePage.")
            PageStore.put("FullReleasePage",page)
            return True

    def handleExtensionContents(self,ext):
        if not ext in ENABLED_EXTENSIONS:
            return ""

        if getPageFromStore('ExtensionContents',ext):
            return getPageFromStore('ExtensionContents',ext)

        buff = StringIO.StringIO()

        az_terms = GetAllTerms(ext) #Returns sorted by id results.
        az_terms.sort(key = lambda u: u.category)

        if len(az_terms) > 0:
            buff.write("<br/><div style=\"text-align: left; margin: 2em\"><h3>Terms defined or referenced in the '%s' extension.</h3>" % ext)

            keys = []
            groups = []
            for k,g in itertools.groupby(az_terms, key = lambda u: u.category):
                keys.append(k)
                groups.append(list(g))

            i = 0
            while i < len(groups):
                groups[i] = sorted(groups[i],key = lambda u: u.id)
                i += 1

            g=0
            while g < len(groups):
                if g > 0:
                    buff.write("<br/>")
                buff.write(self.listTerms(groups[g],"<br/>%s Types (%s)<br/>" %
                                         (keys[g],self.countTypes(groups[g],select="type",layers=ext)),select="type",layers=ext))
                buff.write(self.listTerms(groups[g],"<br/>%s Properties (%s)<br/>" %
                                         (keys[g],self.countTypes(groups[g],select="prop",layers=ext)),select="prop",layers=ext))
                buff.write(self.listTerms(groups[g],"<br/>%s Enumeration values (%s)<br/>" %
                                         (keys[g],self.countTypes(groups[g],select="enum",layers=ext)),select="enum",layers=ext))
                g += 1
            buff.write("</div>")

        ret = buff.getvalue()
        PageStore.put('ExtensionContents',ret,ext)
        buff.close()
        return ret

    def countTypes(self,interms,select="",layers='core'):
        ret = 0
        for t in interms:
            if select == "type" and t.isClass(layers):
                ret += 1
            elif select == "prop" and t.isAttribute(layers):
                ret += 1
            elif select == "enum" and t.isEnumerationValue(layers):
                ret +=1
            elif select == "":
                ret += 1
        return ret


    def listTerms(self,interms,prefix="",select=None,layers='core'):
        buff = StringIO.StringIO()
        terms = interms
        if select:
            terms = []
            for t in interms:
                use = False
                if select == "type":
                    use = t.isClass(layers)
                elif select == "prop":
                    use = t.isAttribute(layers)
                elif select == "enum":
                    use = t.isEnumerationValue(layers)
                if use:
                    terms.append(t)

        if(len(terms) > 0):
            buff.write(prefix)
            first = True
            sep = ""
            for term in terms:
                if not first:
                    sep = ", "
                else:
                    first = False
                buff.write("%s%s" % (sep,self.ml(term)))

        ret = buff.getvalue()
        buff.close()
        return ret


    def setupHostinfo(self, node, test=""):
        hostString = test
        args = []
        if test == "":
            hostString = self.request.host
            args = self.request.arguments()

        scheme = "http" #Defalt for tests
        if not getInTestHarness():  #Get the actual scheme from the request
            scheme = self.request.scheme

        host_ext = re.match( r'([\w\-_]+)[\.:]?', hostString).group(1)
        #log.info("setupHostinfo: scheme=%s hoststring=%s host_ext?=%s" % (scheme, hostString, str(host_ext) ))

        setHttpScheme(scheme)

        split = hostString.rsplit(':')
        myhost = split[0]
        mybasehost = myhost
        myport = "80"
        if len(split) > 1:
            myport = split[1]

        setHostExt(host_ext)
        setBaseHost(mybasehost)
        setHostPort(myport)

        if host_ext != None:
            # e.g. "bib"
            log.debug("HOST: Found %s in %s" % ( host_ext, hostString ))
            if host_ext == "www":
                # www is special case that cannot be an extension - need to redirect to basehost
                mybasehost = mybasehost[4:]
                setBaseHost(mybasehost)
                return self.redirectToBase(node)
            elif not host_ext in ENABLED_EXTENSIONS:
                host_ext = ""
            else:
                mybasehost = mybasehost[len(host_ext) + 1:]
            setHostExt(host_ext)
            setBaseHost(mybasehost)


        setHostExt(host_ext)
        setBaseHost(mybasehost)
        setHostPort(myport)
        setArguments(args)

        dcn = host_ext
        if dcn == None or dcn == "" or dcn =="core":
            dcn = "core"
        if scheme != "http":
            dcn = "%s-%s" % (dcn,scheme)

        log.info("sdoapp.py setting current datacache to: %s " % dcn)
        DataCache.setCurrent(dcn)
        PageStore.setCurrent(dcn)
        HeaderStore.setCurrent(dcn)
        
        debugging = False
        if "localhost" in hostString or "sdo-phobos.appspot.com" in hostString or FORCEDEBUGGING:
            debugging = True
        setAppVar('debugging',debugging)

        return True

    def redirectToBase(self,node=""):
        uri = makeUrl("",node)
        self.response = webapp2.redirect(uri, True, 301)
        log.info("Redirecting [301] to: %s" % uri)
        return False


    def head(self, node):

        self.get(node) #Get the page

        #Clear the request & payload and only put the headers and status back
        hdrs = self.response.headers.copy()
        stat = self.response.status
        self.response.clear()
        self.response.headers = hdrs
        self.response.status = stat
        return

    def get(self, node):
        if not self.setupHostinfo(node):
            return

        if not node or node == "":
            node = "/"

        NotModified = False
        etag = getslug() + str(hash(node))
        jetag = etag + "json"
        passedTag = etag

        try:
            if ( "If-None-Match" in self.request.headers and
                 (self.request.headers["If-None-Match"] == etag or
                  self.request.headers["If-None-Match"] == jetag)):
                    NotModified = True
                    passedTag = self.request.headers["If-None-Match"]
                    log.debug("Etag - do 304")
            elif ( "If-Unmodified-Since" in self.request.headers and
                   datetime.datetime.strptime(self.request.headers["If-Unmodified-Since"],"%a, %d %b %Y %H:%M:%S %Z") == getmodiftime() ):
                    NotModified = True
                    log.debug("Unmod-since - do 304")
        except Exception as e:
            log.info("ERROR reading request headers: %s" % e)
            pass

        retHdrs = HeaderStore.get(passedTag)   #Already cached headers for this request?
        
        if retHdrs and "_pageFlush" in getArguments():
            log.info("Reloading header for %s" % passedTag)
            HeaderStore.remove(passedTag)
            retHdrs = None
        
        if NotModified and retHdrs:
            self.response.clear()
            self.response.headers = retHdrs
            self.response.set_status(304,"Not Modified")
        else:
            enableCaching = self._get(node) #Go build the page

            tagsuff = ""
            if ( "content-type" in self.response.headers and
                 "json" in self.response.headers["content-type"] ):
                  tagsuff = "json"

            if enableCaching:
                if self.response.status.startswith("200"):
                    self.response.headers.add_header("ETag", etag + tagsuff)
                    self.response.headers['Last-Modified'] = getmodiftime().strftime("%a, %d %b %Y %H:%M:%S UTC")
                    retHdrs = self.response.headers.copy()
                    HeaderStore.put(etag + tagsuff,retHdrs) #Cache these headers for a future 304 return


    def _get(self, node, doWarm=True):
        global LOADEDSOURCES
        """Get a schema.org site page generated for this node/term.

        Web content is written directly via self.response.

        CORS enabled all URLs - we assume site entirely public.
        See http://en.wikipedia.org/wiki/Cross-origin_resource_sharing

        These should give a JSON version of schema.org:

            curl --verbose -H "Accept: application/ld+json" http://localhost:8080/docs/jsonldcontext.json
            curl --verbose -H "Accept: application/ld+json" http://localhost:8080/docs/jsonldcontext.json.txt
            curl --verbose -H "Accept: application/ld+json" http://localhost:8080/

        Per-term pages vary for type, property and enumeration.

        Last resort is a 404 error if we do not exactly match a term's id.

        See also https://webapp-improved.appspot.com/guide/request.html#guide-request
        
        Return True to enable browser caching ETag/Last-Modified - False for no cache
        """
        global_vars.time_start = datetime.datetime.now()
        tick() #keep system fresh

        #log.info("[%s] _get(%s)" % (getInstanceId(short=True),node))

        self.callCount()

        if (node in silent_skip_list):
            return False

        if ENABLE_HOSTED_EXTENSIONS:
            layerlist = self.setupExtensionLayerlist(node) # e.g. ['core', 'bib']
        else:
            layerlist = ["core"]

        setSiteName(self.getExtendedSiteName(layerlist)) # e.g. 'bib.schema.org', 'schema.org'
        log.debug("EXT: set sitename to %s " % getSiteName())
        if(node == "_ah/warmup"):
            if "localhost" in os.environ['SERVER_NAME'] and WarmupState.lower() == "auto":
                log.info("[%s] Warmup dissabled for localhost instance" % getInstanceId(short=True))
                if DISABLE_NDB_FOR_LOCALHOST:
                    log.info("[%s] NDB dissabled for localhost instance" % getInstanceId(short=True))
                    enablePageStore(False)
            else:
                if not memcache.get("warmedup"):
                    memcache.set("warmedup", value=True)
                    self.warmup()
                else:
                    log.info("Warmup already actioned")
            return False
        #elif doWarm:  #Do a bit of warming on each call
            #global WarmedUp
            #global Warmer
            #if not WarmedUp:
                #Warmer.stepWarm(self)

        self.emitHTTPHeaders(node) #Ensure we have the right basic header values

        if(node == "_ah/start"):
            log.info("Instance[%s] received Start request at %s" % (modules.get_current_instance_id(), global_vars.time_start) )
            if "localhost" in os.environ['SERVER_NAME'] and WarmupState.lower() == "auto":
                log.info("[%s] Warmup dissabled for localhost instance" % getInstanceId(short=True))
                if DISABLE_NDB_FOR_LOCALHOST:
                    log.info("[%s] NDB dissabled for localhost instance" % getInstanceId(short=True))
                    enablePageStore(False)
            else:
                if not memcache.get("warmedup"):
                    memcache.set("warmedup", value=True)
                    self.warmup()
                else:
                    log.info("Warmup already actioned")
            return False

        if not getPageFromStore(node): #Not stored this page before
            #log.info("Not stored %s" % node)
            if not LOADEDSOURCES:
                log.info("Instance[%s] received request for not stored page: %s" % (getInstanceId(short=True), node) )
                log.info("Instance[%s] needs to load sources to create it" % (getInstanceId(short=True)) )
                load_sources() #Get Examples files and schema definitions

        if (node in ["", "/"]):
            return self.handleHomepage(node)

        if node in ["docs/jsonldcontext.json.txt", "docs/jsonldcontext.json"]:
            if self.handleJSONContext(node):
                return True
            else:
                log.info("Error handling JSON-LD context: %s" % node)
                return False

        if (node == "docs/full.html"): 
            if self.handleFullHierarchyPage(node, layerlist=layerlist):
                return True
            else:
                log.info("Error handling full.html : %s " % node)
                return False

        if (node == "docs/schemas.html"): 
            if self.handleSchemasPage(node, layerlist=layerlist):
                return True
            else:
                log.info("Error handling schemas.html : %s " % node)
                return False
        if (node == "docs/developers.html"): 
            if self.handleDumpsPage(node, layerlist=layerlist):
                return True
            else:
                log.info("Error handling developers.html : %s " % node)
                return False



        if (node == "docs/tree.jsonld" or node == "docs/tree.json"):
            if self.handleJSONSchemaTree(node, layerlist=ALL_LAYERS):
                return True
            else:
                log.info("Error handling JSON-LD schema tree: %s " % node)
                return False

        currentVerPath = "version/%s" % SCHEMA_VERSION

        if(node.startswith("version/latest")):
            newurl = "%s%s" % (currentVerPath,node[14:])
            log.info("REDIRECTING TO: %s" % newurl)
            self.response.set_status(302,"Found")
            self.response.headers['Location'] = makeUrl("",newurl)
            self.emitCacheHeaders()
            return False #don't cache this redirect

        #Match nodes of pattern 'version/*' 'version/*/' or 'version/'
        if (re.match(r'^version/[^/]*$', str(node)) or re.match(r'^version/[^/]*/$', str(node)) or node == "version/") :
            if self.handleFullReleasePage(node, layerlist=layerlist):
                return True
            else:
                log.info("Error handling full release page: %s " % node)
                if self.handle404Failure(node):
                    return False
                else:
                    log.info("Error handling 404 under /version/")
                    return False

        if(node == "_siteDebug"):
            if(getBaseHost() != "schema.org" or os.environ['PRODSITEDEBUG'] == "True"):
                self.siteDebug()
                return False #Treat as a dynamic page - suppress Etags etc.

        if(node == "_cacheFlush"):
            setmodiftime(datetime.datetime.utcnow()) #Resets etags and modtime
            counts = CacheControl.clean(pagesonly=True)
            inf = "<div style=\"clear: both; float: left; text-align: left; font-size: xx-small; color: #888 ; margin: 1em; line-height: 100%;\">"
            inf +=  str(counts)
            inf += "</div>"
            self.handle404Failure(node,extrainfo=inf)
            return False
            

        # Pages based on request path matching a Unit in the term graph:
        if self.handleExactTermPage(node, layers=layerlist):
            return True
        else:
            log.info("Error handling exact term page. Assuming a 404: %s" % node)

            # Drop through to 404 as default exit.
            if self.handle404Failure(node):
                return False
            else:
                log.info("Error handling 404.")
                return False

    def siteDebug(self):
        global STATS
        page = templateRender('siteDebug.tpl')

        self.response.out.write( page )
        ext = getHostExt()
        if ext == "":
            ext = "core"
        self.response.out.write("<div style=\"display: none;\">\nLAYER:%s\n</div>" % ext)
        self.response.out.write("<table style=\"width: 70%; border: solid 1px #CCCCCC; border-collapse: collapse;\"><tbody>\n")
        self.writeDebugRow("Setting","Value",True)
        if SHAREDSITEDEBUG:
            self.writeDebugRow("System start",memcache.get("SysStart"))
            inst = memcache.get("Instances")
            extinst = memcache.get("ExitInstances")
            self.writeDebugRow("Running instances(%s)" % len(memcache.get("Instances")),inst.keys())
            self.writeDebugRow("Instance exits(%s)" % len(memcache.get("ExitInstances")),extinst.keys())
        self.writeDebugRow("httpScheme",getHttpScheme())
        self.writeDebugRow("host_ext",getHostExt())
        self.writeDebugRow("basehost",getBaseHost())
        self.writeDebugRow("hostport",getHostPort())
        self.writeDebugRow("sitename",getSiteName())
        self.writeDebugRow("debugging",getAppVar('debugging'))
        self.writeDebugRow("intestharness",getInTestHarness())
        if SHAREDSITEDEBUG:
            self.writeDebugRow("total calls",memcache.get("total"))
            for s in ALL_LAYERS:
                self.writeDebugRow("%s calls" % s, memcache.get(s))
            for s in ["http","https"]:
                self.writeDebugRow("%s calls" % s, memcache.get(s))


        self.writeDebugRow("This Instance ID",os.environ["INSTANCE_ID"],True)
        self.writeDebugRow("Instance Calls", callCount)
        self.writeDebugRow("Instance Memory Usage [Mb]", str(runtime.memory_usage()).replace("\n","<br/>"))
        self.writeDebugRow("Instance Current DataCache", DataCache.getCurrent())
        self.writeDebugRow("Instance DataCaches", len(DataCache.keys()))
        for c in DataCache.keys():
           self.writeDebugRow("Instance DataCache[%s] size" % c, len(DataCache.getCache(c) ))
        self.response.out.write("</tbody><table><br/>\n")
        self.response.out.write( "</div>\n<body>\n</html>" )

    def writeDebugRow(self,term,value,head=False):
        rt = "td"
        cellStyle = "border: solid 1px #CCCCCC; vertical-align: top; border-collapse: collapse;"
        if head:
            rt = "th"
            cellStyle += " color: #FFFFFF; background: #888888;"

        leftcellStyle = cellStyle
        leftcellStyle += " width: 35%"

        divstyle = "width: 100%; max-height: 100px; overflow: auto"

        self.response.out.write("<tr><%s style=\"%s\">%s</%s><%s style=\"%s\"><div style=\"%s\">%s</div></%s></tr>\n" % (rt,leftcellStyle,term,rt,rt,cellStyle,divstyle,value,rt))

    def callCount(self):
        global instance_first
        global instance_num
        global callCount
        callCount += 1
        if(instance_first):
            instance_first = False
            instance_num += 1
            if SHAREDSITEDEBUG:
                if(memcache.add(key="Instances",value={})):
                    memcache.add(key="ExitInstances",value={})
                    memcache.add(key="http",value=0)
                    memcache.add(key="https",value=0)
                    memcache.add(key="total",value=0)
                    for i in ALL_LAYERS:
                        memcache.add(key=i,value=0)

                Insts = memcache.get("Instances")
                Insts[os.environ["INSTANCE_ID"]] = 1
                memcache.replace("Instances",Insts)

        if SHAREDSITEDEBUG:
            memcache.incr("total")
            memcache.incr(getHttpScheme())
            if getHostExt() != "":
                memcache.incr(getHostExt())
            else:
                memcache.incr("core")


    def warmup(self):
        global WarmedUp
        global Warmer
        if WarmedUp:
            return
        warm_start = datetime.datetime.now()
        log.debug("Instance[%s] received Warmup request at %s" % (modules.get_current_instance_id(), datetime.datetime.utcnow()) )
        Warmer.warmAll(self)
        log.debug("Instance[%s] completed Warmup request at %s elapsed: %s" % (modules.get_current_instance_id(), datetime.datetime.utcnow(),datetime.datetime.now() - warm_start ) )

class WarmupTool():

    def __init__(self):
        #self.pageList = ["docs/schemas.html"]
        self.pageList = ["/","docs/schemas.html","docs/full.html","docs/tree.jsonld"]
        self.warmPages = {}
        for l in ALL_LAYERS:
            self.warmPages[l] = []
        self.warmedLayers = []

    def stepWarm(self, unit=None, layer=None):
        global WarmedUp
        if not layer: 
            layer = getHostExt()
            if layer == "":
                layer = "core"
        if not unit or WarmedUp:
            return
        if layer in self.warmedLayers: #Done all for this layer
            return
        warmedPages = False
        for p in self.pageList:
            if p not in self.warmPages[layer]:
                log.info("Warming page %s in layer %s" % (p,layer))
                unit._get(p,doWarm=False)
                unit.response.clear()
                self.warmPages[layer].append(p)
                if len(self.warmPages[layer]) == len(self.pageList):
                    warmedPages = True
                break
        if warmedPages: #Must be all warmed for this layer
            log.info("All warmed in layer %s" % layer)
            self.warmedLayers.append(layer)
            self.checkAll()

    def checkAll(self):
        global WarmedUp
        allDone = True
        for l in ALL_LAYERS:
            if l != "" and l not in self.warmedLayers:
                allDone = False
                break
        if allDone:
            WarmedUp = True
            log.info("All layers warmed!")

    def warmAll(self,unit):
        global WarmedUp
        while not WarmedUp:
            for l in ALL_LAYERS:
                self.stepWarm(layer=l,unit=unit)

Warmer = WarmupTool()

def templateRender(templateName,values=None):
    global sitemode #,sitename
    extDef = Unit.GetUnit(getNss(getHostExt()),True)
    extComment = ""
    extVers = ""
    extName = ""
    #log.info("EXDEF '%s'" % extDef)
    if extDef:
        extComment = GetComment(extDef,ALL_LAYERS)
        if extComment == "No comment":
            extComment = ""
        extDDs = GetTargets(Unit.GetUnit("disambiguatingDescription", True), extDef, layers=ALL_LAYERS )
        if len(extDDs) > 0:
            extDD = Markdown.parse(extDDs[0])
        else:
            extDD = ""
        first = True
        for ver in GetsoftwareVersions(extDef, ALL_LAYERS):
            if first:
                first = False
                extVers = "<em>(Extension version: "
            else:
                extVers += ", "
            extVers += Markdown.parse(ver)
        if len(extVers) :
            extVers += ")</em>"
        nms = GetTargets(Unit.GetUnit("name", True), extDef, layers=ALL_LAYERS )
        if len(nms) > 0:
            extName = nms[0]

    defvars = {
        'ENABLE_HOSTED_EXTENSIONS': ENABLE_HOSTED_EXTENSIONS,
        'SCHEMA_VERSION': SCHEMA_VERSION,
        'sitemode': sitemode,
        'sitename': getSiteName(),
        'staticPath': makeUrl("",""),
        'extensionPath': makeUrl(getHostExt(),""),
        'myhost': getHost(),
        'myport': getHostPort(),
        'mybasehost': getBaseHost(),
        'host_ext': getHostExt(),
        'extComment': extComment,
        'extDD': extDD,
        'extVers': extVers,
        'extName': extName,
        'debugging': getAppVar('debugging')
    }

    if values:
        defvars.update(values)
    template = JINJA_ENVIRONMENT.get_template(templateName)
    return template.render(defvars)


def my_shutdown_hook():
    global instance_num
    if SHAREDSITEDEBUG:
        Insts = memcache.get("ExitInstances")
        Insts[os.environ["INSTANCE_ID"]] = 1
        memcache.replace("ExitInstances",Insts)

        memcache.add("Exits",0)
        memcache.incr("Exits")
    log.info("Instance[%s] shutting down" % modules.get_current_instance_id())

runtime.set_shutdown_hook(my_shutdown_hook)

ThreadVars = threading.local()
def getAppVar(var):
    ret = getattr(ThreadVars, var, None)
    #log.debug("got var %s as %s" % (var,ret))
    return ret

def setAppVar(var,val):
    #log.debug("Setting var %s to %s" % (var,val))
    setattr(ThreadVars,var,val)

def setHttpScheme(val):
    setAppVar('httpScheme',val)

def getHttpScheme():
    return getAppVar('httpScheme')

def setHostExt(val):
    setAppVar('host_ext',val)

def getHostExt():
    return getAppVar('host_ext')

def setSiteName(val):
    setAppVar('sitename',val)

def getSiteName():
    return getAppVar('sitename')

def setHost(val):
    setAppVar('myhost',val)

def getHost():
    return getAppVar('myhost')

def setBaseHost(val):
    setAppVar('mybasehost',val)

def getBaseHost():
    return getAppVar('mybasehost')

def setHostPort(val):
    setAppVar('myport',val)

def getHostPort():
    return getAppVar('myport')

def setArguments(val):
    setAppVar('myarguments',val)

def getArguments():
    return getAppVar('myarguments')

def makeUrl(ext="",path=""):
        port = ""
        sub = ""
        p = ""
        if(getHostPort() != "80"):
            port = ":%s" % getHostPort()
        if ext != "core" and ext != "":
            sub = "%s." % ext
        if path != "":
            if path.startswith("/"):
                p = path
            else:
                p = "/%s" % path

        url = "%s://%s%s%s%s" % (getHttpScheme(),sub,getBaseHost(),port,p)
        return url

def getPageFromStore(id,ext=None):
        cached = PageStore.get(id,ext)
        if cached and "_pageFlush" in getArguments():
            log.info("Reloading page for %s" % id)
            PageStore.remove(id,ext)
            cached = None
        return cached
    
schemasInitialized = False
def load_schema_definitions():
    #log.info("STARTING UP... reading schemas.")
    #load_graph(loadExtensions=ENABLE_HOSTED_EXTENSIONS)
    global schemasInitialized
    read_schemas(loadExtensions=ENABLE_HOSTED_EXTENSIONS)
    if ENABLE_HOSTED_EXTENSIONS:
        read_extensions(ENABLED_EXTENSIONS)
    schemasInitialized = True

LOADINGSOURCE = None
WAITSECS = 360
def load_sources():
    global LOADINGSOURCE, LOADEDSOURCES,WAITSECS
    if LOADEDSOURCES:
        return
    if LOADINGSOURCE: #Another thread may already be here
        elapsedSecs = 0
        while LOADINGSOURCE and elapsedSecs < WAITSECS:
            time.sleep(0.1)
            if LOADINGSOURCE: #If still loading, check timing and go around again
                elapsed = datetime.datetime.now() - LOADINGSOURCE
                elapsedSecs = elapsed.total_seconds()

        if elapsedSecs >= WAITSECS: # Clear potential thread block caused by another thread crashing out leaving flags set
            log.info("LOADINGSOURCE Thread blocked for over %s seconds - clearing lock" % WAITSECS)
            LOADINGSOURCE = None

    if not LOADEDSOURCES and not LOADINGSOURCE: # Check again in case things have changed in above loop
        LOADINGSOURCE = datetime.datetime.now()
        load_start = datetime.datetime.now()
        load_examples_data(ENABLED_EXTENSIONS)
        log.info(("[%s] Examples load took %s " % (getInstanceId(short=True),(datetime.datetime.now() - load_start))))
        load_schema_definitions()
        LOADEDSOURCES=True
        LOADINGSOURCE=None

if getInTestHarness():
    load_sources()
else:
    app = ndb.toplevel(webapp2.WSGIApplication([("/(.*)", ShowUnit)]))
