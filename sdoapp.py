#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import re
import webapp2
import jinja2
import logging
import StringIO
import json

from markupsafe import Markup, escape # https://pypi.python.org/pypi/MarkupSafe

import parsers


from google.appengine.ext import ndb
from google.appengine.ext import blobstore
from google.appengine.api import users
from google.appengine.ext.webapp import blobstore_handlers

from api import inLayer, read_file, full_path, read_schemas, read_extensions, read_examples, namespaces, DataCache
from api import Unit, GetTargets, GetSources
from api import GetComment, all_terms, GetAllTypes, GetAllProperties, GetAllEnumerationValues
from api import GetParentList, GetImmediateSubtypes, HasMultipleBaseTypes
from api import GetJsonLdContext, ShortenOnSentence, StripHtmlTags

logging.basicConfig(level=logging.INFO) # dev_appserver.py --log_level debug .
log = logging.getLogger(__name__)

SCHEMA_VERSION=2.2

FEEDBACK_FORM_BASE_URL='https://docs.google.com/a/google.com/forms/d/1krxHlWJAO3JgvHRZV9Rugkr9VYnMdrI10xbGsWt733c/viewform?entry.1174568178&entry.41124795={0}&entry.882602760={1}'
# {0}: term URL, {1} category of term.

sitemode = "mainsite" # whitespaced list for CSS tags,
            # e.g. "mainsite testsite" when off expected domains
            # "extensionsite" when in an extension (e.g. blue?)

releaselog = { "2.0": "2015-05-13", "2.1": "2015-08-06", "2.2": "2015-11-05" }
#

silent_skip_list =  [ "favicon.ico" ] # Do nothing for now

all_layers = {}
ext_re = re.compile(r'([^\w,])+')
PageCache = {}

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

INTESTHARNESS = False #Used to indicate we are being called from tests - use setInTestHarness() & getInTestHarness() to manage value

EXTENSION_SUFFIX = "" # e.g. "*"

#ENABLED_EXTENSIONS = [ 'admin', 'auto', 'bib' ]
ENABLED_EXTENSIONS = [ 'auto', 'bib' ]
ALL_LAYERS = [ 'core', 'auto', 'bib' ]


FORCEDEBUGGING = False
# FORCEDEBUGGING = True

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

    def traverseForHTML(self, node, depth = 1, hashorslash="/", layers='core', buff=None):

        """Generate a hierarchical tree view of the types. hashorslash is used for relative link prefixing."""

        log.debug("traverseForHTML: node=%s hashorslash=%s" % ( node.id, hashorslash ))
        localBuff = False
        if buff == None:
            localBuff = True
            buff = StringIO.StringIO()

        urlprefix = ""
        home = node.getHomeLayer()
        gotOutput = False
        if home in layers:
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
                    got = self.traverseForHTML(item, depth + 1, hashorslash=hashorslash, layers=layers, buff=subBuff)
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
    return node.examples

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

