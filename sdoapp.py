#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from __future__ import with_statement

import logging
logging.basicConfig(level=logging.INFO) # dev_appserver.py --log_level debug .
log = logging.getLogger(__name__)

import os
import re
import webapp2
import urllib2
import mimetypes
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
from google.appengine.api import app_identity
from google.appengine.api.modules import modules

GAE_APP_ID = "appId"
GAE_VERSION_ID = "versionId"


#Testharness Used to indicate we are being called from tests - use setInTestHarness() & getInTestHarness() to manage value - defauluts to False (we are not in tests)

from testharness import *
from sdoutil import *
from api import *
from apirdfterm import *
from apirdflib import load_graph, getNss, getRevNss, buildSingleTermGraph, serializeSingleTermGrapth
from apirdflib import countTypes, countProperties, countEnums, graphFromFiles, getPathForPrefix, getPrefixForPath, rdfgettops

from apimarkdown import Markdown

from sdordf2csv import sdordf2csv
CONFIGFILE = os.environ.get("CONFIGFILE","sdoconfig.json")
SdoConfig.load(CONFIGFILE)
if not SdoConfig.valid:
    log.error("Invalid config from '%s' or its includes !!" % CONFIGFILE)
    os.exit()

SCHEMA_VERSION="3.9"

if not getInTestHarness():
    GAE_APP_ID = app_identity.get_application_id()
    GAE_VERSION_ID = modules.get_current_version_name()

FEEDBACK_FORM_BASE_URL='https://docs.google.com/a/google.com/forms/d/1krxHlWJAO3JgvHRZV9Rugkr9VYnMdrI10xbGsWt733c/viewform?entry.1174568178&entry.41124795={0}&entry.882602760={1}'
# {0}: term URL, {1} category of term.

sitemode = "mainsite" # whitespaced list for CSS tags,
            # e.g. "mainsite testsite" when off expected domains
            # "extensionsite" when in an extension (e.g. blue?)

releaselog = {  "2.0": "2015-05-13",
                "2.1": "2015-08-06",
                "2.2": "2015-11-05",
                "3.0": "2016-05-04",
                "3.1": "2016-08-09",
                "3.2": "2017-03-23",
                "3.3": "2017-08-14",
                "3.4": "2018-06-15",
                "3.5": "2019-04-01",
                "3.6": "2019-05-01",
                "3.7": "2019-06-01",
                "3.8": "2019-07-01",
                "3.9": "2019-08-01" }

silent_skip_list =  [ "favicon.ico" ] # Do nothing for now

all_layers = {}
ext_re = re.compile(r'([^\w,])+')
validNode_re = re.compile(r'^[\w\/.-]+$')

#TODO: Modes:
# mainsite
# webschemadev
# known extension (not skiplist'd, eg. demo1 on schema.org)

TEMPLATESDIR = SdoConfig.templateDir()
FileBasedTemplates = True

def urlTemplateLoader(name):
    log.info("TEMPLATE LOADER LOOKING FOR: %s" % name)
    url = TEMPLATESDIR + "/" + name
    log.info("URL: %s" % url)
    try:
        fd = urllib2.urlopen(url)
        res = fd.read()
    except urllib2.URLError as e:
        log.info("URLError %s" % e)
        return None
    return res



if TEMPLATESDIR:
    if TEMPLATESDIR.startswith("file://"):
        TEMPLATESDIR = TEMPLATESDIR[7:]
    if "://" in TEMPLATESDIR:
        FileBasedTemplates = False
else:
    TEMPLATESDIR = os.path.join(os.path.dirname(__file__), 'templates')
    log.info("No Templates directory defined - defaulting to %s" % TEMPLATESDIR)

if FileBasedTemplates:
    JINJA_ENVIRONMENT = jinja2.Environment(loader=jinja2.FileSystemLoader(TEMPLATESDIR),
    extensions=['jinja2.ext.autoescape'], autoescape=True, cache_size=0)
else:
    JINJA_ENVIRONMENT = jinja2.Environment(loader=jinja2.FunctionLoader(urlTemplateLoader),
    extensions=['jinja2.ext.autoescape'], autoescape=True, cache_size=0)



CANONICALSCHEME = "http"
ENABLE_JSONLD_CONTEXT = True
ENABLE_CORS = True
ENABLE_HOSTED_EXTENSIONS = True
DISABLE_NDB_FOR_LOCALHOST = True
ENABLEMOREINFO = True
WORKINGHOSTS = ["schema.org","schemaorg.appspot.com",
                "webschemas.org","webschemas-g.appspot.com",
                "sdo-test.appspot.com",
                "localhost"]
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

noindexpages = True

SUBDOMAINS = True
subs = os.environ.get("SUBDOMAINS",None)
if subs:
    if subs.lower() == "true":
        SUBDOMAINS = True
    elif subs.lower() == "false":
        SUBDOMAINS = False
    else:
        log.info("SUBDOMAINS set to invalid value %s - defaulting to %s" %(subs,SUBDOMAINS))
log.info("SUBDOMAINS set to %s" % SUBDOMAINS)

DEVELOPVERSION = True
devs = os.environ.get("DEVELOPVERSION",None)
if devs:
    if devs.lower() == "true":
        DEVELOPVERSION = True
    elif devs.lower() == "false":
        DEVELOPVERSION = False
    else:
        log.info("DEVELOPVERSION set to invalid value %s - defaulting to %s" %(devs,DEVELOPVERSION))
log.info("DEVELOPVERSION set to %s" % DEVELOPVERSION)

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

def getAppEngineVersion():
    ret = ""
    if not getInTestHarness():
        from google.appengine.api.modules.modules import get_current_version_name
        ret = get_current_version_name()
        #log.info("AppEngineVersion '%s'" % ret)
    else:
        return "TestVersion"
    return ret

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
        if not slug:#Occationally memcache will loose the value and result in  becomming Null value
            systarttime = datetime.datetime.utcnow()
            tick()
            setmodiftime(systarttime)#Will store it again
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

def check4NewVersion():
    ret = False
    dep = None
    try:
        fpath = os.path.join(os.path.split(__file__)[0], 'admin/deploy_timestamp.txt')
        #log.info("fpath: %s" % fpath)
        with open(fpath, 'r') as f:
            dep = f.read()
            dep = dep.replace("\n","")
        f.close()
    except Exception  as e:
        log.info("ERROR reading: %s" % e)
        pass

    if  getInTestHarness() or "localhost" in os.environ['SERVER_NAME']: #Force new version logic for local versions and tests
        ret = True
        log.info("Assuming new version for local/test instance")
    else:
        stored,info = getTimestampedInfo("deployed-timestamp")
        if stored != dep:
            ret = True

    return ret, dep

def storeNewTimestamp(stamp=None):
    storeTimestampedInfo("deployed-timestamp",stamp)

def storeInitialisedTimestamp(stamp=None):
    storeTimestampedInfo("initialised-timestamp",stamp)



if getInTestHarness():
    load_examples_data(ENABLED_EXTENSIONS)
else: #Ensure clean start for any memcached or ndb store values...

    changed, dep = check4NewVersion()
    if changed: #We are a new instance of the app
        msg = "New app instance [%s:%s] detected - FLUSHING CACHES.  (deploy_timestamp='%s')\nLoaded Config file from: %s" % (GAE_VERSION_ID,GAE_APP_ID,dep,CONFIGFILE)
        memcache.flush_all()
        storeNewTimestamp(dep)

        sdo_send_mail(to="rjw@dataliberate.com",subject="[SCHEMAINFO] from 'sdoapp'", msg=msg)
        log.info("%s" % msg)

        load_start = datetime.datetime.now()
        systarttime = datetime.datetime.utcnow()
        memcache.set(key="app_initialising", value=True, time=300)  #Give the system 5 mins - auto remove flag in case of crash
        memcache.set(key="static-version", value=appver)
        memcache.add(key="SysStart", value=systarttime)
        instance_first = True
        cleanmsg = CacheControl.clean()
        log.info("Clean count(s): %s" % cleanmsg)
        log.info(("[%s] Cache clean took %s " % (getInstanceId(short=True),(datetime.datetime.now() - load_start))))
        load_start = datetime.datetime.now()
        tick()
        memcache.set(key="app_initialising", value=False)
        log.debug("[%s] Awake >>>>>>>>>>>." % (getInstanceId(short=True)))
        storeInitialisedTimestamp()
    else:
        time.sleep(0.5) #Give time for the initialisation flag (possibly being set in another thread/instance) to be set
        WAITCOUNT = 180
        waittime = WAITCOUNT
        while waittime > 0:
            waittime -= 1
            flag = memcache.get("app_initialising")
            if not flag or flag == False: #Initialised or value missing
                break

            log.debug("[%s] Waited %s seconds for intialisation to end memcahce value = %s" % (getInstanceId(short=True),
                                                    (WAITCOUNT - waittime),memcache.get("app_initialising")))
            time.sleep(1)
        if waittime <= 0:
            log.info("[%s] Waited %s seconds for intialisation to end - proceeding anyway!"  % (getInstanceId(short=True),WAITCOUNT))

        log.debug("[%s] End of waiting !!!!!!!!!!." % (getInstanceId(short=True)))
        tick()
        systarttime = memcache.get("SysStart")

    if(not systarttime): #Occationally memcache will loose the value and result in systarttime becomming Null value
         systarttime = datetime.datetime.utcnow()
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
        self.visited = []
        self.prefix = prefix

    def emit(self, s):
        self.txt += s + "\n"

    def emit2buff(self, buff, s):
        buff.write(s + "\n")

    def toHTML(self):
        return '%s<ul>%s</ul>' % (self.prefix, self.txt)

    def toJSON(self):
        return self.txt

    def traverseForHTML(self, term, depth = 1, hashorslash="/", layers='core', idprefix="", urlprefix="", traverseAllLayers=False, buff=None):

        """Generate a hierarchical tree view of the types. hashorslash is used for relative link prefixing."""

        #log.info("traverseForHTML: node=%s hashorslash=%s" % ( term, hashorslash ))

        if not term:
            return False

        if term.superseded() or term.getLayer() == ATTIC:
            return False

        localBuff = False
        if buff == None:
            localBuff = True
            buff = StringIO.StringIO()

        home = term.getLayer()
        gotOutput = True


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
        subTypes = term.getSubs()
        idstring = idprefix + term.getId()
        if len(subTypes) > 0:
            # and we haven't been here before
            if term.getId() not in self.visited:
                self.emit2buff(buff, ' %s<li class="tbranch" id="%s"><a %s %s href="%s%s%s">%s</a>%s' % (" " * 4 * depth, idstring,  tooltip, extclass, urlprefix, hashorslash, term.getId(), term.getId(), extflag) )
                self.emit2buff(buff, ' %s<ul>' % (" " * 4 * depth))

                # handle our subtypes
                for item in subTypes:
                    subBuff = StringIO.StringIO()
                    got = self.traverseForHTML(item, depth + 1, hashorslash=hashorslash, layers=layers, idprefix=idprefix, urlprefix=urlprefix, traverseAllLayers=traverseAllLayers,buff=subBuff)
                    if got:
                        self.emit2buff(buff,subBuff.getvalue())
                    subBuff.close()
                self.emit2buff(buff, ' %s</ul>' % (" " * 4 * depth))
            else:
                # we are a supertype but we visited this type before, e.g. saw Restaurant via Place then via Organization
                seencount = self.visited.count(term.getId())
                idstring = "%s%s" % (idstring, "+" * seencount)
                seen = '  <a href="#%s">+</a> ' % term.getId()
                self.emit2buff(buff, ' %s<li class="tbranch" id="%s"><a %s %s href="%s%s%s">%s</a>%s%s' % (" " * 4 * depth, idstring,  tooltip, extclass, urlprefix, hashorslash, term.getId(), term.getId(), extflag, seen) )
        # leaf nodes
        if len(subTypes) == 0:
            gotOutput = True
            seen = ""
            if term.getId() in self.visited:
                seencount = self.visited.count(term.getId())
                idstring = "%s%s" % (idstring, "+" * seencount)
                seen = '  <a href="#%s">+</a> ' % term.getId()

            self.emit2buff(buff, '%s<li class="tleaf" id="%s"><a %s %s href="%s%s%s">%s</a>%s%s' % (" " * depth, idstring, tooltip, extclass, urlprefix, hashorslash, term.getId(), term.getId(), extflag, seen ))

        self.visited.append(term.getId()) # remember our visit
        self.emit2buff(buff, ' %s</li>' % (" " * 4 * depth) )

        if localBuff:
            self.emit(buff.getvalue())
            buff.close()

        return gotOutput

    # based on http://danbri.org/2013/SchemaD3/examples/4063550/hackathon-schema.js  - thanks @gregg, @sandro
    def traverseForJSONLD(self, term, depth = 0, last_at_this_level = True, supertype="None", layers='core'):
        emit_debug = False
        if not term or not term.getId():
            log.error("Error None value passed to traverseForJSONLD()")
            return
        if term.getId() in self.visited:
            # self.emit("skipping %s - already visited" % node.id)
            return
        self.visited.append(term.getId())
        p1 = " " * 4 * depth
        if emit_debug:
            self.emit("%s# @id: %s last_at_this_level: %s" % (p1, term.getId(), last_at_this_level))
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
        for st in term.getSubs():
            if not st.getId() in self.visited:
                unseen_subtypes.append(st)
        unvisited_subtype_count = len(unseen_subtypes)
        subtype_count = len( term.getSubs() )

        supertx = "{}".format( '"rdfs:subClassOf": "schema:%s", ' % supertype.getId() if supertype != "None" else '' )
        maybe_comma = "{}".format("," if unvisited_subtype_count > 0 else "")
        comment = term.getComment().strip()
        comment = ShortenOnSentence(StripHtmlTags(comment),60)

        def encode4json(s):
            return json.dumps(s)

        self.emit('\n%s{\n%s\n%s"@type": "rdfs:Class", %s "description": %s,\n%s"name": "%s",\n%s"@id": "schema:%s",\n%s"layer": "%s"%s'
                  % (p1, ctx, p1,                 supertx,            encode4json(comment),     p1,   term.getId(), p1,        term.getId(), p1, term.getLayer(), maybe_comma))

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
                self.traverseForJSONLD(t, depth + 1, inner_lastness, supertype=term, layers=layers)

            self.emit("%s  ]%s" % (p1,  "{}".format( "" if not last_at_this_level else '' ) ) )

        maybe_comma = "{}".format( ',' if not last_at_this_level else '' )
        self.emit('\n%s}%s\n' % (p1, maybe_comma))



def GetExamples(term, layers='core'):
    """Returns the examples (if any) for some Unit node."""
    return LoadTermExamples(term)

def GetExtMappingsRDFa(term):
    """Self-contained chunk of RDFa HTML markup with mappings for this term."""
    equivs = term.getEquivalents()
    if (term.isClass()):
        if len(equivs) > 0:
            markup = ''
            for c in equivs:

                if (c.startswith('http')):
                  markup = markup + "<link property=\"owl:equivalentClass\" href=\"%s\"/>\n" % c
                else:
                  markup = markup + "<link property=\"owl:equivalentClass\" resource=\"%s\"/>\n" % c

            return markup
    if (term.isProperty()):
        if len(equivs) > 0:
            markup = ''
            for c in equivs:
                markup = markup + "<link property=\"owl:equivalentProperty\" href=\"%s\"/>\n" % c
            return markup
    return "<!-- no external mappings noted for this term. -->"

class ShowUnit (webapp2.RequestHandler):
    """ShowUnit exposes schema.org terms via Web RequestHandler
    (HTML/HTTP etc.).
    """

    def emitCacheHeaders(self):
        """Send cache-related headers via HTTP."""
        if "CACHE_CONTROL" in os.environ:
            log.info("Setting http cache control to '%s' from .yaml" % os.environ["CACHE_CONTROL"])
            self.response.headers['Cache-Control'] = os.environ["CACHE_CONTROL"]
        else:
            self.response.headers['Cache-Control'] = "public, max-age=600" # 10m
        self.response.headers['Vary'] = "Accept, Accept-Encoding"

    def write(self, str):
        """Write some text to Web server's output stream."""
        self.outputStrings.append(str)


    def moreInfoBlock(self, term, layer='core'):

        # if we think we have more info on this term, show a bulleted list of extra items.
        moreblock = os.environ.get("MOREBLOCK")
        if not moreblock or (moreblock.lower() == "false"):
            return ""


        # defaults
        bugs = ["No known open issues."]
        mappings = ["No recorded schema mappings."]
        items = bugs + mappings


        feedback_url = FEEDBACK_FORM_BASE_URL.format(term.getUri(), term.getType())
        items = [
        self.emitCanonicalURL(term),
        self.emitEquivalents(term),

        "<a href='{0}'>Leave public feedback on this term &#128172;</a>".format(feedback_url),
        "<a href='https://github.com/schemaorg/schemaorg/issues?q=is%3Aissue+is%3Aopen+{0}'>Check for open issues.</a>".format(term.getId())

        ]
        if term.getLayer() != "core":
            items.append("'{0}' is mentioned in the <a href='{1}'>{2}</a> extention.".format( term.getId(), makeUrl(term.getLayer(),"",full=True), term.getLayer() ))

        moreinfo = """<div>
        <div id='infobox' style='text-align: right;' role="checkbox" aria-checked="false"><label for="morecheck"><b><span style="cursor: pointer;">[more...]</span></b></label></div>
        <input type='checkbox' checked="checked" style='display: none' id=morecheck><div id='infomsg' style='background-color: #EEEEEE; text-align: left; padding: 0.5em;'>
        <ul>"""

        for i in items:
            if i and len(i):
                moreinfo += "<li>%s</li>" % i