#    def __init__(self):
#        self.outputStrings = []

    def emitCacheHeaders(self):
        """Send cache-related headers via HTTP."""
        self.response.headers['Cache-Control'] = "public, max-age=43200" # 12h
        self.response.headers['Vary'] = "Accept, Accept-Encoding"

    def GetCachedText(self, node, layers='core'):
        """Return page text from node.id cache (if found, otherwise None)."""
        global PageCache
        cachekey = "%s:%s" % ( layers, node.id ) # was node.id
        if (cachekey in PageCache):
            return PageCache[cachekey]
        else:
            return None

    def AddCachedText(self, node, textStrings, layers='core'):
        """Cache text of our page for this node via its node.id.

        We can be passed a text string or an array of text strings.
        """
        global PageCache
        cachekey = "%s:%s" % ( layers, node.id ) # was node.id
        outputText = "".join(textStrings)
        log.debug("CACHING: %s" % node.id)
        PageCache[cachekey] = outputText
        return outputText

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
            sc = Unit.GetUnit("typeOf")
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
        if(node.id == "DataType"):  #Special case
            return "<a href=\"%s\">%s</a>" % (node.id, node.id)

        if label=='':
          label = node.id
        if title != '':
          title = " title=\"%s\"" % (title)
        if prop:
            prop = " property=\"%s\"" % (prop)
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
            extclass = "class=\"ext ext-%s\" " % home
            extflag = EXTENSION_SUFFIX
            tooltip = "title=\"Extended schema: %s.schema.org\" " % home

        rdfalink = ''
        if prop:
            rdfalink = '<link %s href="http://schema.org/%s" />' % (prop,label)


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
        self.write("<h1 class=\"page-title\">\n")
        self.write(node.id)
        self.write("</h1>")
        home = node.home
        if home != "core" and home != "":
            self.write("Defined in the %s.schema.org extension." % home)
            self.write(" (This is an initial exploratory release.)<br/>")
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

        enuma = node.isEnumerationValue(layers=layers)

        crumbsout = []
        for row in range(len(self.crumbStacks)):
           thisrow = ""
           if(":" in self.crumbStacks[row][len(self.crumbStacks[row])-1].id):
                continue
           count = 0
           while(len(self.crumbStacks[row]) > 0):
                n = self.crumbStacks[row].pop()
                if(count > 0):
                    if((len(self.crumbStacks[row]) == 0) and enuma):
                        thisrow += " :: "
                    else:
                        thisrow += " &gt; "
                elif n.id == "Class": # If Class is first breadcrum suppress it
                        continue
                count += 1
                thisrow += "%s" % (self.ml(n))
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
            subs = GetTargets(Unit.GetUnit("typeOf"), node, layers=layers)
            subs += GetTargets(Unit.GetUnit("rdfs:subClassOf"), node, layers=layers)
        elif node.isClass(layers=layers):
            subs = GetTargets(Unit.GetUnit("rdfs:subClassOf"), node, layers=layers)
        elif(node.isAttribute(layers=layers)):
            subs = GetTargets(Unit.GetUnit("rdfs:subPropertyOf"), node, layers=layers)
        else:
            subs = GetTargets(Unit.GetUnit("typeOf"), node, layers=layers)# Enumerations are classes that have no declared subclasses

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
            supersedes = prop.supersedes(layers=layers)
            olderprops = prop.supersedes_all(layers=layers)
            inverseprop = prop.inverseproperty(layers=layers)
            subprops = prop.subproperties(layers=layers)
            superprops = prop.superproperties(layers=layers)
            ranges = GetTargets(ri, prop, layers=layers)
            comment = GetComment(prop, layers=layers)
            if (not headerPrinted):
                class_head = self.ml(cl)
                if subclass:
                    class_head = self.ml(cl, prop="rdfs:subClassOf")
                out.write("<tr class=\"supertype\">\n     <th class=\"supertype-name\" colspan=\"3\">Properties from %s</th>\n  \n</tr>\n\n<tbody class=\"supertype\">\n  " % (class_head))
                headerPrinted = True

            out.write("<tr typeof=\"rdfs:Property\" resource=\"http://schema.org/%s\">\n    \n      <th class=\"prop-nam\" scope=\"row\">\n\n<code property=\"rdfs:label\">%s</code>\n    </th>\n " % (prop.id, self.ml(prop)))
            out.write("<td class=\"prop-ect\">\n")
            first_range = True
            for r in ranges:
                if (not first_range):
                    out.write(" or <br/> ")
                first_range = False
                out.write(self.ml(r, prop='rangeIncludes'))
                out.write("&nbsp;")
            out.write("</td>")
            out.write("<td class=\"prop-desc\" property=\"rdfs:comment\">%s" % (comment))
            if (len(olderprops) > 0):
                olderlinks = ", ".join([self.ml(o) for o in olderprops])
                out.write(" Supersedes %s." % olderlinks )
            if (inverseprop != None):
                out.write("<br/> Inverse property: %s." % (self.ml(inverseprop)))

            out.write("</td></tr>")
            subclass = False
            propcount += 1

        if subclass: # in case the superclass has no defined attributes
            out.write("<tr><td colspan=\"3\"><meta property=\"rdfs:subClassOf\" content=\"%s\"></td></tr>" % (cl.id))

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

        first = True
        count = 0
        for prop in sorted(GetSources(di, cl, ALL_LAYERS), key=lambda u: u.id):
            if (prop.superseded(layers=layers)):
                continue
            if inLayer(layers,prop):
                continue
            log.debug("ClassExtensionfFound %s " % (prop))

            sep = ", "
            if first:
                out.write("<li>From %s: " % cl)
                sep = ""
                first = False

            out.write("%s%s" % (sep,self.ml(prop)))
            count += 1
        if(count > 0):
            out.write("</li>\n")


    def emitClassIncomingProperties (self, cl, layers="core", out=None, hashorslash="/"):
        """Write out a table of incoming properties for a per-type page."""
        if not out:
            out = self

        headerPrinted = False
        di = Unit.GetUnit("domainIncludes")
        ri = Unit.GetUnit("rangeIncludes")
        for prop in sorted(GetSources(ri, cl, layers=layers), key=lambda u: u.id):
            if (prop.superseded(layers=layers)):
                continue
            supersedes = prop.supersedes(layers=layers)
            inverseprop = prop.inverseproperty(layers=layers)
            subprops = prop.subproperties(layers=layers)
            superprops = prop.superproperties(layers=layers)
            ranges = GetTargets(di, prop, layers=layers)
            comment = GetComment(prop, layers=layers)

            if (not headerPrinted):
                self.write("<br/><br/>Instances of %s may appear as values for the following properties<br/>" % (self.ml(cl)))
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

        di = Unit.GetUnit("domainIncludes")
        ri = Unit.GetUnit("rangeIncludes")
        ranges = sorted(GetTargets(ri, node, layers=layers), key=lambda u: u.id)
        domains = sorted(GetTargets(di, node, layers=layers), key=lambda u: u.id)
        first_range = True

        newerprop = node.supersededBy(layers=layers) # None of one. e.g. we're on 'seller'(new) page, we get 'vendor'(old)
        olderprop = node.supersedes(layers=layers) # None or one
        olderprops = node.supersedes_all(layers=layers) # list, e.g. 'seller' has 'vendor', 'merchant'.

        inverseprop = node.inverseproperty(layers=layers)
        subprops = node.subproperties(layers=layers)
        superprops = node.superproperties(layers=layers)


        if (inverseprop != None):
            tt = "This means the same thing, but with the relationship direction reversed."
            out.write("<p>Inverse-property: %s.</p>" % (self.ml(inverseprop, inverseprop.id,tt, prop=False, hashorslash=hashorslash)) )

        out.write("<table class=\"definition-table\">\n")
        out.write("<thead>\n  <tr>\n    <th>Values expected to be one of these types</th>\n  </tr>\n</thead>\n\n  <tr>\n    <td>\n      ")

        for r in ranges:
            if (not first_range):
                out.write("<br/>")
            first_range = False
            tt = "The '%s' property has values that include instances of the '%s' type." % (node.id, r.id)
            out.write(" <code>%s</code> " % (self.ml(r, r.id, tt, prop="rangeIncludes", hashorslash=hashorslash) +"\n"))
        out.write("    </td>\n  </tr>\n</table>\n\n")
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

        if (subprops != None and len(subprops) > 0):
            out.write("<table class=\"definition-table\">\n")
            out.write("  <thead>\n    <tr>\n      <th>Sub-properties</th>\n    </tr>\n</thead>\n")
            for sbp in subprops:
                c = ShortenOnSentence(StripHtmlTags( GetComment(sbp,layers=layers) ),60)
                tt = "%s: ''%s''" % ( sbp.id, c)
                out.write("\n    <tr><td><code>%s</code></td></tr>\n" % (self.ml(sbp, sbp.id, tt, hashorslash=hashorslash)))
            out.write("\n</table>\n\n")

        # Super-properties
        if (superprops != None and  len(superprops) > 0):
            out.write("<table class=\"definition-table\">\n")
            out.write("  <thead>\n    <tr>\n      <th>Super-properties</th>\n    </tr>\n</thead>\n")
            for spp in superprops:
                c = ShortenOnSentence(StripHtmlTags( GetComment(spp,layers=layers) ),60)
                c = re.sub(r'<[^>]*>', '', c) # This is not a sanitizer, we trust our input.
                tt = "%s: ''%s''" % ( spp.id, c)
                out.write("\n    <tr><td><code>%s</code></td></tr>\n" % (self.ml(spp, spp.id, tt,hashorslash)))
            out.write("\n</table>\n\n")

        # Supersedes
        if (olderprops != None and len(olderprops) > 0):
            out.write("<table class=\"definition-table\">\n")
            out.write("  <thead>\n    <tr>\n      <th>Supersedes</th>\n    </tr>\n</thead>\n")

            for o in olderprops:
                c = GetComment(o, layers=layers)
                tt = "%s: ''%s''" % ( o.id, c)
                out.write("\n    <tr><td><code>%s</code></td></tr>\n" % (self.ml(o, o.id, tt, hashorslash)))
            out.write("\n</table>\n\n")

        # supersededBy (at most one direct successor)
        if (newerprop != None):
            out.write("<table class=\"definition-table\">\n")
            out.write("  <thead>\n    <tr>\n      <th><a href=\"/supersededBy\">supersededBy</a></th>\n    </tr>\n</thead>\n")
            tt="supersededBy: %s" % newerprop.id
            out.write("\n    <tr><td><code>%s</code></td></tr>\n" % (self.ml(newerprop, newerprop.id, tt,hashorslash)))
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
        accept_header = self.request.headers.get('Accept').split(',')
        logging.info("accepts: %s" % self.request.headers.get('Accept'))

        if ENABLE_JSONLD_CONTEXT:
            jsonldcontext = GetJsonLdContext(layers=ALL_LAYERS)

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
            self.response.headers['Content-Type'] = "application/ld+json"
            self.emitCacheHeaders()
            self.response.out.write( jsonldcontext )
            return True
        else:
            # Serve a homepage from template
            # the .tpl has responsibility for extension homepages
            # TODO: pass in extension, base_domain etc.
            sitekeyedhomepage = "homepage %s" % getSiteName()
            hp = DataCache.get(sitekeyedhomepage)
            if hp != None:
                self.response.out.write( hp )
                #log.info("Served datacache homepage.tpl key: %s" % sitekeyedhomepage)
                log.debug("Served datacache homepage.tpl key: %s" % sitekeyedhomepage)
            else:

                template = JINJA_ENVIRONMENT.get_template('homepage.tpl')
                template_values = {
                    'ENABLE_HOSTED_EXTENSIONS': ENABLE_HOSTED_EXTENSIONS,
                    'SCHEMA_VERSION': SCHEMA_VERSION,
                    'sitename': getSiteName(),
                    'staticPath': makeUrl("",""),
                    'myhost': getHost(),
                    'myport': getHostPort(),
                    'mybasehost': getBaseHost(),
                    'host_ext': getHostExt(),
                    'ext_contents': self.handleExtensionContents(getHostExt()),
                    'home_page': "True",
                    'debugging': getAppVar('debugging')
                }

                # We don't want JINJA2 doing any cachine of included sub-templates.

                page = template.render(template_values)
                self.response.out.write( page )
                log.debug("Served and cached fresh homepage.tpl key: %s " % sitekeyedhomepage)
                #log.info("Served and cached fresh homepage.tpl key: %s " % sitekeyedhomepage)
                DataCache.put(sitekeyedhomepage, page)
                #            self.response.out.write( open("static/index.html", 'r').read() )
            return True
        log.info("Warning: got here how?")
        return False

    def getExtendedSiteName(self, layers):
        """Returns site name (domain name), informed by the list of active layers."""
        if layers==["core"]:
            return "schema.org"
        if len(layers)==0:
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
                nodeTypes = GetTargets(Unit.GetUnit("typeOf"), node, layers=layers)
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

            template = JINJA_ENVIRONMENT.get_template('genericTermPageHeader.tpl')
            template_values = {
                'entry': str(entry),
                'desc' : desc,
                'sitemode': sitemode,
                'sitename': getSiteName(),
                'staticPath': makeUrl("",""),
                'menu_sel': "Schemas",
                'rdfs_type': rdfs_type,
                'ext_mappings': ext_mappings
            }
            out = template.render(template_values)
            DataCache.put(generated_page_id,out)
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




    def emitExactTermPage(self, node, layers="core"):
        """Emit a Web page that exactly matches this node."""
        log.debug("EXACT PAGE: %s" % node.id)
        self.outputStrings = [] # blank slate
        ext_mappings = GetExtMappingsRDFa(node, layers=layers)

        global sitemode #,sitename
        if ("schema.org" not in self.request.host and sitemode == "mainsite"):
            sitemode = "mainsite testsite"

        self.emitSchemaorgHeaders(node, ext_mappings, sitemode, getSiteName(), layers)

        if ( ENABLE_HOSTED_EXTENSIONS and ("core" not in layers or len(layers)>1) ):
            ll = " ".join(layers).replace("core","")

            target=""
            if inLayer("core", node):
                target = node.id


            s = "<p id='lli' class='layerinfo %s'><a href=\"https://github.com/schemaorg/schemaorg/wiki/ExtensionList\">extension shown</a>: %s [<a href='%s'>x</a>]</p>\n" % (ll, ll, makeUrl("",target))
            self.write(s)

        cached = self.GetCachedText(node, layers)
        if (cached != None):
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

        elif (Unit.isAttribute(node, layers=layers)):
            self.emitAttributeProperties(node, layers=layers)
            self.write(self.moreInfoBlock(node))

        if (node.isClass(layers=layers)):
            children = []
            children = GetSources(Unit.GetUnit("rdfs:subClassOf"), node, ALL_LAYERS)# Normal subclasses
            if(node.isDataType() or node.id == "DataType"):
                children += GetSources(Unit.GetUnit("typeOf"), node, ALL_LAYERS)# Datatypes
            children = sorted(children, key=lambda u: u.id)

            if (len(children) > 0):
                buff = StringIO.StringIO()
                extbuff = StringIO.StringIO()

                firstext=True
                for c in children:
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

            children = sorted(GetSources(Unit.GetUnit("typeOf"), node, ALL_LAYERS), key=lambda u: u.id)
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
            self.write("<h4  id=\"acks\">Acknowledgements</h4>\n")
            for ao in ackorgs:
                acks = sorted(GetTargets(Unit.GetUnit("rdfs:comment"), ao, layers))
                for ack in acks:
                    self.write(str(ack+"<br/>"))

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
            for ex in examples:
                if "id" in ex.egmeta:
                    self.write('<span id="%s"></span>' % ex.egmeta["id"])
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

        self.response.write(self.AddCachedText(node, self.outputStrings, layers))

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
        log.debug("layerlist: %s" % layerlist)
        return layerlist

    def handleJSONContext(self, node):
        """Handle JSON-LD Context non-homepage requests (including refuse if not enabled)."""

        if not ENABLE_JSONLD_CONTEXT:
            self.error(404)
            self.response.out.write('<title>404 Not Found.</title><a href="/">404 Not Found (JSON-LD Context not enabled.)</a><br/><br/>')
            return True

        if (node=="docs/jsonldcontext.json.txt"):
            jsonldcontext = GetJsonLdContext(layers=ALL_LAYERS)
            self.response.headers['Content-Type'] = "text/plain"
            self.emitCacheHeaders()
            self.response.out.write( jsonldcontext )
            return True
        if (node=="docs/jsonldcontext.json"):
            jsonldcontext = GetJsonLdContext(layers=ALL_LAYERS)
            self.response.headers['Content-Type'] = "application/ld+json"
            self.emitCacheHeaders()
            self.response.out.write( jsonldcontext )
            return True
        return False
        # see also handleHomepage for conneg'd version.

    def handleSchemasPage(self, node,  layerlist='core'):
        self.response.headers['Content-Type'] = "text/html"
        self.emitCacheHeaders()

        if DataCache.get('SchemasPage'):
            self.response.out.write( DataCache.get('SchemasPage') )
            log.debug("Serving recycled SchemasPage.")
            return True
        else:
            extensions = []
            for ex in sorted(ENABLED_EXTENSIONS):
                extensions.append("<a href=\"%s\">%s.schema.org</a>" % (makeUrl(ex,""),ex))

            template = JINJA_ENVIRONMENT.get_template('schemas.tpl')
            page = template.render({'sitename': getSiteName(),
                                    'staticPath': makeUrl("",""),
                                    'counts': self.getCounts(),
                                    'extensions': extensions,
                                    'menu_sel': "Schemas"})

            self.response.out.write( page )
            log.debug("Serving fresh SchemasPage.")
            DataCache.put("SchemasPage",page)

            return True

    def getCounts(self):
        text = ""
        text += "The core vocabulary currently consists of %s Types, " % len(GetAllTypes("core"))
        text += " %s Properties, " % len(GetAllProperties("core"))
        text += "and %s Enumeration values." % len(GetAllEnumerationValues("core"))
        return text


    def handleFullHierarchyPage(self, node,  layerlist='core'):
        self.response.headers['Content-Type'] = "text/html"
        self.emitCacheHeaders()

        if DataCache.get('FullTreePage'):
            self.response.out.write( DataCache.get('FullTreePage') )
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
            #az_enums = GetAllEnumerationValues(layerlist)
            #az_enums.sort( key = lambda u: u.id)
            #thing_tree += self.listTerms(az_enums,"<br/><strong>Enumeration Values</strong><br/>")


            fullmainroot = TypeHierarchyTree("<h3>Core plus all extension vocabularies</h3>")
            fullmainroot.traverseForHTML(uThing, layers=ALL_LAYERS)
            full_thing_tree = fullmainroot.toHTML()
            #az_enums = GetAllEnumerationValues(ALL_LAYERS)
            #az_enums.sort( key = lambda u: u.id)
            #full_thing_tree += self.listTerms(az_enums,"<br/><strong>Enumeration Values</strong><br/>")

            ext_thing_tree = None
            if len(extonlylist) > 0:
                extroot = TypeHierarchyTree("<h3>Extension: %s</h3>" % extlist)
                extroot.traverseForHTML(uThing, layers=extonlylist)
                ext_thing_tree = extroot.toHTML()
                #az_enums = GetAllEnumerationValues(extonlylist)
                #az_enums.sort( key = lambda u: u.id)
                #ext_thing_tree += self.listTerms(az_enums,"<br/><strong>Enumeration Values</strong><br/>")


            dtroot = TypeHierarchyTree("<h4>Data Types</h4>")
            dtroot.traverseForHTML(uDataType, layers=layerlist)
            datatype_tree = dtroot.toHTML()

            full_button = "Core plus all extensions"

            page = template.render({ 'thing_tree': thing_tree,
                                    'full_thing_tree': full_thing_tree,
                                    'ext_thing_tree': ext_thing_tree,
                                    'datatype_tree': datatype_tree,
                                    'local_button': local_button,
                                    'full_button': full_button,
                                    'ext_button': ext_button,
                                    'sitename': getSiteName(),
                                    'staticPath': makeUrl("",""),
                                    'menu_sel': "Schemas"})

            self.response.out.write( page )
            log.debug("Serving fresh FullTreePage.")
            DataCache.put("FullTreePage",page)

            return True

    def handleJSONSchemaTree(self, node, layerlist='core'):
        """Handle a request for a JSON-LD tree representation of the schemas (RDFS-based)."""

        self.response.headers['Content-Type'] = "application/ld+json"
        self.emitCacheHeaders()

        if DataCache.get('JSONLDThingTree'):
            self.response.out.write( DataCache.get('JSONLDThingTree') )
            log.debug("Serving recycled JSONLDThingTree.")
            return True
        else:
            uThing = Unit.GetUnit("Thing")
            mainroot = TypeHierarchyTree()
            mainroot.traverseForJSONLD(Unit.GetUnit("Thing"), layers=layerlist)
            thing_tree = mainroot.toJSON()
            self.response.out.write( thing_tree )
            log.debug("Serving fresh JSONLDThingTree.")
            DataCache.put("JSONLDThingTree",thing_tree)
            return True
        return False


    def handleExactTermPage(self, node, layers='core'):
        """Handle with requests for specific terms like /Person, /fooBar. """

        #self.outputStrings = [] # blank slate
        schema_node = Unit.GetUnit(node) # e.g. "Person", "CreativeWork".
        log.debug("Layers: %s",layers)
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
                for x in all_terms[schema_node.id]:
                    x = x.replace("#","")
                    ext = {}
                    ext['href'] = makeUrl(x,schema_node.id)
                    ext['text'] = x
                    extensions.append(ext)
                    #self.response.out.write("<li><a href='%s'>%s</a></li>" % (makeUrl(x,schema_node.id), x) )

                template = JINJA_ENVIRONMENT.get_template('wrongExt.tpl')
                page = template.render({ 'target': schema_node.id,
                                        'extensions': extensions,
                                        'sitename': "schema.org",
                                        'staticPath': makeUrl("","")})

                self.response.out.write( page )
                log.debug("Serving fresh wrongExtPage.")
                return True
            return False

    def handle404Failure(self, node, layers="core"):
        self.error(404)
        self.emitSchemaorgHeaders("404 Missing")
        self.response.out.write('<h3>404 Not Found.</h3><p><br/>Page not found. Please <a href="/">try the homepage.</a><br/><br/></p>')


        clean_node = cleanPath(node)

        log.debug("404: clean_node: clean_node: %s node: %s" % (clean_node, node))

        base_term = Unit.GetUnit( node.rsplit('/')[0] )
        if base_term != None :
            self.response.out.write('<div>Perhaps you meant: <a href="/%s">%s</a></div> <br/><br/> ' % ( base_term.id, base_term.id ))

        base_actionprop = Unit.GetUnit( node.rsplit('-')[0] )
        if base_actionprop != None :
            self.response.out.write('<div>Looking for an <a href="/Action">Action</a>-related property? Note that xyz-input and xyz-output have <a href="/docs/actions.html">special meaning</a>. See also: <a href="/%s">%s</a></div> <br/><br/> ' % ( base_actionprop.id, base_actionprop.id ))

        return True