#          <li>mappings to other terms.</li>
#          <li>or links to open issues.</li>

        moreinfo += "</ul>\n</div>\n</div>\n"
        return moreinfo



    def ml(self, term, label='', title='', prop='', hashorslash='/'):
        """ml ('make link')
        Returns an HTML-formatted link to the class or property URL

        * label = optional anchor text label for the link
        * title = optional title attribute on the link
        * prop = an optional property value to apply to the A element
        """
        if not term:
            return ""

        if ":" in term.getId():
            return self.external_ml(term,title=title, prop=prop)

        if label=='':
          label = term.getLabel()
        if title != '':
          title = " title=\"%s\"" % (title)
        if prop:
            prop = " property=\"%s\"" % (prop)

        rdfalink = ''
        if prop:
            rdfalink = '<link %s href="%s%s" />' % (prop,api.SdoConfig.vocabUri(),label)

        if(term.id == "DataType"):  #Special case
            return "%s<a href=\"%s\">%s</a>" % (rdfalink,term.getId(), term.getId())

        urlprefix = "."
        home = term.getLayer()

        if home in ENABLED_EXTENSIONS and home != getHostExt():
            port = ""
            if getHostPort() != "80":
                port = ":%s" % getHostPort()
            urlprefix = makeUrl(home,full=True)

        extclass = ""
        extflag = ""
        tooltip = ""
        if home != "core" and home != "":
            if home != "meta":
                extclass = "class=\"ext ext-%s\" " % home
            extflag = EXTENSION_SUFFIX
            tooltip = "title=\"Defined in extension: %s.schema.org\" " % home

        return "%s<a %s %s href=\"%s%s%s\"%s>%s</a>%s" % (rdfalink,tooltip, extclass, urlprefix, hashorslash, term.getId(), title, label, extflag)
        #return "<a %s %s href=\"%s%s%s\"%s%s>%s</a>%s" % (tooltip, extclass, urlprefix, hashorslash, node.id, prop, title, label, extflag)

    def external_ml(self, term, title='', prop=''):
        #log.info("EXTERNAL!!!! %s %s " % (term.getLabel(),term.getId()))

        name = term.getId()

        if not ":" in name:
            return name

        if name.startswith("http") and '#' in name:
            x = name.split("#")
            path = x[0] + "#"
            val = x[1]
            voc = getPrefixForPath(path)


        elif name.startswith("http"):
            val = os.path.basename(name)
            path = name[:len(name) - len(val)]
            voc = getPrefixForPath(path)

        else:
            x = name.split(":")
            voc = x[0]
            val = x[1]
            path = getPathForPrefix(voc)
            if path:
                if not path.endswith("#") and not path.endswith("/"):
                    path += "/"
        if title != '':
          title = " title=\"%s\"" % str(title)
        if prop:
            prop = " property=\"%s\"" % (prop)
        rdfalink = ''
        if prop:
            rdfalink = '<link %s href="%s%s" />' % (prop,api.SdoConfig.vocabUri(),label)

        return "%s<a %s href=\"%s%s\" class=\"externlink\" target=\"_blank\">%s:%s</a>" % (rdfalink,title,path,val,voc,val)



    def makeLinksFromArray(self, nodearray, tooltip=''):
        """Make a comma separate list of links via ml() function.

        * tooltip - optional text to use as title of all links
        """
        hyperlinks = []
        for f in nodearray:
           hyperlinks.append(self.ml(f, f.id, tooltip))
        return (", ".join(hyperlinks))

    def emitUnitHeaders(self, term, layers='core'):
        """Write out the HTML page headers for this node."""
        self.write("<h1 property=\"rdfs:label\" class=\"page-title\">")
        self.write(term.getLabel())
        self.write("</h1>\n")
        home = term.getLayer()
        if home != "core" and home != "":
            exthome = "%s.schema.org" % home
            exthomeurl = uri = makeUrl(home,"/",full=True)
            linktext = "Defined in the %s section."
            lt = SdoConfig.getDescriptor(home,"linktext")
            if lt:
                if lt.count("%s") != 1:
                    log.error("ERROR Linktext '%s' includes %s '%%s' - only 1 permitted" % (lt,lt.count()))
                else:
                    linktext = lt
            t = SdoConfig.getDescriptor(home,"disambiguatingDescription")
            linkinsert = "<a title=\"%s\" href=\"%s\">%s</a>" % (t,exthomeurl,home)

            self.write("<span class=\"extlink\">")
            self.write(linktext % linkinsert)
            self.write("<br/></span>")
        if not ENABLEMOREINFO:
            self.write(self.emitCanonicalURL(term))
            eq = self.emitEquivalents(term)
            if eq and len(eq):
                self.write()

        self.BreadCrumbs(term)

        comment = term.getComment()

        self.write(" <div property=\"rdfs:comment\">%s</div>\n\n" % (comment) + "\n")
        usage = GetUsage(term.getId())
        #if len(usage):
        #    self.write(" <br/><div>Usage: %s</div>\n\n" % (usage) + "\n")

        if ENABLEMOREINFO:
            self.write(self.moreInfoBlock(term))

    def emitCanonicalURL(self,term):
        output = StringIO.StringIO()
        site = SdoConfig.vocabUri()

        cURL = "%s://schema.org/%s" % (CANONICALSCHEME,term.getId())
        output.write(" <span class=\"canonicalUrl\">Canonical URL: <a href=\"%s\">%s</a></span> " % (cURL, cURL))

        if CANONICALSCHEME == "http":
            other = "https"
        else:
            other = "http"
        sa = '\n<link  property="sameAs" href="%s://schema.org/%s" />' % (other,term.getId())
        output.write(sa)

        return output.getvalue()

    def emitEquivalents(self,term):
        buff = StringIO.StringIO()
        equivs = term.getEquivalents()
        if len(equivs) > 0:
            if (term.isClass() or term.isDataType()):
                label = "Equivalent Class:"
            else:
                label = "Equivalent Property:"
            br = ""
            for e in equivs:
                eq = VTerm.getTerm(e,createReference=True)
                log.info("EQUIVALENT %s %s" % (e,eq))
                title = eq.getUri()
                buff.write("%s<span class=\"equivalents\">%s %s</span> " % (br,label,self.ml(eq,title=title)))
                br = "<br/>"
        return buff.getvalue()

    # Stacks to support multiple inheritance
    crumbStacks = []
    def BreadCrumbs(self, term):

        self.crumbStacks = term.getParentPaths()

        for cstack in self.crumbStacks:
            if term.isProperty():
                cstack.append(VTerm.getTerm("http://schema.org/Property"))
                cstack.append(VTerm.getTerm("http://schema.org/Thing"))
            elif term.isDataType() and not term.id == "DataType":
                cstack.append(VTerm.getTerm("http://schema.org/DataType"))


        enuma = term.isEnumerationValue()

        crumbsout = []
        for row in range(len(self.crumbStacks)):
           thisrow = ""
           targ = self.crumbStacks[row][len(self.crumbStacks[row])-1]
           if not targ:
                continue
           count = 0
           while(len(self.crumbStacks[row]) > 0):
                propertyval = None
                n = self.crumbStacks[row].pop()

                if((len(self.crumbStacks[row]) == 1) and n and
                    not ":" in n.id) : #penultimate crumb that is not a non-schema reference
                    if term.isProperty():
                        if n.isProperty(): #Can only be a subproperty of a property
                            propertyval = "rdfs:subPropertyOf"
                    else:
                        propertyval = "rdfs:subClassOf"

                if(count > 0):
                    if((len(self.crumbStacks[row]) == 0) and enuma): #final crumb
                        thisrow += " :: "
                    else:
                        thisrow += " &gt; "
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
    def WalkCrumbs(self, term, cstack):
        if ":" in term.getId():  #Suppress external class references
            return

        cstack.append(term)
        tmpStacks = []
        tmpStacks.append(cstack)
        supers = term.getSupers()

        for i in range(len(supers)):
            if(i > 0):
                t = cstack[:]
                tmpStacks.append(t)
                self.crumbStacks.append(t)
        x = 0

        for p in supers:
            self.WalkCrumbs(p,tmpStacks[x])
            x += 1

    def emitSimplePropertiesPerType(self, cl, layers="core", out=None, hashorslash="/"):
        """Emits a simple list of properties applicable to the specified type."""

        if not out:
            out = self

        out.write("<ul class='props4type'>")

        for prop in VTerm.getTerm(cl).getProperties():
            if prop.superseded():
                continue
            out.write("<li><a href='%s%s'>%s</a></li>" % ( hashorslash, prop.getId(), prop.getId()  ))

        out.write("</ul>\n\n")

    def emitSimplePropertiesIntoType(self, cl, layers="core", out=None, hashorslash="/"):
        """Emits a simple list of properties whose values are the specified type."""

        if not out:
            out = self

        out.write("<ul class='props2type'>")

        for prop in VTerm.getTerm(cl).getTargetOf():
            if prop.superseded():
                continue
            out.write("<li><a href='%s%s'>%s</a></li>" % ( hashorslash, prop.getId(), prop.getId()  ))
        out.write("</ul>\n\n")

    def hideAtticTerm(self,term):
        if getHostExt() == ATTIC:
            return False
        if term.inLayers([ATTIC]):
            return True
        return False

    def ClassProperties (self, cl, subclass=False, term=None, out=None, hashorslash="/"):
        """Write out a table of properties for a per-type page."""
        if not out:
            out = self

        propcount = 0

        headerPrinted = False
        props = cl.getProperties()

        for prop in props:
            if prop.superseded() or self.hideAtticTerm(prop):
                continue
            olderprops = prop.getSupersedes()
            inverseprop = prop.getInverseOf()
            ranges = prop.getRanges()
            doms = prop.getDomains()
            comment = prop.getComment()
            if ":" in prop.id and comment == "-":
                comment = "Term from external vocabulary"
            if not getAppVar("tableHdr"):
                setAppVar("tableHdr",True)
                if ((term.isClass() or term.isEnumeration()) and not term.isDataType() and term.id != "DataType"):
                    self.write("<table class=\"definition-table\">\n        <thead>\n  <tr><th>Property</th><th>Expected Type</th><th>Description</th>               \n  </tr>\n  </thead>\n\n")
                self.tablehdr = True
            if (not headerPrinted):
                class_head = self.ml(cl)
                out.write("<tr class=\"supertype\">\n     <th class=\"supertype-name\" colspan=\"3\">Properties from %s</th>\n  \n</tr>\n\n<tbody class=\"supertype\">\n  " % (class_head))
                headerPrinted = True

            out.write("<tr typeof=\"rdfs:Property\" resource=\"%s\">\n    \n      <th class=\"prop-nam\" scope=\"row\">\n\n<code property=\"rdfs:label\">%s</code>\n    </th>\n " % (prop.getUri(), self.ml(prop)))
            out.write("<td class=\"prop-ect\">\n")
            first_range = True
            for r in ranges:
                if (not first_range):
                    out.write(" or <br/> ")
                first_range = False
                out.write(self.ml(r, prop='rangeIncludes'))
                out.write("&nbsp;")
            for d in doms:
                out.write("<link property=\"domainIncludes\" href=\"%s\">" % d.getUri())
            out.write("</td>")
            out.write("<td class=\"prop-desc\" property=\"rdfs:comment\">%s" % (comment))
            if (olderprops and len(olderprops) > 0):
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

       #log.info("SUPERS %s" % VTerm.term2str(cl.getSupers()))

       for p in cl.getSupers():

          if not p.isReference() and p.inLayers(layers):
               continue


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
           if cl.getId() == "DataType":
               self.write("<h4>Subclass of:<h4>")
           else:
               self.write("<h4>Available supertypes defined elsewhere</h4>")
           self.write("<ul>")
           self.write(content)
           self.write("</ul>")
       buff.close()

    """    def emitClassExtensionProperties (self, cl, layers="core", out=None):
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
    """

    def _ClassExtensionProperties (self, out, cl, layers="core"):
        """Write out a list of properties not displayed as they are in extensions for a per-type page."""

        di = Unit.GetUnit("schema:domainIncludes")

        targetlayers=self.appropriateLayers(layers)
        #log.info("Appropriate targets %s" % targetlayers)
        exts = {}

        for prop in sorted(GetSources(di, cl, targetlayers), key=lambda u: u.id):
            if ":" in prop.id:
                continue
            if (prop.superseded(layers=targetlayers)):
                continue
            if inLayer(layers,prop): #Already in the correct layer - no need to report
                continue
            if inLayer("meta",prop): #Suppress mentioning properties from the 'meta' extension.
                continue
            ext = prop.getHomeLayer()

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


    def emitClassIncomingProperties (self, term, out=None, hashorslash="/"):
        """Write out a table of incoming properties for a per-type page."""
        if not out:
            out = self

        headerPrinted = False
        props = term.getTargetOf()
        for prop in props:
            if (prop.superseded()):
                continue
            supersedes = prop.getSupersedes()
            inverseprop = prop.getInverseOf()
            ranges = prop.getRanges()
            domains = prop.getDomains()
            comment = prop.getComment()

            if (not headerPrinted):
                self.write("<br/><br/><div id=\"incoming\">Instances of %s may appear as values for the following properties</div><br/>" % (self.ml(term)))
                self.write("<table class=\"definition-table\">\n        \n  \n<thead>\n  <tr><th>Property</th><th>On Types</th><th>Description</th>               \n  </tr>\n</thead>\n\n")

                headerPrinted = True

            self.write("<tr>\n<th class=\"prop-nam\" scope=\"row\">\n <code>%s</code>\n</th>\n " % (self.ml(prop)) + "\n")
            self.write("<td class=\"prop-ect\">\n")
            first_dom = True
            for d in domains:
                if (not first_dom):
                    self.write(" or<br/> ")
                first_dom = False
                self.write(self.ml(d))
                self.write("&nbsp;")
            self.write("</td>")
            self.write("<td class=\"prop-desc\">%s " % (comment))
            if supersedes:
                self.write(" Supersedes")
                first = True
                for s in supersedes:
                    if first:
                        first = False
                        self.write(",")
                    self.write(" %s" % self.ml(s))
                self.write(". ")
            if inverseprop:
                self.write("<br/> inverse property: %s." % (self.ml(inverseprop)) )

            self.write("</td></tr>")
        if (headerPrinted):
            self.write("</table>\n")

    def emitRangeTypesForProperty(self, node, layers="core", out=None, hashorslash="/"):
        """Write out simple HTML summary of this property's expected types."""
        if not out:
            out = self

        out.write("<ul class='attrrangesummary'>")
        for rt in VTerm.getTerm(node).getRanges():
            out.write("<li><a href='%s%s'>%s</a></li>" % ( hashorslash, rt.getId(), rt.getId()  ))
        out.write("</ul>\n\n")


    def emitDomainTypesForProperty(self, node, layers="core", out=None, hashorslash="/"):
        """Write out simple HTML summary of types that expect this property."""
        if not out:
            out = self

        out.write("<ul class='attrdomainsummary'>")
        for dt in VTerm.getTerm(node).getDomains():
            out.write("<li><a href='%s%s'>%s</a></li>" % ( hashorslash, dt.getId(), dt.getId()  ))
        out.write("</ul>\n\n")


    def emitAttributeProperties(self, term, out=None, hashorslash="/"):
        """Write out properties of this property, for a per-property page."""
        if not out:
            out = self

        ranges = term.getRanges()
        domains =term.getDomains()

        inverseprop = term.getInverseOf()
        subprops = term.getSubs()
        superprops = term.getSupers()


        if (inverseprop != None):
            tt = "This means the same thing, but with the relationship direction reversed."
            out.write("<p>Inverse-property: %s.</p>" % (self.ml(inverseprop, inverseprop.getId(),tt, prop=False, hashorslash=hashorslash)) )

        out.write("<table class=\"definition-table\">\n")
        out.write("<thead>\n  <tr>\n    <th>Values expected to be one of these types</th>\n  </tr>\n</thead>\n\n  <tr>\n    <td>\n      ")

        first_range = True
        for r in ranges:
            if (not first_range):
                out.write("<br/>")
            first_range = False
            tt = "The '%s' property has values that include instances of the '%s' type." % (term.getId(), r.getId())
            out.write(" <code>%s</code> " % (self.ml(r, r.getId(), tt, prop="rangeIncludes", hashorslash=hashorslash) +"\n"))
        out.write("    </td>\n  </tr>\n</table>\n\n")

        first_domain = True
        out.write("<table class=\"definition-table\">\n")
        out.write("  <thead>\n    <tr>\n      <th>Used on these types</th>\n    </tr>\n</thead>\n<tr>\n  <td>")
        for d in domains:
            if (not first_domain):
                out.write("<br/>")
            first_domain = False
            tt = "The '%s' property is used on the '%s' type." % (term.getId(), d.getId())
            out.write("\n    <code>%s</code> " % (self.ml(d, d.getId(), tt, prop="domainIncludes",hashorslash=hashorslash)+"\n" ))
        out.write("      </td>\n    </tr>\n</table>\n\n")

        # Sub-properties
        if (subprops != None and len(subprops) > 0):
            out.write("<table class=\"definition-table\">\n")
            out.write("  <thead>\n    <tr>\n      <th>Sub-properties</th>\n    </tr>\n</thead>\n")
            for sp in subprops:
                c = ShortenOnSentence(StripHtmlTags( sp.getComment() ),60)
                tt = "%s: ''%s''" % ( sp.getId(), c)
                out.write("\n    <tr><td><code>%s</code></td></tr>\n" % (self.ml(sp, sp.getId(), tt, hashorslash=hashorslash)))
            out.write("\n</table>\n\n")

        # Super-properties
        if (superprops != None and  len(superprops) > 0):
            out.write("<table class=\"definition-table\">\n")
            out.write("  <thead>\n    <tr>\n      <th>Super-properties</th>\n    </tr>\n</thead>\n")
            for sp in superprops:
                c = ShortenOnSentence(StripHtmlTags( sp.getComment() ),60)
                tt = "%s: ''%s''" % ( sp.getId(), c)
                out.write("\n    <tr><td><code>%s</code></td></tr>\n" % (self.ml(sp, sp.getId(), tt, hashorslash=hashorslash)))
            out.write("\n</table>\n\n")

    def emitSupersedes(self, term, out=None, hashorslash="/"):
        """Write out Supersedes and/or Superseded by for this term"""

        if not out:
            out = self
        newerprop = term.getSupersededBy() # None of one. e.g. we're on 'seller'(new) page, we get 'vendor'(old)
        #olderprop = node.supersedes(layers=layers) # None or one
        olderprops = term.getSupersedes()


        # Supersedes
        if (olderprops != None and len(olderprops) > 0):
            out.write("<table class=\"definition-table\">\n")
            out.write("  <thead>\n    <tr>\n      <th>Supersedes</th>\n    </tr>\n</thead>\n")

            for o in olderprops:
                c = ShortenOnSentence(StripHtmlTags( o.getComment() ),60)
                tt = "%s: ''%s''" % ( o.getId(), c)
                out.write("\n    <tr><td><code>%s</code></td></tr>\n" % (self.ml(o, o.getId(), tt)))
                log.info("Super %s" % o.getId())
            out.write("\n</table>\n\n")

        # supersededBy (at most one direct successor)
        if (newerprop != None):
            out.write("<table class=\"definition-table\">\n")
            out.write("  <thead>\n    <tr>\n      <th><a href=\"/supersededBy\">supersededBy</a></th>\n    </tr>\n</thead>\n")
            c = ShortenOnSentence(StripHtmlTags( newerprop.getComment() ),60)
            tt = "%s: ''%s''" % ( newerprop.getId(), c)
            out.write("\n    <tr><td><code>%s</code></td></tr>\n" % (self.ml(newerprop, newerprop.getId(), tt)))
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
        json_score = mimereq.get('application/json', 10)
        log.info( "accept_header: " + str(accept_header) + " mimereq: "+str(mimereq) + "Scores H:{0} XH:{1} JL:{2} J:{3}".format(html_score,xhtml_score,jsonld_score,json_score))

        if (ENABLE_JSONLD_CONTEXT and ((jsonld_score < html_score and jsonld_score < xhtml_score) or (json_score < html_score and json_score < xhtml_score))):
            self.response.set_status(302,"Found")
            if jsonld_score < json_score:
                self.response.headers['Location'] = makeUrl("","docs/jsonldcontext.jsonld")
            else:
                self.response.headers['Location'] = makeUrl("","docs/jsonldcontext.json")
            self.emitCacheHeaders()
            return False #don't cache this redirect
        else:
            # Serve a homepage from template
            # the .tpl has responsibility for extension homepages
            # TODO: pass in extension, base_domain etc.
            #sitekeyedhomepage = "homepage %s" % getSiteName()
            ext = getHostExt()

            if ext == "core":
                ext = ""

            if len(ext):
                ext += "."
            sitekeyedhomepage = "%sindex.html" % ext
            hp = getPageFromStore(sitekeyedhomepage)
            self.response.headers['Content-Type'] = "text/html"
            self.emitCacheHeaders()
            if hp:
                self.response.out.write( hp )
                #log.info("Served datacache homepage.tpl key: %s" % sitekeyedhomepage)
            else:
                template_values = {
                    'ext_contents': self.handleExtensionContents(getHostExt()),
                    'home_page': "True",
                }
                page = templateRender('homepage.tpl', node, template_values)
                self.response.out.write( page )
                log.debug("Served and cached fresh homepage.tpl key: %s " % sitekeyedhomepage)

                setAppVar(CLOUDEXTRAMETA,{'x-goog-meta-sdotermlayer': getHostExt()})
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
        self.response.out.write(self.buildSchemaorgHeaders(node, ext_mappings, sitemode, sitename, layers))


    def buildSiteHeaders(self, term, ext_mappings='', sitemode="default", sitename="schema.org"):
        """
        Generates, caches and emits HTML headers for class, property and enumeration pages. Leaves <body> open.

        * entry = name of the class or property
        """
        buff = sdoStringIO()

        rdfs_type = 'rdfs:Class'
        entry = term.id
        if term.isProperty():
            rdfs_type = 'rdfs:Property'

        desc = entry
        desc = self.getMetaDescription(term, lengthHint=200)

        template_values = {
            'entry': str(entry),
            'desc' : desc,
            'menu_sel': "Schemas",
            'rdfs_type': rdfs_type,
            'ext_mappings': ext_mappings,
            'noindexpage': noindexpages
        }
        out = templateRender('genericTermPageHeader.tpl', term, template_values)
        buff.write(out)

        ret = buff.getvalue()
        buff.close()
        return ret

    def buildSchemaorgHeaders(self, node, ext_mappings='', sitemode="default", sitename="schema.org", layers="core"):
        """
        Generates, caches and emits HTML headers for class, property and enumeration pages. Leaves <body> open.

        * entry = name of the class or property
        """
        buff = sdoStringIO()

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

        desc = entry
        if anode:
            desc = self.getMetaDescription(node, layers=layers, lengthHint=200)

        template_values = {
            'entry': str(entry),
            'desc' : desc,
            'menu_sel': "Schemas",
            'rdfs_type': rdfs_type,
            'ext_mappings': ext_mappings,
            'noindexpage': noindexpages
        }
        out = templateRender('genericTermPageHeader.tpl', node, template_values)
        buff.write(out)

        ret = buff.getvalue()
        buff.close()
        return ret

    def getMetaDescription(self, term, layers="core",lengthHint=250):
        ins = ""
        if term.isEnumeration():
            ins += " Enumeration Type"
        elif term.isClass():
            ins += " Type"
        elif term.isProperty():
            ins += " Property"
        elif term.isEnumerationValue():
            ins += " Enumeration Value"

        desc = "Schema.org%s: %s - " % (ins, term.id)

        lengthHint -= len(desc)

        comment = term.getComment()

        desc += ShortenOnSentence(StripHtmlTags(comment),lengthHint)

        return desc

    def appropriateLayers(self,layers="core"):
        if ATTIC in layers:
            return ALL_LAYERS
        return ALL_LAYERS_NO_ATTIC

    def emitExactTermPage(self, term, layers="core"):
        """Emit a Web page that exactly matches this node."""
        log.info("EXACT PAGE: %s" % term.getId())
        self.outputStrings = [] # blank slate
        cached = getPageFromStore(term.getId())

        if (cached != None):
            log.info("GOT CACHED page for %s" % term.getId())
            self.response.write(cached)
            return
        log.info("Building page")

        ext_mappings = GetExtMappingsRDFa(term)
        self.write(self.buildSiteHeaders(term, ext_mappings, sitemode, getSiteName()))

        #log.info("Done buildSiteHeaders")
        #log.info("Stak %s" % term.getTermStack())

        self.emitUnitHeaders(term) # writes <h1><table>...
        stack = self._removeStackDupes(term.getTermStack())
        setAppVar("tableHdr",False)
        if term.isClass() or term.isDataType() or term.isEnumeration():
            for p in stack:
                self.ClassProperties(p, p==[0], out=self, term=term)
            if getAppVar("tableHdr"):
                self.write("\n\n</table>\n\n")


            self.emitClassIncomingProperties(term)

            self.emitClassExtensionSuperclasses(term,layers)

            #self.emitClassExtensionProperties(p,layers) #Not needed since extension defined properties displayed in main listing

        elif term.isProperty():
            self.emitAttributeProperties(term)

        elif term.isDataType():
            self.emitClassIncomingProperties(term)

        self.emitSupersedes(term)
        self.emitchildren(term)
        self.emitAcksAndSources(term)
        self.emitTermExamples(term)

        self.write(" <br/>\n\n</div>\n</body>\n<!-- AppEngineVersion %s (%s)-->\n</html>" % (getAppEngineVersion(),appver))

        page = "".join(self.outputStrings)
        setAppVar(CLOUDEXTRAMETA,{'x-goog-meta-sdotermlayer': term.getLayer()})
        PageStore.put(term.getId(),page)

        self.response.write(page)

    def emitTermExamples(self,term):
        examples = GetExamples(term)
        log.debug("Rendering n=%s examples" % len(examples))
        if (len(examples) > 0):
            example_labels = [
              ('Without Markup', 'original_html', 'selected'),
              ('Microdata', 'microdata', ''),
              ('RDFa', 'rdfa', ''),
              ('JSON-LD', 'jsonld', ''),
            ]
            self.write("<b><a %s >Examples</a></b><br/><br/>\n\n" % self.showlink("examples"))
            exNum = 0
            for ex in sorted(examples, key=lambda u: u.keyvalue):

                #if not ex.egmeta["layer"] in layers: #Example defined in extension we are not in
                    #continue
                exNum += 1
                id="example-%s" % exNum
                if "id" in ex.egmeta:
                    id = ex.egmeta["id"]
                self.write("<div><a %s>Example %s</a></div>" % (self.showlink(id),exNum))
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

    def showlink(self,id):
        ret = ""
        if id and len(id):
            ret = " id=\"%s\" title=\"Link: #%s\" href=\"#%s\" class=\"clickableAnchor\" " % (id,id,id)
        return ret

    def _removeStackDupes(self,stack):
        cleanstack = []
        i = len(stack)
        while i:
            i -= 1
            if not stack[i] in cleanstack:
                cleanstack.insert(0,stack[i])

        return cleanstack

    def emitAcksAndSources(self,term):
        sources = term.getSources()
        if len(sources):
            s = ""
            if len(sources) > 1:
                s = "s"
            self.write("<h4  id=\"acks\">Source%s</h4>\n" % s)
            for val in sources:
                if val.startswith("http://") or val.startswith("https://"):
                    val = "[%s](%s)" % (val,val) #Put into markdown format
                self.write(Markdown.parse(val,True))

        acknowledgements = term.getAcknowledgements()
        if len(acknowledgements):
            s = ""
            if len(acknowledgements) > 1:
                s = "s"
            self.write("<h4  id=\"acks\">Acknowledgement%s</h4>\n" % s)
            for ack in sorted(acknowledgements):
                self.write(Markdown.parse(str(ack),True))


    def emitchildren(self,term):
            children = term.getSubs()

            log.info("CHILDREN: %s" % VTerm.term2str(children))
            isEnumAnc = VTerm.isEnumerationAncestor(term)

            if (len(children) > 0):
                buff = StringIO.StringIO()
                buff2 = StringIO.StringIO()
                for c in children:
                    if c.superseded() or self.hideAtticTerm(c):
                        continue
                    if isEnumAnc and (c.parent == term or term.isEnumeration()):
                        buff2.write("<li> %s </li>" % (self.ml(c)))
                    else:
                        buff.write("<li> %s </li>" % (self.ml(c)))

                if (len(buff.getvalue()) > 0 and not term.isProperty()):
                    if term.isDataType():
                        self.write("<br/><b><a %s>More specific DataTypes</a></b><ul>" % self.showlink("subtypes"))
                    elif term.isClass() or term.isEnumerationValue():
                        self.write("<br/><b><a %s>More specific Types</a></b><ul>" % self.showlink("subtypes"))
                    self.write(buff.getvalue())

                if isEnumAnc and len(buff2.getvalue()) > 0:
                    self.write("<br/><b><a %s>Enumeration members</a></b><ul>" % self.showlink("enumbers"))
                    self.write(buff2.getvalue())
                self.write("</ul>")

                buff.close()

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
        log.debug("?ext= extension list: '%s' " % ", ".join(extlist))

        # 2. Ignore ?ext=, start with 'core' only.
        layerlist = [ "core"]

        # 3. Use host_ext if set, e.g. 'bib' from bib.schema.org
        if getHostExt() != None:
            log.debug("Host: %s host_ext: %s" % ( self.request.host , getHostExt() ) )
            extlist.append(getHostExt())

        # Report domain-requested extensions
        for x in extlist:
            #log.debug("Ext filter found: %s" % str(x))
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
        ctype = "text/plain"
        if (node=="docs/jsonldcontext.json.txt"):
            label = "txt:jsonldcontext.json.txt"
            ctype = "text/plain"
        elif (node=="docs/jsonldcontext.json"):
            label = "json:docs/jsonldcontext.json"
            ctype = "application/json"
        elif (node=="docs/jsonldcontext.jsonld"):
            label = "jsonld:docs/jsonldcontext.jsonld"
            ctype = "application/ld+json"
        else:
            return False

        self.response.headers['Content-Type'] = ctype

        jsonldcontext = getPageFromStore(label)
        if not jsonldcontext:
            jsonldcontext = GetJsonLdContext(layers=ALL_LAYERS)

            PageStore.put(label,jsonldcontext)

        if jsonldcontext:
            self.emitCacheHeaders()
            self.response.out.write( jsonldcontext )
            return True
        return False
        # see also handleHomepage for conneg'd version.

    def handleSchemasPage(self, node,  layerlist='core'):
        page = getPageFromStore(node)
        if page:
            self.response.out.write( page )
            log.debug("Serving recycled SchemasPage.")
            return True
        else:
            self.response.headers['Content-Type'] = "text/html"
            self.emitCacheHeaders()

            extensions = []
            for ex in sorted(ENABLED_EXTENSIONS):
                if ex != ATTIC:
                    t = SdoConfig.getDescriptor(ex,"disambiguatingDescription")
                    extensions.append("<a title=\"%s\" href=\"%s\">%s.schema.org</a>" % (t,makeUrl(ex,"",full=True),ex))

            page = templateRender('schemas.tpl', node, {'counts': self.getCounts(),
                                    'extensions': extensions,
                                    'attic': "<a href=\"%s\">%s.schema.org</a>" % (makeUrl(ATTIC,""),ATTIC),
                                    'menu_sel': "Schemas"})

            self.response.out.write( page )
            log.debug("Serving fresh SchemasPage.")
            PageStore.put(node,page)

            return True

    def handleDumpsPage(self, node,  layerlist='core'):
        self.response.headers['Content-Type'] = "text/html"
        self.emitCacheHeaders()

        page = getPageFromStore(node)

        if page:
            self.response.out.write( page)
            log.debug("Serving recycled DumpsPage.")
            return True
        else:
            extensions = sorted(ENABLED_EXTENSIONS)

            page = templateRender('developers.tpl', node, {'extensions': extensions,
                                    'version': SCHEMA_VERSION,
                                    'menu_sel': "Schemas"})

            self.response.out.write( page )
            log.debug("Serving fresh DumpsPage.")
            PageStore.put(node,page)

            return True

    def getCounts(self):
        log.info("counts")
        typesCount = str(countTypes(extension="core"))
        log.info("TYPES %s" % typesCount)
        propsCount = str(countProperties(extension="core"))
        log.info("PROPS %s" % propsCount)
        enumCount = str(countEnums(extension="core"))
        log.info("ENUMS %s" % enumCount)

        text = ""
        text += "The core vocabulary currently consists of %s Types, " % typesCount
        text += " %s Properties, " % propsCount
        text += "and %s Enumeration values." % enumCount
        return text


    def handleFullHierarchyPage(self, node,  layerlist='core'):
        #label = 'FullTreePage - %s' % getHostExt()
        #label = 'FullTreePage'
        urlprefix = ''
        label = node
        if label.startswith('docs/'):
            urlprefix = '..'

        if getPageFromStore(label):
            self.response.out.write( getPageFromStore(label) )
            log.debug("Serving recycled %s." % label)
            return True
        else:
            self.response.headers['Content-Type'] = "text/html"
            self.emitCacheHeaders()
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
            #local_label = "<h3>Core vocabulary</h3>"
            local_label = ""
            ext_button = ""

            tops = self.gettops()

            full_thing_tree = ""
            thing_tree = ""
            datatype_tree = ""
            first = True
            dtcount = 0
            tcount = 0
            mainroot = TypeHierarchyTree(local_label)
            dtroot = TypeHierarchyTree("<h4>Data Types</h4>")
            for t in tops:
                if not first:
                    local_label = ""
                first = False
                top = VTerm.getTerm(t)
                if top.isDataType() or top.getUri() == "http://schema.org/DataType":
                    dtcount += 1
                    dtroot.traverseForHTML(top, layers=layerlist, idprefix="D.", urlprefix=urlprefix)
                else:
                    tcount += 1
                    mainroot.traverseForHTML(top, layers=layerlist, idprefix="C.", urlprefix=urlprefix, traverseAllLayers=True)
            if dtcount:
                datatype_tree += dtroot.toHTML()
            if tcount:
                full_thing_tree += mainroot.toHTML()

            #fullmainroot = TypeHierarchyTree("<h3>Core plus all extension vocabularies</h3>")
            #fullmainroot.traverseForHTML(uThing, layers=ALL_LAYERS_NO_ATTIC, idprefix="CE.", urlprefix=urlprefix)
            #full_thing_tree = fullmainroot.toHTML()

            ext_thing_tree = ""
            #if len(extonlylist) > 0:
                #extroot = TypeHierarchyTree("<h3>Extension: %s</h3>" % extlist)
                #extroot.traverseForHTML(uThing, layers=extonlylist, traverseAllLayers=True, idprefix="E.", urlprefix=urlprefix)
                #ext_thing_tree = extroot.toHTML()

            #dtroot = TypeHierarchyTree("<h4>Data Types</h4>")
            #dtroot.traverseForHTML(uDataType, layers=layerlist, idprefix="D.", urlprefix=urlprefix)
            #datatype_tree = dtroot.toHTML()

            full_button = "Core plus all extension vocabularies"

            page = templateRender('full.tpl', node, { 'full_thing_tree': full_thing_tree,
                                    'datatype_tree': datatype_tree,
                                    'menu_sel': "Schemas"})

            self.response.out.write( page )
            log.debug("Serving fresh %s." % label)
            PageStore.put(label,page)

            return True

    def gettops(self):
        return rdfgettops()

    def handleJSONSchemaTree(self, node, layerlist='core'):
        """Handle a request for a JSON-LD tree representation of the schemas (RDFS-based)."""

        if isinstance(node, Unit):
            node = node.id

        self.response.headers['Content-Type'] = "application/ld+json"
        self.emitCacheHeaders()

        page = getPageFromStore(node)
        if page:
            self.response.out.write( page )
            log.debug("Serving recycled JSONLDThingTree.")
            return True
        else:
            mainroot = TypeHierarchyTree()
            mainroot.traverseForJSONLD(VTerm.getTerm("Thing"), layers=layerlist)
            thing_tree = mainroot.toJSON()
            self.response.out.write( thing_tree )
            log.debug("Serving fresh JSONLDThingTree.")
            PageStore.put(node,thing_tree)
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
            ah = re.sub( r";q=\d?\.\d+", '', ah).strip()
            log.debug("ACCEPT '%s'" % ah)
            if ah == "text/html":
                return False
            elif ah == "application/ld+json":
                target = ".jsonld"
            elif ah == "application/x-turtle" or ah == "text/turtle" or ah == "application/turtle":
                target = ".ttl"
            elif ah == "application/rdf+xml":
                target = ".rdf"
            elif ah == "text/plain" or ah == "application/n-triples" or ah == "text/n3" or ah == "application/n3":
                target = ".nt"
            elif ah == "text/csv":
                target = ".csv"
            if target:
                #log.info("GOT: %s" % target)
                break
        if target:
            self.response.set_status(303,"See Other")
            self.response.headers['Location'] = makeUrl("","%s%s" % (node,target))
            self.emitCacheHeaders()
            return True
        return False

    def handleExactTermPage(self, node, layers='core'):

        baseuri = SdoConfig.baseUri()

        if node.startswith(baseuri): #Special case will map full schema URI to the term name
            node = node[len(baseuri):]

        """Handle with requests for specific terms like /Person, /fooBar. """
        dataext = os.path.splitext(node)
        if dataext[1] in OUTPUTDATATYPES:
            ret = self.handleExactTermDataOutput(dataext[0],dataext[1])
            if ret == True:
                return True
        if self.checkConneg(node):
            return True
        log.info("GETTING TERM: %s" % node)
        term = VTerm.getTerm(node)

        if not term:
            return False

        if not self.checkNodeExt(term):
            return False

        if not SUBDOMAINS or term.inLayers(layers):
            self.emitExactTermPage(term, layers=layers)
            return True

    def checkNodeExt(self,term):
        if os.environ.get('STAYINEXTENTION',"False").lower() == "true":
            return True

        home = term.getLayer()
        ext = getHostExt()
        log.info("term: '%s' home: '%s' ext: '%s'" % (term,home,ext))
        if home == CORE and ext == '':
            return True

        if SUBDOMAINS:
            log.info("Checking for correct subdomain")
            if home == ext:
                return True

            if home == CORE:
                log.info("Redirecting to core entity")
                self.redirectToBase(term.getId(),full=True)
            else:
                log.info("Redirecting to '%s' entity" % home)
                self.redirectToExt(term.getId(),ext=home, full=True)
            return False
        else: #SUBDOMAINS == False
            if ext == '':
                return True
            else:
                 log.info("SUBDOMAINS dissabled - Redirecting to core entity")
                 self.redirectToBase(term.getId(),full=True)
            return False

    def handleExactTermDataOutput(self, node=None, outputtype=None):
        log.info("handleExactTermDataOutput Node: '%s'  Outputtype: '%s'" % (node, outputtype))
        ret = False
        file = None
        if node and outputtype:
            term = VTerm.getTerm(node)
            if term:
                ret = True
                index = "%s:%s%s" % (outputtype,node,outputtype)
                data = getPageFromStore(index)

                excludeAttic=True
                if getHostExt()== ATTIC:
                    excludeAttic=False
                if outputtype == ".csv":
                    self.response.headers['Content-Type'] = "text/csv; charset=utf-8"
                    if not data:
                        data = self.emitcsvTerm(term,excludeAttic)
                        PageStore.put(index,data)
                else:
                    format = None
                    if outputtype == ".jsonld":
                        self.response.headers['Content-Type'] = "application/ld+json; charset=utf-8"
                        format = "json-ld"
                    elif outputtype == ".json":
                        self.response.headers['Content-Type'] = "application/json; charset=utf-8"
                        format = "json"
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

    def emitcsvTerm(self,term,excludeAttic=True):
        csv = sdordf2csv(queryGraph=getQueryGraph(),fullGraph=getQueryGraph(),markdownComments=True,excludeAttic=excludeAttic)
        file = StringIO.StringIO()
        termUri = term.getUri()
        if term.isClass() or term.isEnumerationValue():
            csv.type2CSV(header=True,out=file)
            csv.type2CSV(term=termUri,header=False,out=file)
        elif term.isProperty():
            csv.prop2CSV(header=True,out=file)
            csv.prop2CSV(term=termUri,header=False,out=file)
        data = file.getvalue()
        file.close()
        return data


    def handle404Failure(self, node, layers="core", extrainfo=None, suggest=True):
        self.error(404)
        self.emitSchemaorgHeaders("404 Not Found")
        #404 could be called from any path, so output all potential locations of schemaorg.css
        self.response.out.write('<link rel="stylesheet" type="text/css" href="../docs/schemaorg.css" />')
        self.response.out.write('<link rel="stylesheet" type="text/css" href="docs/schemaorg.css" />')
        self.response.out.write('<link rel="stylesheet" type="text/css" href="/docs/schemaorg.css" />')

        self.response.out.write('<h3>404 Not Found.</h3><p><br/>Page not found. Please <a href="/">try the homepage.</a><br/><br/></p>')

        if suggest:
            clean_node = cleanPath(node)

            log.debug("404: clean_node: clean_node: %s node: %s" % (clean_node, node))

            base_term = VTerm.getTerm( node.rsplit('/')[0] )
            if base_term != None :
                self.response.out.write('<div>Perhaps you meant: <a href="/%s">%s</a></div> <br/><br/> ' % ( base_term.getId(), base_term.getId() ))

            base_actionprop = VTerm.getTerm( node.rsplit('-')[0] )
            if base_actionprop != None :
                self.response.out.write('<div>Looking for an <a href="/Action">Action</a>-related property? Note that xyz-input and xyz-output have <a href="/docs/actions.html">special meaning</a>. See also: <a href="/%s">%s</a></div> <br/><br/> ' % ( base_actionprop.getId(), base_actionprop.getId() ))

        if extrainfo:
            self.response.out.write("<div>%s</div>" % extrainfo)

        self.response.out.write("</div>\n</body>\n<!--AppEngineVersion %s -->\n</html>\n"  % getAppEngineVersion())

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
            log.info("Defaulting to current version- %s" % SCHEMA_VERSION)
            requested_version = SCHEMA_VERSION

        if requested_version in releaselog:
            log.info("Version '%s' was released on %s. Serving from filesystem." % ( node, releaselog[requested_version] ))

            version_rdfa = "data/releases/%s/schema.rdfa" % requested_version
            version_allhtml = "data/releases/%s/schema-all.html" % requested_version
            version_nt = "data/releases/%s/schema.nt" % requested_version
            if requested_format=="":
                return self.redirectToBase("/version/%s/schema-all.html" % requested_version)

            if requested_format=="schema.rdfa":
                return self.redirectToBase("/version/%s/schema.rdfa" % requested_version)

            if requested_format=="schema.nt":
                return self.redirectToBase("/version/%s/schema.nt" % requested_version)

            if requested_format != "":
                return False # Turtle, csv etc.

        else:
            log.info("Unreleased version requested. We only understand requests for latest if unreleased.")

            if requested_version != "build-latest":
                return False
                log.info("giving up to 404.")
            else:  # build-latest
                requested_version = SCHEMA_VERSION
                log.info("generating a live view of this latest release (with SCHEMA_VERSION set as: %s)." % SCHEMA_VERSION)


        if getPageFromStore('FullReleasePage.html'):
            self.response.out.write( getPageFromStore('FullReleasePage.html') )
            log.debug("Serving recycled FullReleasePage.")
            return True
        else:
            mainroot = TypeHierarchyTree()
            mainroot.traverseForHTML(VTerm.getTerm("Thing"), hashorslash="#term_", layers=layerlist)
            thing_tree = mainroot.toHTML()
            base_href = "/version/%s/" % requested_version

            az_types = GetAllTypes()
            az_types.sort()
            az_type_meta = {}

            az_props = GetAllProperties()
            az_props.sort()
            az_prop_meta = {}

            # TYPES
            for t in az_types:
                props4type = HTMLOutput() # properties applicable for a type
                props2type = HTMLOutput() # properties that go into a type

                self.emitSimplePropertiesPerType(t, out=props4type, hashorslash="#term_" )
                self.emitSimplePropertiesIntoType(t, out=props2type, hashorslash="#term_" )

                tcmt = Markup(VTerm.getTerm(t).getComment())
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

                cmt = Markup(VTerm.getTerm(pt).getComment())
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

            page = templateRender('fullReleasePage.tpl', node,
                    {"base_href": base_href,
                    'thing_tree': thing_tree,
                    'liveversion': SCHEMA_VERSION,
                    'requested_version': requested_version,
                    'releasedate': releasedate,
                    'az_props': az_props, 'az_types': az_types,
                    'az_prop_meta': az_prop_meta, 'az_type_meta': az_type_meta,
                    'menu_sel': "Documentation",
                    'suppressDevnote': True})

            self.response.out.write( page )
            log.debug("Serving fresh FullReleasePage.")
            PageStore.put("FullReleasePage.html",page)
            return True

    def handleExtensionContents(self,ext):
        if not ext in ENABLED_EXTENSIONS:
            return ""

#        if getPageFromStore('ExtensionContents',ext):
#            return getPageFromStore('ExtensionContents',ext)

        buff = StringIO.StringIO()

        az_terms = VTerm.getAllTerms(layer=ext) #Returns sorted by id results.
        az_terms.sort(key = lambda u: u.category)

        if len(az_terms) > 0:
            buff.write("<br/><div style=\"text-align: left; margin: 2em\"><h3>Terms defined in the '%s' section.</h3>" % ext)

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
#        PageStore.put('ExtensionContents',ret,ext)
        buff.close()
        return ret

    def countTypes(self,interms,select="",layers='core'):
        ret = 0
        for t in interms:
            if select == "type" and t.isClass():
                ret += 1
            elif select == "prop" and t.isProperty():
                ret += 1
            elif select == "enum" and t.isEnumerationValue():
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
                    use = t.isClass()
                elif select == "prop":
                    use = t.isProperty()
                elif select == "enum":
                    use = t.isEnumerationValue()
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
        global noindexpages
        node = str(node)
        hostString = test
        host_ext = ""
        args = []
        if test == "":
            hostString = self.request.host
            args = self.request.arguments()

        ver=None
        if not getInTestHarness():
            from google.appengine.api.modules.modules import get_current_version_name
            ver = get_current_version_name()
        if hostString.startswith("%s." % ver):
            log.info("Removing version prefix '%s' from hoststring" % ver)
            hostString = hostString[len(ver) + 1:]

        scheme = "http" #Defalt for tests
        if not getInTestHarness():  #Get the actual scheme from the request
            scheme = self.request.scheme
        setHttpScheme(scheme)

        match = re.match( r'([\w\-_]+)[\.:]?', hostString)
        host_ext = str(match.group(1))
        match0 = str(match.group(0))
        if host_ext + ":" == match0: #Special case for URLs with no subdomains - eg. localhost
            host_ext = ""

        split = hostString.rsplit(':')
        myhost = split[0]
        mybasehost = myhost
        myport = "80"
        if len(split) > 1:
            myport = split[1]
        setHostPort(myport)


        log.info("setupHostinfo: data: scheme='%s' hoststring='%s' initial host_ext='%s'" % (scheme, hostString, str(host_ext) ))

        ver=None
        if not getInTestHarness():
            from google.appengine.api.modules.modules import get_current_version_name
            ver = get_current_version_name()

        if host_ext != "":
            if host_ext in ENABLED_EXTENSIONS:
                mybasehost = mybasehost[len(host_ext) + 1:]

            elif host_ext == "www":
                mybasehost = mybasehost[4:]
                setBaseHost(mybasehost)
                log.info("Host extention '%s' - redirecting to '%s'" % (host_ext,mybasehost))
                return self.redirectToBase(node,True)
            else:
                tempbase = mybasehost[len(host_ext)+1:]
                if tempbase in WORKINGHOSTS: #Known hosts so can control extention values
                    mybasehost = tempbase
                    setHostExt("")
                    setBaseHost(mybasehost)
                    log.info("Host extention '%s' not enabled - redirecting to '%s'" % (host_ext,mybasehost))
                    return self.redirectToBase(node,True)

                else:                        #Unknown host so host_ext may be just part of the host string
                    host_ext = ""

        log.info("setupHostinfo: calculated: basehost='%s' host_ext='%s'" % (mybasehost, host_ext ))

        setHostExt(host_ext)
        setBaseHost(mybasehost)

        if mybasehost == "schema.org":
            noindexpages = False
        if "FORCEINDEXPAGES" in os.environ:
            if os.environ["FORCEINDEXPAGES"] == "True":
                noindexpages = False
        log.info("[%s] noindexpages: %s" % (getInstanceId(short=True),noindexpages))

        setHostExt(host_ext)
        setBaseHost(mybasehost)
        setHostPort(myport)
        setArguments(args)

        dcn = host_ext
        if dcn == None or dcn == "" or dcn =="core":
            dcn = "core"
        if scheme != "http":
            dcn = "%s-%s" % (dcn,scheme)

        dcn = "single" #Forcing single cache
        #log.info("Forcing single cache.  !!!!!!!!!!!!!!!!")
        #log.info("sdoapp.py setting current datacache to: %s " % dcn)
        DataCache.setCurrent(dcn)
        PageStore.setCurrent(dcn)
        HeaderStore.setCurrent(dcn)

        debugging = False
        if "localhost" in hostString or "sdo-phobos.appspot.com" in hostString or FORCEDEBUGGING:
            debugging = True
        setAppVar('debugging',debugging)

        return True

    def redirectToBase(self,node="",full=False):
        uri = makeUrl("",node,full)
        log.info("Redirecting [301] to: %s" % uri)
        if not getInTestHarness():
            self.response = webapp2.redirect(uri, True, 301)
        return False

    def redirectToExt(self,node="",ext="",full=False):
        uri = makeUrl(ext,node,full)
        log.info("Redirecting [301] to: %s" % uri)
        if not getInTestHarness():
            self.response = webapp2.redirect(uri, True, 301)
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
        log.info("NODE: '%s'" % node)

        if not node or node == "":
            node = "/"

        if not validNode_re.search(str(node)) or os.path.basename(str(node)).count('.') > 2: #invalid node name
            log.warning("Invalid node name '%s'" % str(node))
            self.handle404Failure(node,suggest=False)
            return

        NotModified = False
        matchTag = self.request.headers.get("If-None-Match",None)
        unMod = self.request.headers.get("If-Unmodified-Since",None)

        #log.info("matchTag '%s' unMod '%s'" % (matchTag,unMod))

        hdrIndex = getHostExt()
        if len(hdrIndex):
            hdrIndex +=  ":"
        hdrIndex += node

        hdrs = HeaderStore.get(hdrIndex)
        mod = None

        if hdrs:
            etag = hdrs.get("ETag",None)
            mod = hdrs.get("Last-Modified",None)
            log.info("stored etag '%s' mod '%s'" % (etag,mod))

            if matchTag == etag:
                NotModified = True
            elif unMod:
                unModt = datetime.datetime.strptime(unMod,"%a, %d %b %Y %H:%M:%S %Z")
                modt = datetime.datetime.strptime(mod,"%a, %d %b %Y %H:%M:%S %Z")
                if modt <= unModt:
                    log.info("Last mod '%s' not modified since '%s' " % (mod,unMod))
                    NotModified = True

        if hdrs and "_pageFlush" in getArguments():
            log.info("Reloading header for %s" % hdrIndex)
            HeaderStore.remove(hdrIndex)
            hdrs = None
            NotModified = False

        if NotModified:
            self.response.clear()
            self.response.headers = hdrs
            self.response.set_status(304,"Not Modified")
        else:
            enableCaching = self._get(node) #Go get the page

            if enableCaching:
                if self.response.status.startswith("200"):
                    stat = getAppVar(CLOUDSTAT)
                    log.info("CLOUDSTAT %s" % stat)
                    if stat: #Use values from cloud storage
                        self.response.headers.add_header("ETag", stat.etag)
                        self.response.headers['Last-Modified'] = time.strftime("%a, %d %b %Y %H:%M:%S GMT",time.gmtime(stat.st_ctime))
                        self.response.headers['Content-Type'] = stat.content_type
                    else:
                        if not self.response.headers.get('Content-Type',None):
                            mimetype, contentType = mimetypes.guess_type(node)
                            self.response.headers['Content-Type'] = mimetype

                        self.response.headers.add_header("ETag", getslug() + str(hash(hdrIndex)))
                        self.response.headers['Last-Modified'] = getmodiftime().strftime("%a, %d %b %Y %H:%M:%S GMT")

                    store = True
                    if mod: #Previous hdrs cached for this node
                        new = self.response.headers.get('Last-Modified',None)
                        if new and new == mod: #previous cached hdrs has same time as new one
                            store = False #No point storing it again

                    if store:
                        retHdrs = self.response.headers.copy()
                        try:
                            HeaderStore.put(hdrIndex,retHdrs) #Cache these headers for a future 304 return
                        except Exception  as e:
                            log.warning("HeaderStore.put(%s) returned exception: %s" % (hdrIndex,e))
                            log.info("Abandoning caching of response headers for '%s'" % node)
                            pass

            #self.response.set_cookie('GOOGAPPUID', getAppEngineVersion())
        log.info("Responding:\n%s\nstatus: %s\n%s" % (node,self.response.status,self.response.headers ))


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

        log.info("[%s] _get(%s)" % (getInstanceId(short=True),node))

        self.callCount()

        if (node in silent_skip_list):
            return False

        if ENABLE_HOSTED_EXTENSIONS:
            layerlist = self.setupExtensionLayerlist(node) # e.g. ['core', 'bib']
        else:
            layerlist = ["core"]

        setSiteName(self.getExtendedSiteName(layerlist)) # e.g. 'bib.schema.org', 'schema.org'
        log.debug("EXT: set sitename to %s " % getSiteName())

        if not LOADEDSOURCES:
            log.info("Instance[%s] received request for not stored page: %s" % (getInstanceId(short=True), node) )
            log.info("Instance[%s] needs to load sources to create it" % (getInstanceId(short=True)) )
            load_sources() #Get Examples files and schema definitions

        self.emitHTTPHeaders(node) #Ensure we have the right basic header values

        if node.startswith("docs/"):
            return self._getDocs(node,layerlist=layerlist)

        if(node == "_ah/warmup"):
            if "localhost" in os.environ['SERVER_NAME'] and WarmupState.lower() == "auto":
                log.info("[%s] Warmup dissabled for localhost instance" % getInstanceId(short=True))
                if DISABLE_NDB_FOR_LOCALHOST:
                    log.info("[%s] NDB dissabled for localhost instance" % getInstanceId(short=True))
                    enablePageStore("INMEM")
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

        if(node == "admin/refresh"):
            log.info("Processing refesh request")
            load_start = datetime.datetime.now()
            memcache.flush_all()
            memcache.set(key="app_initialising", value=True, time=300)  #Give the system 5 mins - auto remove flag in case of crash
            cleanmsg = CacheControl.clean()
            log.info("Clean count(s): %s" % cleanmsg)
            log.info(("[%s] Cache clean took %s " % (getInstanceId(short=True),(datetime.datetime.now() - load_start))))
            memcache.set(key="app_initialising", value=False)
            storeInitialisedTimestamp()
            self.emitSchemaorgHeaders("Refresh")
            #404 could be called from any path, so output all potential locations of schemaorg.css
            self.response.out.write('<link rel="stylesheet" type="text/css" href="../docs/schemaorg.css" />')
            self.response.out.write('<link rel="stylesheet" type="text/css" href="docs/schemaorg.css" />')
            self.response.out.write('<link rel="stylesheet" type="text/css" href="/docs/schemaorg.css" />')

            self.response.out.write('<h3>Refresh Completed</h3><p>Took: %s</p>' % (datetime.datetime.now() - load_start))
            return False


        if(node == "_ah/start"):
            log.info("Instance[%s] received Start request at %s" % (modules.get_current_instance_id(), global_vars.time_start) )
            if "localhost" in os.environ['SERVER_NAME'] and WarmupState.lower() == "auto":
                log.info("[%s] Warmup dissabled for localhost instance" % getInstanceId(short=True))
                if DISABLE_NDB_FOR_LOCALHOST:
                    log.info("[%s] NDB dissabled for localhost instance" % getInstanceId(short=True))
                    enablePageStore("INMEM")
            else:
                if not memcache.get("warmedup"):
                    memcache.set("warmedup", value=True)
                    self.warmup()
                else:
                    log.info("Warmup already actioned")
            return False

        if(node == "_ah/stop"):
            log.info("Instance[%s] received Stop request at %s" % (modules.get_current_instance_id(), global_vars.time_start) )
            log.info("Flushing memcache")
            memcache.flush_all()
            return False

        if (node in ["", "/"]):
            return self.handleHomepage(node)

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

    def _getDocs(self, node, layerlist=""):
        hstext = getHostExt()
        if hstext == "":
            hstext = "core"

        if (node.startswith("docs/") and hstext != "core"): #All docs should operate in core
            return self.redirectToBase(node,True)

        if node in ["docs/jsonldcontext.json.txt", "docs/jsonldcontext.json", "docs/jsonldcontext.jsonld"]:
            if self.handleJSONContext(node):
                return True
            else:
                log.info("Error handling JSON-LD context: %s" % node)
                return False

        elif (node == "docs/full.html"):
            if self.handleFullHierarchyPage(node, layerlist=layerlist):
                return True
            else:
                log.info("Error handling full.html : %s " % node)
                return False

        elif (node == "docs/schemas.html"):
            if self.handleSchemasPage(node, layerlist=layerlist):
                return True
            else:
                log.info("Error handling schemas.html : %s " % node)
                return False
        elif (node == "docs/developers.html"):
            if self.handleDumpsPage(node, layerlist=layerlist):
                return True
            else:
                log.info("Error handling developers.html : %s " % node)
                return False

        elif (node == "docs/tree.jsonld" or node == "docs/tree.json"):
            if self.handleJSONSchemaTree(node, layerlist=ALL_LAYERS):
                return True
            else:
                log.info("Error handling JSON-LD schema tree: %s " % node)
                return False
        else: #Asking for a sttic file under docs
            return self.handleStaticDoc(node)

    def handleStaticDoc(self,node):
        if PAGESTOREMODE == "CLOUDSTORE":
            log.info("Asking for: %s" % node)
            page = getPageFromStore(node,enableFlush=False)
            if page:
                self.response.out.write( page )
                log.debug("Serving static page: %s" % node)
                return True
            else:
                self.handle404Failure(node)
                return False


        return False

    def siteDebug(self):
        global STATS
        page = templateRender('siteDebug.tpl', "_siteDebug" )

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
        self.response.out.write("</div>\n</body>\n<!--AppEngineVersion %s -->\n</html>\n"  % getAppEngineVersion())

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
        if memcache.get("Warming"):
            log.debug("Instance[%s] detected system already warming" % (modules.get_current_instance_id()) )
        else:
            memcache.set("Warming",True,time=300)
            Warmer.warmAll(self)
            log.debug("Instance[%s] completed Warmup request at %s elapsed: %s" % (modules.get_current_instance_id(), datetime.datetime.utcnow(),datetime.datetime.now() - warm_start ) )
            memcache.set("Warming",False)