#    def handleJSONSchemaTree(self, node, layerlist='core'):
#        """Handle a request for a JSON-LD tree representation of the schemas (RDFS-based)."""
#
#        self.response.headers['Content-Type'] = "application/ld+json"
#        self.emitCacheHeaders()
#
#        if DataCache.get('JSONLDThingTree'):
#            self.response.out.write( DataCache.get('JSONLDThingTree') )
#            log.debug("Serving recycled JSONLDThingTree.")
#            return True
#        else:
#            uThing = Unit.GetUnit("Thing")
#            mainroot = TypeHierarchyTree()
#            mainroot.traverseForJSONLD(Unit.GetUnit("Thing"), layers=layerlist)
#            thing_tree = mainroot.toJSON()
#            self.response.out.write( thing_tree )
#            log.debug("Serving fresh JSONLDThingTree.")
#            DataCache.put("JSONLDThingTree",thing_tree)
#            return True
#        return False



    # if (node == "version/2.0/" or node == "version/latest/" or "version/" in node) ...

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
            if DataCache.get('tocVersionPage'):
                self.response.out.write( DataCache.get('tocVersionPage'))
                return True
            else:
                log.debug("Serving tocversionPage from cache.")
                template = JINJA_ENVIRONMENT.get_template('tocVersionPage.tpl')
                page = template.render({ "releases": releaselog.keys(),
                                         "menu_sel": "Schemas",
                                         "sitename": getSiteName(),
                                         'staticPath': makeUrl("","")})

                self.response.out.write( page )
                log.debug("Serving fresh tocVersionPage.")
                DataCache.put("tocVersionPage",page)
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

            if requested_version != "latest":
                return False
                log.info("giving up to 404.")
            else:
                log.info("generating a live view of this latest release.")


        if DataCache.get('FullReleasePage'):
            self.response.out.write( DataCache.get('FullReleasePage') )
            log.debug("Serving recycled FullReleasePage.")
            return True
        else:
            template = JINJA_ENVIRONMENT.get_template('fullReleasePage.tpl')
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

            page = template.render({ "base_href": base_href, 'thing_tree': thing_tree,
                    'liveversion': SCHEMA_VERSION,
                    'requested_version': requested_version,
                    'releasedate': releaselog[str(SCHEMA_VERSION)],
                    'az_props': az_props, 'az_types': az_types,
                    'az_prop_meta': az_prop_meta, 'az_type_meta': az_type_meta,
                    'sitename': getSiteName(),
                    'staticPath': makeUrl("",""),
                    'menu_sel': "Documentation"})

            self.response.out.write( page )
            log.debug("Serving fresh FullReleasePage.")
            DataCache.put("FullReleasePage",page)
            return True

    def handleExtensionContents(self,ext):
        if not ext in ENABLED_EXTENSIONS:
            log.info("cannot list ext %s",ext)
            return ""

        buff = StringIO.StringIO()

        az_types = GetAllTypes(ext)
        az_types.sort( key=lambda u: u.id)
        az_props = GetAllProperties(ext)
        az_props.sort( key = lambda u: u.id)
        az_enums = GetAllEnumerationValues(ext)
        az_enums.sort( key = lambda u: u.id)

        buff.write("<br/><h3>Terms defined or referenced in the '%s' extension.</h3>" % ext)
        buff.write(self.listTerms(az_types,"<br/><strong>Types</strong> (%s)<br/>" % len(az_types)))
        buff.write(self.listTerms(az_props,"<br/><br/><strong>Properties</strong> (%s)<br/>" % len(az_props)))
        buff.write(self.listTerms(az_enums,"<br/><br/><strong>Enumeration values</strong> (%s)<br/>" % len(az_enums)))
        ret = buff.getvalue()
        buff.close()
        return ret

    def listTerms(self,terms,prefix=""):
        buff = StringIO.StringIO()
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
        if test == "":
            hostString = self.request.host

        scheme = "http" #Defalt for tests
        if not getInTestHarness():  #Get the actual scheme from the request
            scheme = self.request.scheme

        host_ext = re.match( r'([\w\-_]+)[\.:]?', hostString).group(1)
        log.info("setupHostinfo: scheme=%s hoststring=%s host_ext?=%s" % (scheme, hostString, str(host_ext) ))

        setHttpScheme(scheme)

        split = hostString.rsplit(':')
        myhost = split[0]
        mybasehost = myhost
        myport = "80"
        if len(split) > 1:
            myport = split[1]

        if host_ext != None:
            # e.g. "bib"
            log.debug("HOST: Found %s in %s" % ( host_ext, hostString ))
            if host_ext == "www":
                # www is special case that cannot be an extension - need to redirect to basehost
                mybasehost = mybasehost[4:]
                return self.redirectToBase(node)
            elif not host_ext in ENABLED_EXTENSIONS:
                host_ext = ""
            else:
                mybasehost = mybasehost[len(host_ext) + 1:]

        setHostExt(host_ext)
        setBaseHost(mybasehost)
        setHostPort(myport)

        dcn = host_ext
        if dcn == None or dcn == "" or dcn =="core":
            dcn = "core"

        log.debug("sdoapp.py setting current datacache to: %s " % dcn)
        DataCache.setCurrent(dcn)


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


    def get(self, node):

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
        """

        if not self.setupHostinfo(node):
            return

        self.callCount()

        self.emitHTTPHeaders(node)

        if (node in silent_skip_list):
            return

        if ENABLE_HOSTED_EXTENSIONS:
            layerlist = self.setupExtensionLayerlist(node) # e.g. ['core', 'bib']
        else:
            layerlist = ["core"]

        setSiteName(self.getExtendedSiteName(layerlist)) # e.g. 'bib.schema.org', 'schema.org'

        log.debug("EXT: set sitename to %s " % getSiteName())
        if (node in ["", "/"]):
            if self.handleHomepage(node):
                return
            else:
                log.info("Error handling homepage: %s" % node)
                return

        if node in ["docs/jsonldcontext.json.txt", "docs/jsonldcontext.json"]:
            if self.handleJSONContext(node):
                return
            else:
                log.info("Error handling JSON-LD context: %s" % node)
                return

        if (node == "docs/full.html"): # DataCache.getDataCache.get
            if self.handleFullHierarchyPage(node, layerlist=layerlist):
                return
            else:
                log.info("Error handling full.html : %s " % node)
                return

        if (node == "docs/schemas.html"): # DataCache.getDataCache.get
            if self.handleSchemasPage(node, layerlist=layerlist):
                return
            else:
                log.info("Error handling schemas.html : %s " % node)
                return



        if (node == "docs/tree.jsonld" or node == "docs/tree.json"):
            if self.handleJSONSchemaTree(node, layerlist=ALL_LAYERS):
                return
            else:
                log.info("Error handling JSON-LD schema tree: %s " % node)
                return

        if (node == "version/2.0/" or node == "version/latest/" or "version/" in node):
            if self.handleFullReleasePage(node, layerlist=layerlist):
                return
            else:
                log.info("Error handling full release page: %s " % node)
                if self.handle404Failure(node):
                    return
                else:
                    log.info("Error handling 404 under /version/")
                    return

        if(node == "_siteDebug"):
            self.siteDebug()
            return

        # Pages based on request path matching a Unit in the term graph:
        if self.handleExactTermPage(node, layers=layerlist):
            return
        else:
            log.info("Error handling exact term page. Assuming a 404: %s" % node)

            # Drop through to 404 as default exit.
            if self.handle404Failure(node):
                return
            else:
                log.info("Error handling 404.")
                return

    def siteDebug(self):
        global STATS
        template = JINJA_ENVIRONMENT.get_template('siteDebug.tpl')
        page = template.render({'sitename': getSiteName(),
                                'staticPath': makeUrl("","")})

        self.response.out.write( page )
        self.response.out.write("<table style=\"width: 50%; border: solid 1px #CCCCCC; border-collapse: collapse;\"><tbody>\n")
        self.writeDebugRow("Setting","Value",True)

        self.writeDebugRow("httpScheme",getHttpScheme())
        self.writeDebugRow("host_ext",getHostExt())
        self.writeDebugRow("basehost",getBaseHost())
        self.writeDebugRow("hostport",getHostPort())
        self.writeDebugRow("sitename",getSiteName())
        self.writeDebugRow("debugging",getAppVar('debugging'))
        self.writeDebugRow("intestharness",getInTestHarness())
        self.writeDebugRow("Current DataCache",DataCache.getCurrent())
        self.writeDebugRow("DataCaches",len(DataCache.keys()))
        for c in DataCache.keys():
            self.writeDebugRow("DataCache[%s] size" % c, len(DataCache.getCache(c)))
        for s in STATS.keys():
            self.writeDebugRow("%s" % s, STATS[s])

        self.response.out.write("</tbody><table><br/>\n")
        self.response.out.write( "</div>\n<body>\n</html>" )

    def writeDebugRow(self,term,value,head=False):
        rt = "td"
        cellStyle = "border: solid 1px #CCCCCC; border-collapse: collapse;"
        if head:
            rt = "th"
            cellStyle += " color: #FFFFFF; background: #888888;"

        self.response.out.write("<tr><%s style=\"%s\">%s</%s><%s style=\"%s\">%s</%s></tr>\n" % (rt,cellStyle,term,rt,rt,cellStyle,value,rt))

    def callCount(self):
        statInc("total calls")
        statInc(getHttpScheme() + " calls")
        if getHostExt() != "":
            statInc(getHostExt() + " calls")
        else:
            statInc("core calls")


STATS = {}
def statInc(stat):
    global STATS
    val = 1
    if stat in STATS:
        val += STATS.get(stat)
    STATS[stat] = val


def setInTestHarness(val):
    global INTESTHARNESS
    INTESTHARNESS = val
def getInTestHarness():
    global INTESTHARNESS
    return INTESTHARNESS

TestAppIndex = {}
def getAppVar(index):
    global TestAppIndex

    reg = None
    if not getInTestHarness():
        app = webapp2.get_app()
        reg = app.registry
    else:
        log.debug("getAppVar(): Using non-threadsafe session variables for test only")
        reg = TestAppIndex

    return reg.get(index)

def setAppVar(index,val):
    global TestAppIndex

    reg = None
    if not getInTestHarness():
        app = webapp2.get_app()
        reg = app.registry
    else:
        log.debug("setAppVar(): Using non-threadsafe session variables for test only")
        reg = TestAppIndex

    reg[index] = val

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

#log.info("STARTING UP... reading schemas.")
read_schemas(loadExtensions=ENABLE_HOSTED_EXTENSIONS)
if ENABLE_HOSTED_EXTENSIONS:
    read_extensions(ENABLED_EXTENSIONS)
schemasInitialized = True

app = ndb.toplevel(webapp2.WSGIApplication([("/(.*)", ShowUnit)]))