class WarmupTool():

    def __init__(self):
        #self.pageList = ["docs/schemas.html"]
        self.pageList = ["/","docs/schemas.html","docs/full.html","docs/tree.jsonld","docs/developers.html","docs/jsonldcontext.json"]
        self.extPageList = ["/"] #Pages warmed in all extentions
        self.warmPages = {}
        for l in ALL_LAYERS:
            self.warmPages[l] = []
        self.warmedLayers = []

    def stepWarm(self, unit=None, layer=None):
        lock = threading.Lock()
        with lock:
            realHostExt = getHostExt()
            if layer:
                setHostExt(layer)

            self._stepWarm(unit=unit, layer=layer)

            setHostExt(realHostExt)


    def _stepWarm(self, unit=None, layer=None):
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
                self.warmPages[layer].append(p)
                if layer == "core" or p in self.extPageList: #Only warm selected pages in extensions
                    log.info("Warming page %s in layer %s" % (p,layer))
                    unit._get(p,doWarm=False)
                    unit.response.clear()
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

def getExtenstionDescriptions():
    extDisambiguatingDescription = ""
    extComment = ""
    extlinktext = ""
    extVers = ""
    extName = ""
    extDD = ""
    ex = getHostExt()
    if ex and len(ex):
        descs = api.SdoConfig.descriptor(ex)
        if descs and len(descs):
            extName = descs[0].get("name")
            extDD = Markdown.parse(descs[0].get("brief"))
            extVers = Markdown.parse(descs[0].get("version"))
            extlinktext = Markdown.parse(descs[0].get("linktext"))
            extComment = Markdown.parse(descs[0].get("comment"))
            extDisambiguatingDescription = Markdown.parse(descs[0].get("extDisambiguatingDescription"))

    return extName, extDD, extVers, extlinktext, extComment, extDisambiguatingDescription

def templateRender(templateName, node, values=None):
    global sitemode #,sitename
    #log.info("templateRender(%s,%s,%s)" % (templateName, node, values))
    #log.info("getHostExt %s" % getHostExt())


    if isinstance(node, Unit):
        node = node.id
    if isinstance(node, VTerm):
        node = node.getId()

    extName, extDD, extVers, extlinktext, extComment, extDisambiguatingDescription =  getExtenstionDescriptions()

    if node.startswith("docs/"):
        docsdir = "./"
        homedir = ".."
    elif node.startswith("version/"):
        docsdir = "/docs/"
        homedir = ""
    else:
        docsdir = "docs/"
        homedir = "."
    defvars = {
        'ENABLE_HOSTED_EXTENSIONS': ENABLE_HOSTED_EXTENSIONS,
        'SCHEMA_VERSION': SCHEMA_VERSION,
        'appengineVersion': getAppEngineVersion(),
        'developVersion': DEVELOPVERSION,
        'suppressDevnote': False,
        'debugging': getAppVar('debugging'),
        'docsdir': docsdir,
        'extlinktext': extlinktext,
        'extDisambiguatingDescription':extDisambiguatingDescription,
        'extComment': extComment,
        'extDD': extDD,
        'extName': extName,
        'extVers': extVers,
        'extensionPath': makeUrl(getHostExt(),"",full=True),
        'homedir': homedir,
        'host_ext': getHostExt(),
        'mybasehost': getBaseHost(),
        'myhost': getHost(),
        'myport': getHostPort(),
        'sitemode': sitemode,
        'sitename': SdoConfig.getname(),
        'staticPath': homedir,
        'targethost': makeUrl("","",full=True),
        'vocabUri': SdoConfig.vocabUri()
    }

    if values:
        defvars.update(values)
    template = JINJA_ENVIRONMENT.get_template(templateName)
    return template.render(defvars)

def oldtemplateRender(templateName, node, values=None):
    global sitemode #,sitename
    log.info("templateRender(%s,%s,%s)" % (templateName, node, values))
    log.info("getHostExt %s" % getHostExt())


    if isinstance(node, Unit):
        node = node.id

    extDef = Unit.GetUnit(getNss(getHostExt()),True)
    extComment = ""
    extVers = ""
    extName = ""
    #log.info("EXDEF '%s'" % extDef)
    if extDef:
        extComment = GetComment(extDef,ALL_LAYERS)
        if extComment == "-":
            extComment = ""
        extDDs = GetTargets(Unit.GetUnit("schema:disambiguatingDescription", True), extDef, layers=ALL_LAYERS )
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
        nms = GetTargets(Unit.GetUnit("schema:name", True), extDef, layers=ALL_LAYERS )
        if len(nms) > 0:
            extName = nms[0]
    if node.startswith("docs/"):
        docsdir = "./"
        homedir = ".."
    else:
        docsdir = "docs/"
        homedir = "."
    defvars = {
        'ENABLE_HOSTED_EXTENSIONS': ENABLE_HOSTED_EXTENSIONS,
        'SCHEMA_VERSION': SCHEMA_VERSION,
        'SUBDOMAINS': SUBDOMAINS,
        'sitemode': sitemode,
        'sitename': SdoConfig.getname(),
        'staticPath': homedir,
        'extensionPath': makeUrl(getHostExt(),"",full=True),
        'myhost': getHost(),
        'myport': getHostPort(),
        'mybasehost': getBaseHost(),
        'host_ext': getHostExt(),
        'extComment': extComment,
        'docsdir': docsdir,
        'homedir': homedir,
        'extDD': extDD,
        'extVers': extVers,
        'extName': extName,
        'targethost': makeUrl("","",full=True),
        'debugging': getAppVar('debugging'),
        'appengineVersion': getAppEngineVersion()
    }

    if values:
        defvars.update(values)
    template = JINJA_ENVIRONMENT.get_template(templateName)
    return template.render(defvars)


def my_shutdown_hook():
    global instance_num
    if SHAREDSITEDEBUG:
        Insts = memcache.get("ExitInstances")
        if Insts:
            Insts[os.environ["INSTANCE_ID"]] = 1
            memcache.replace("ExitInstances",Insts)

        memcache.add("Exits",0)
        memcache.incr("Exits")
    log.info("Instance[%s] shutting down" % modules.get_current_instance_id())

runtime.set_shutdown_hook(my_shutdown_hook)

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

def makeUrl(ext="",path="",full=False,scheme=None):
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

        if full:
            if not scheme:
                scheme = getHttpScheme()

            targethost = os.environ.get("TARGETSITE",getBaseHost())

            url = "%s://%s%s%s%s" % (scheme,sub,targethost,port,p)
        else:
            url = "%s" % (p)
        return url

def getPageFromStore(id,ext=None,enableFlush=True):
        cached = PageStore.get(id,ext)
        if enableFlush and cached and "_pageFlush" in getArguments():
            log.info("Reloading page for %s" % id)
            PageStore.remove(id,ext)
            cached = None
        return cached

schemasInitialized = False
def load_schema_definitions(refresh=False):
    global schemasInitialized
    if not schemasInitialized or refresh:
        log.info("STARTING UP... reading schemas.")
        #load_graph(loadExtensions=ENABLE_HOSTED_EXTENSIONS)
        if SdoConfig.isValid():
           read_schemas(SdoConfig.termFiles())
           load_usage_data(SdoConfig.countsFiles())
        else:
            read_local_schemas(loadExtensions=ENABLE_HOSTED_EXTENSIONS)
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
        load_schema_definitions()
        log.info(("[%s] Term definitions load took %s " % (getInstanceId(short=True),(datetime.datetime.now() - load_start))))
        load_start = datetime.datetime.now()
        load_examples_data(ENABLED_EXTENSIONS)
        log.info(("[%s] Examples load took %s " % (getInstanceId(short=True),(datetime.datetime.now() - load_start))))
        LOADEDSOURCES=True
        LOADINGSOURCE=None

if getInTestHarness():
    load_sources()
else:
    app = ndb.toplevel(webapp2.WSGIApplication([("/(.*)", ShowUnit)]))
