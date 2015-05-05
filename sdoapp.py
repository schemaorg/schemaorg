#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import webapp2
import jinja2
import re
from google.appengine.ext import ndb
from google.appengine.ext import blobstore
from google.appengine.api import users
from google.appengine.ext.webapp import blobstore_handlers
import logging
import parsers
import headers
import os

from api import inLayer, read_file, full_path, read_schemas, namespaces, DataCache
from api import Unit, GetTargets, GetSources
from api import GetComment, all_terms, GetAllTypes
from api import GetParentList, GetImmediateSubtypes, HasMultipleBaseTypes

logging.basicConfig(level=logging.INFO) # dev_appserver.py --log_level debug .
log = logging.getLogger(__name__)

SCHEMA_VERSION=1.999999
sitename = "schema.org"
sitemode = "mainsite" # whitespaced list for CSS tags,
            # e.g. "mainsite testsite" when off expected domains
            # "extensionsite" when in an extension (e.g. blue?)

# Declare here as used here, not in api.py any more:

all_layers = {}
ext_re = re.compile(r'([^\w,])+')
PageCache = {}

#TODO: Modes:
# mainsite
# webschemadev
# known extension (not skiplist'd, eg. demo1 on schema.org)

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')),
    extensions=['jinja2.ext.autoescape'], autoescape=True)


ENABLE_JSONLD_CONTEXT = True
ENABLE_CORS = True

os_host = os.environ.get('HTTP_HOST', 'localhost')
host_ext = re.match(r'(\w*)[.:]',os_host)
if host_ext != None:
    host_ext = host_ext.group(1) # e.g. "bib"

debugging = False
if host_ext == "localhost" or  "webschemas" in os_host:
    debugging = True

# Core API: we have a single schema graph built from triples and units.
# now in api.py


class TypeHierarchyTree:

    def __init__(self):
        self.txt = ""
        self.visited = {}

    def emit(self, s):
        self.txt += s + "\n"

    def toHTML(self):
        return '<ul>%s</ul>' % self.txt

    def toJSON(self):
        return self.txt

    def traverseForHTML(self, node, depth = 1, layers='core'):

        # we are a supertype of some kind
        if len(node.GetImmediateSubtypes(layers=layers)) > 0:

            # and we haven't been here before
            if node.id not in self.visited:
                self.visited[node.id] = True # remember our visit
                self.emit( ' %s<li class="tbranch" id="%s"><a href="/%s">%s</a>' % (" " * 4 * depth, node.id, node.id, node.id) )
                self.emit(' %s<ul>' % (" " * 4 * depth))

                # handle our subtypes
                for item in node.GetImmediateSubtypes(layers=layers):
                    self.traverseForHTML(item, depth + 1, layers=layers)
                self.emit( ' %s</ul>' % (" " * 4 * depth))
            else:
                # we are a supertype but we visited this type before, e.g. saw Restaurant via Place then via Organization
                seen = '  <a href="#%s">*</a> ' % node.id
                self.emit( ' %s<li class="tbranch" id="%s"><a href="/%s">%s</a>%s' % (" " * 4 * depth, node.id, node.id, node.id, seen) )

        # leaf nodes
        if len(node.GetImmediateSubtypes(layers=layers)) == 0:
            if node.id not in self.visited:
                self.emit( '%s<li class="tleaf" id="%s"><a href="/%s">%s</a>%s' % (" " * depth, node.id, node.id, node.id, "" ))
            #else:
                #self.visited[node.id] = True # never...
                # we tolerate "VideoGame" appearing under both Game and SoftwareApplication
                # and would only suppress it if it had its own subtypes. Seems legit.

        self.emit( ' %s</li>' % (" " * 4 * depth) )

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
        comment = comment.replace('"',"'")
        comment = re.sub('<[^<]+?>', '', comment)[:60]

        self.emit('\n%s{\n%s\n%s"@type": "rdfs:Class", %s "description": "%s...",\n%s"name": "%s",\n%s"@id": "schema:%s"%s'
                  % (p1, ctx, p1,                 supertx,            comment,     p1,   node.id, p1,        node.id,  maybe_comma))

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


class Example ():

    @staticmethod
    def AddExample(terms, original_html, microdata, rdfa, jsonld, egmeta, layer='core'):
       """
       Add an Example (via constructor registering it with the terms that it
       mentions, i.e. stored in term.examples).
       """
       # todo: fix partial examples: if (len(terms) > 0 and len(original_html) > 0 and (len(microdata) > 0 or len(rdfa) > 0 or len(jsonld) > 0)):
       if (len(terms) > 0 and len(original_html) > 0 and len(microdata) > 0 and len(rdfa) > 0 and len(jsonld) > 0):
            return Example(terms, original_html, microdata, rdfa, jsonld, egmeta, layer='core')

    def get(self, name, layers='core') :
        """Exposes original_content, microdata, rdfa and jsonld versions (in the layer(s) specified)."""
        if name == 'original_html':
           return self.original_html
        if name == 'microdata':
           return self.microdata
        if name == 'rdfa':
           return self.rdfa
        if name == 'jsonld':
           return self.jsonld

    def __init__ (self, terms, original_html, microdata, rdfa, jsonld, egmeta, layer='core'):
        """Example constructor, registers itself with the relevant Unit(s)."""
        self.terms = terms
        self.original_html = original_html
        self.microdata = microdata
        self.rdfa = rdfa
        self.jsonld = jsonld
        self.egmeta = egmeta
        self.layer = layer
        for term in terms:
            if "id" in egmeta:
              logging.debug("Created Example with ID %s and type %s" % ( egmeta["id"], term.id ))
            term.examples.append(self)



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

def GetJsonLdContext(layers='core'):
    """Generates a basic JSON-LD context file for schema.org."""
    global namespaces;
    jsonldcontext = "{\"@context\":    {\n"
    jsonldcontext += namespaces ;
    jsonldcontext += "        \"@vocab\": \"http://schema.org/\",\n"

    url = Unit.GetUnit("URL")
    date = Unit.GetUnit("Date")
    datetime = Unit.GetUnit("DateTime")

    properties = sorted(GetSources(Unit.GetUnit("typeOf"), Unit.GetUnit("rdf:Property"), layers=layers), key=lambda u: u.id)
    for p in properties:
        range = GetTargets(Unit.GetUnit("rangeIncludes"), p, layers=layers)
        type = None

        if url in range:
            type = "@id"
        elif date in range:
            type = "Date"
        elif datetime in range:
            type = "DateTime"

        if type:
            jsonldcontext += "        \"" + p.id + "\": { \"@type\": \"" + type + "\" },"

    jsonldcontext += "}}\n"
    jsonldcontext = jsonldcontext.replace("},}}","}\n    }\n}")
    jsonldcontext = jsonldcontext.replace("},","},\n")

    return jsonldcontext

class ShowUnit (webapp2.RequestHandler):
    """ShowUnit exposes schema.org terms via Web RequestHandler
    (HTML/HTTP etc.).
    """
    def emitCacheHeaders(self):
        """Send cache-related headers via HTTP."""
        self.response.headers['Cache-Control'] = "public, max-age=43200" # 12h
        self.response.headers['Vary'] = "Accept, Accept-Encoding"

    def GetCachedText(self, node, layers='core'):
        """Return page text from node.id cache (if found, otherwise None)."""
        global PageCache
        cachekey = "%s:%s" % ( layers, node.id ) # was node.id
        #if (node.id in PageCache):
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

        items = [

         "<a href='https://github.com/schemaorg/schemaorg/issues?q=is%3Aissue+is%3Aopen+{0}'>Check for open issues.</a>".format(node.id)
        ]

        for l in all_terms[node.id]:
            l = l.replace("#","")
            items.append("'{0}' is mentioned in extension layer: <a href='?ext={1}'>{2}</a>".format( node.id, l, l ))

        moreinfo = """<div>
        <div id='infobox' style='text-align: right;'><b><span style="cursor: pointer;">[more...]</span></b></div>
        <div id='infomsg' style='display: none; background-color: #EEEEEE; text-align: left; padding: 0.5em;'>
        <ul>"""

        for i in items:
            moreinfo += "<li>%s</li>" % i

#          <li>mappings to other terms.</li>
#          <li>or links to open issues.</li>

        moreinfo += """</ul>
          </div>
        </div</div>
        <script type="text/javascript">
        $("#infobox").click(function(x) {
            element = $("#infomsg");
            if (! $(element).is(":visible")) {
                $("#infomsg").show(300);
            } else {
                $("#infomsg").hide(300);

            }
        });
</script>"""
        return moreinfo

    def GetParentStack(self, node, layers='core'):
        """Returns a hiearchical structured used for site breadcrumbs."""
        if (node not in self.parentStack):
            self.parentStack.append(node)

        if (Unit.isAttribute(node, layers=layers)):
            self.parentStack.append(Unit.GetUnit("Property"))
            self.parentStack.append(Unit.GetUnit("Thing"))

        sc = Unit.GetUnit("rdfs:subClassOf")
        if GetTargets(sc, node, layers=layers):
            for p in GetTargets(sc, node, layers=layers):
                self.GetParentStack(p, layers=layers)
        else:
            # Enumerations are classes that have no declared subclasses
            sc = Unit.GetUnit("typeOf")
            for p in GetTargets(sc, node, layers=layers):
                self.GetParentStack(p, layers=layers)

    def ml(self, node, label='', title='', prop=''):
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
        return "<a href=\"%s\"%s%s>%s</a>" % (node.id, prop, title, label)

    def makeLinksFromArray(self, nodearray, tooltip=''):
        """Make a comma separate list of links via ml() function.

        * tooltip - optional text to use as title of all links
        """
        hyperlinks = []
        for f in nodearray:
           hyperlinks.append(self.ml(f, f.id, tooltip))
        return (", ".join(hyperlinks))

    def UnitHeaders(self, node, layers='core'):
        """Write out the HTML page headers for this node."""
        self.write("<h1 class=\"page-title\">\n")
        ind = len(self.parentStack)
        thing_seen = False
        while (ind > 0) :
            ind = ind -1
            nn = self.parentStack[ind]
            if (nn.id == "Thing" or thing_seen or nn.isDataType(layers=layers)):
                thing_seen = True
                self.write(self.ml(nn) )
                if ind == 1 and node.isEnumerationValue(layers=layers):
                    self.write(" :: ")
                elif ind > 0:
                    self.write(" &gt; ")
                if ind == 1:
                    self.write("<span property=\"rdfs:label\">")
                if ind == 0:
                    self.write("</span>")
        self.write("</h1>")
        comment = GetComment(node, layers)
        self.write(" <div property=\"rdfs:comment\">%s</div>\n\n" % (comment) + "\n")

        self.write(" <br><div>Usage: %s</div>\n\n" % (node.UsageStr()) + "\n")

        self.write(self.moreInfoBlock(node))

        if (node.isClass(layers=layers) and not node.isDataType(layers=layers)):

            self.write("<table class=\"definition-table\">\n        <thead>\n  <tr><th>Property</th><th>Expected Type</th><th>Description</th>               \n  </tr>\n  </thead>\n\n")

    def ClassProperties (self, cl, subclass=False, layers="core"):
        """Write out a table of properties for a per-type page."""

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
                self.write("<thead class=\"supertype\">\n  <tr>\n    <th class=\"supertype-name\" colspan=\"3\">Properties from %s</th>\n  </tr>\n</thead>\n\n<tbody class=\"supertype\">\n  " % (class_head))
                headerPrinted = True

            self.write("<tr typeof=\"rdfs:Property\" resource=\"http://schema.org/%s\">\n    \n      <th class=\"prop-nam\" scope=\"row\">\n\n<code property=\"rdfs:label\">%s</code>\n    </th>\n " % (prop.id, self.ml(prop)))
            self.write("<td class=\"prop-ect\">\n")
            first_range = True
            for r in ranges:
                if (not first_range):
                    self.write(" or <br/> ")
                first_range = False
                self.write(self.ml(r, prop='rangeIncludes'))
                self.write("&nbsp;")
            self.write("</td>")
            self.write("<td class=\"prop-desc\" property=\"rdfs:comment\">%s" % (comment))
            if (len(olderprops) > 0):
                olderlinks = ", ".join([self.ml(o) for o in olderprops])
                self.write(" Supersedes %s." % olderlinks )
            if (inverseprop != None):
                self.write("<br/> Inverse property: %s." % (self.ml(inverseprop)))

            self.write("</td></tr>")
            subclass = False

        if subclass: # in case the superclass has no defined attributes
            self.write("<meta property=\"rdfs:subClassOf\" content=\"%s\">" % (cl.id))

    def ClassIncomingProperties (self, cl, layers="core"):
        """Write out a table of incoming properties for a per-type page."""
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


    def AttributeProperties (self, node, layers="core"):
        """Write out properties of this property, for a per-property page."""
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
            self.write("<p>Inverse-property: %s.</p>" % (self.ml(inverseprop, inverseprop.id,tt)) )

        self.write("<table class=\"definition-table\">\n")
        self.write("<thead>\n  <tr>\n    <th>Values expected to be one of these types</th>\n  </tr>\n</thead>\n\n  <tr>\n    <td>\n      ")

        for r in ranges:
            if (not first_range):
                self.write("<br/>")
            first_range = False
            tt = "The '%s' property has values that include instances of the '%s' type." % (node.id, r.id)
            self.write(" <code>%s</code> " % (self.ml(r, r.id, tt, prop="rangeIncludes"))+"\n")
        self.write("    </td>\n  </tr>\n</table>\n\n")
        first_domain = True

        self.write("<table class=\"definition-table\">\n")
        self.write("  <thead>\n    <tr>\n      <th>Used on these types</th>\n    </tr>\n</thead>\n<tr>\n  <td>")
        for d in domains:
            if (not first_domain):
                self.write("<br/>")
            first_domain = False
            tt = "The '%s' property is used on the '%s' type." % (node.id, d.id)
            self.write("\n    <code>%s</code> " % (self.ml(d, d.id, tt, prop="domainIncludes"))+"\n")
        self.write("      </td>\n    </tr>\n</table>\n\n")

        if (subprops != None and len(subprops) > 0):
            self.write("<table class=\"definition-table\">\n")
            self.write("  <thead>\n    <tr>\n      <th>Sub-properties</th>\n    </tr>\n</thead>\n")
            for sbp in subprops:
                c = GetComment(sbp,layers=layers)
                tt = "%s: ''%s''" % ( sbp.id, c)
                self.write("\n    <tr><td><code>%s</code></td></tr>\n" % (self.ml(sbp, sbp.id, tt)))
            self.write("\n</table>\n\n")

        # Super-properties
        if (superprops != None and  len(superprops) > 0):
            self.write("<table class=\"definition-table\">\n")
            self.write("  <thead>\n    <tr>\n      <th>Super-properties</th>\n    </tr>\n</thead>\n")
            for spp in superprops:
                c = GetComment(spp, layers=layers)           # markup needs to be stripped from c, e.g. see 'logo', 'photo'
                c = re.sub(r'<[^>]*>', '', c) # This is not a sanitizer, we trust our input.
                tt = "%s: ''%s''" % ( spp.id, c)
                self.write("\n    <tr><td><code>%s</code></td></tr>\n" % (self.ml(spp, spp.id, tt)))
            self.write("\n</table>\n\n")

        # Supersedes
        if (olderprops != None and len(olderprops) > 0):
            self.write("<table class=\"definition-table\">\n")
            self.write("  <thead>\n    <tr>\n      <th>Supersedes</th>\n    </tr>\n</thead>\n")

            for o in olderprops:
                c = GetComment(o, layers=layers)
                tt = "%s: ''%s''" % ( o.id, c)
                self.write("\n    <tr><td><code>%s</code></td></tr>\n" % (self.ml(o, o.id, tt)))
            self.write("\n</table>\n\n")

        # supersededBy (at most one direct successor)
        if (newerprop != None):
            self.write("<table class=\"definition-table\">\n")
            self.write("  <thead>\n    <tr>\n      <th><a href=\"/supersededBy\">supersededBy</a></th>\n    </tr>\n</thead>\n")
            self.write("\n    <tr><td><code>%s</code></td></tr>\n" % (self.ml(newerprop, newerprop.id, tt)))
            self.write("\n</table>\n\n")

    def rep(self, markup):
        """Replace < and > with HTML escape chars."""
        m1 = re.sub("<", "&lt;", markup)
        m2 = re.sub(">", "&gt;", m1)
        # TODO: Ampersand? Check usage with examples.
        return m2

    def getHomepage(self, node):
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
            jsonldcontext = GetJsonLdContext() # consider memcached?

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
            return
        else:
            # Serve a homepage from template
            # the .tpl has responsibility for extension homepages
            # TODO: pass in extension, base_domain etc.
            hp = DataCache.get("homepage")
            if hp != None:
                self.response.out.write( hp )
                log.info("Served datacache homepage.tpl")
            else:
                template = JINJA_ENVIRONMENT.get_template('homepage.tpl')
                template_values = {
                    'ENABLE_JSONLD_CONTEXT': ENABLE_JSONLD_CONTEXT,
                    'ENABLE_CORS': ENABLE_CORS,
                    'SCHEMA_VERSION': SCHEMA_VERSION,
                    'os_host': os_host,
                    'host_ext': host_ext,
                    'debugging': debugging
                }
                page = template.render(template_values)
                self.response.out.write( page )
                log.info("Served fresh homepage.tpl")
                DataCache["homepage"] = page
                #            self.response.out.write( open("static/index.html", 'r').read() )
            return
        log.info("Warning: got here how?")
        return
    log.info("Error: unreachable reached.")

    def getExtendedSiteName(self, layers):
        """Returns site name (domain name), informed by the list of active layers."""
        if layers==["core"]:
            return "schema.org"
        # layers.remove("core")
        return (layers[ len(layers)-1 ] + ".schema.org")

    def getExactTermPage(self, node, layers="core"):
        """Emit a Web page that exactly matches this node."""
        self.outputStrings = []
        log.info("EXACT PAGE: %s" % node.id)
        ext_mappings = GetExtMappingsRDFa(node, layers=layers)

        global sitemode

        if ("schema.org" not in os_host and sitemode == "mainsite"):
            sitemode = "mainsite testsite"

        global sitename
        headers.OutputSchemaorgHeaders(self, node.id, node.isClass(), ext_mappings, sitemode, sitename)

        if ("core" not in layers or len(layers)>1):
            ll = " ".join(layers).replace("#","")

            s = "<p id='lli' class='layerinfo %s'><a href=\"https://github.com/schemaorg/schemaorg/wiki/ExtensionList\">extensions shown</a>: %s [<a href='http://schema.org/%s'>x</a>]</p>\n" % (ll, ll, node.id )
            self.write(s)
#            self.write("<!-- Layers: %s -->" % layers)

#        if ("localhost" in os_host):
#            self.write("<p id='localhost_note' class='layerinfo'>localhost</p>")

#        if ("schema.org" not in os_host and sitemode == "mainsite"):
#            self.write("<p id='offsite_note' class='layerinfo'>in schema.org mode but offsite</p>")


        cached = self.GetCachedText(node, layers)
        if (cached != None):
            self.response.write(cached)
            return

        self.parentStack = []
        self.GetParentStack(node, layers=layers)

        self.UnitHeaders(node,  layers=layers)

        if (node.isClass(layers=layers)):
            subclass = True
            for p in self.parentStack:
                self.ClassProperties(p, p==self.parentStack[0], layers=layers)
            self.write("</table>\n")
            self.ClassIncomingProperties(node, layers=layers)
        elif (Unit.isAttribute(node, layers=layers)):
            self.AttributeProperties(node, layers=layers)

        if (not Unit.isAttribute(node, layers=layers)):
            self.write("\n\n</table>\n\n") # no supertype table for properties

        if (node.isClass(layers=layers)):
            children = sorted(GetSources(Unit.GetUnit("rdfs:subClassOf"), node, layers=layers), key=lambda u: u.id)
            if (len(children) > 0):
                self.write("<br/><b>More specific Types</b>");
                for c in children:
                    self.write("<li> %s" % (self.ml(c)))

        if (node.isEnumeration(layers=layers)):
            children = sorted(GetSources(Unit.GetUnit("typeOf"), node, layers=layers), key=lambda u: u.id)
            if (len(children) > 0):
                self.write("<br/><br/>Enumeration members");
                for c in children:
                    self.write("<li> %s" % (self.ml(c)))

        ackorgs = GetTargets(Unit.GetUnit("dc:source"), node, layers=layers)
        if (len(ackorgs) > 0):
            self.write("<h4  id=\"acks\">Acknowledgements</h4>\n")
            for ao in ackorgs:
                acks = sorted(GetTargets(Unit.GetUnit("rdfs:comment"), ao, layers))
                for ack in acks:
                    self.write(str(ack+"<br/>"))

        examples = GetExamples(node, layers=layers)
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
                    self.write("    <a value='%s' data-selects='%s' class='%s'>%s</a>\n"
                               % (example_type, example_type, selected, label))
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

        if ENABLE_CORS:
            self.response.headers.add_header("Access-Control-Allow-Origin", "*") # entire site is public.

#        TODO: redirections - https://github.com/rvguha/schemaorg/issues/4
#        or https://webapp-improved.appspot.com/guide/routing.html?highlight=redirection
#
#        if str(self.request.host).startswith("www.schema.org"):
#            log.debug("www.schema.org requested. We should redirect to use schema.org as hostname, not " + self.request.host)
#            origURL = self.request.url
#            origURL.replace("https://", "http://")
#            origURL.replace("//www.schema.org", "//schema.org")
#            self.redirect(newURL, permanent=True)

        if (node == "favicon.ico"):
            return

        # Identify which extension layer(s) are requested
        # TODO: add subdomain support e.g. bib.schema.org/Globe
        # instead of Globe?ext=bib which is more for debugging.
        #
        extlist = self.request.get("ext")
        extlist = re.sub(ext_re, '', extlist).split(',')
        log.debug("Extension list: %s " % ", ".join(extlist))
#        layerlist = ["core", "bib"]
        layerlist = [ "core"]

        if host_ext != None:
            log.info("Host: %s host_ext: %s" % ( os_host , host_ext ) )
            extlist.append(host_ext)
            #host_ext = host_ext.group(1)

        for x in extlist:
            log.info("Ext filter found: %s" % str(x))
            if x  in ["core", "localhost", ""]:
                continue
            layerlist.append("%s" % str(x))
        layerlist = list(set(layerlist))
        log.info("layerlist: %s" % layerlist)

        sitename = self.getExtendedSiteName(layerlist)


        # First: fixed paths: homepage, and generated JSON-LD files.
        #
        if (node == "" or node=="/"):
            self.getHomepage(node)
            return

        if ENABLE_JSONLD_CONTEXT:
            if (node=="docs/jsonldcontext.json.txt"):
                jsonldcontext = GetJsonLdContext()
                self.response.headers['Content-Type'] = "text/plain"
                self.emitCacheHeaders()
                self.response.out.write( jsonldcontext )
                return
            if (node=="docs/jsonldcontext.json"):
                jsonldcontext = GetJsonLdContext()
                self.response.headers['Content-Type'] = "application/ld+json"
                self.emitCacheHeaders()
                self.response.out.write( jsonldcontext )
                return

        if (node == "docs/full.html"): # DataCache.getDataCache.get
            self.response.headers['Content-Type'] = "text/html"
            self.emitCacheHeaders()

            if DataCache.get('FullTreePage'):
                self.response.out.write( DataCache.get('FullTreePage') )
                log.debug("Serving cached FullTreePage.")
                return
            else:
                template = JINJA_ENVIRONMENT.get_template('full.tpl')
                uThing = Unit.GetUnit("Thing")
                uDataType = Unit.GetUnit("DataType")

                mainroot = TypeHierarchyTree()
                mainroot.traverseForHTML(uThing, layers=layerlist)
                thing_tree = mainroot.toHTML()

                dtroot = TypeHierarchyTree()
                dtroot.traverseForHTML(uDataType, layers=layerlist)
                datatype_tree = dtroot.toHTML()

                template_values = {
                    'thing_tree': thing_tree,
                    'datatype_tree': datatype_tree,
                }

                page = template.render(template_values)

                self.response.out.write( page )
                log.debug("Serving fresh FullTreePage.")
                DataCache["FullTreePage"] = page

                return

        if (node == "docs/tree.jsonld"):
            self.response.headers['Content-Type'] = "application/ld+json"
            self.emitCacheHeaders()

            if DataCache.get('JSONLDThingTree'):
                self.response.out.write( DataCache.get('JSONLDThingTree') )
                log.debug("Serving cached JSONLDThingTree.")
                return
            else:
                uThing = Unit.GetUnit("Thing")
                mainroot = TypeHierarchyTree()
                mainroot.traverseForJSONLD(Unit.GetUnit("Thing"), layers=layerlist)
                thing_tree = mainroot.toJSON()
                self.response.out.write( thing_tree )
                log.debug("Serving fresh JSONLDThingTree.")
                DataCache["JSONLDThingTree"] = thing_tree

                return

        # Next: pages based on request path matching a Unit in the term graph.

        node = Unit.GetUnit(node) # e.g. "Person", "CreativeWork".

        # TODO:
        # - handle http vs https; www.schema.org vs schema.org
        # - handle foo-input Action pseudo-properties
        # - handle /Person/Minister -style extensions

        if inLayer(layerlist, node):
            self.getExactTermPage(node, layerlist)
            return
        else:
            # log.info("Looking for node: %s in layers: %s" % (node.id, ",".join(all_layers.keys() )) )
            if node is not None and node.id in all_terms:# look for it in other layers
                log.info("TODO: layer toc: %s" % all_terms[node.id] )
                # self.response.out.write("Layers should be listed here. %s " %  all_terms[node.id] )
                self.response.out.write("<h3>Schema.org Extensions</h3>\n<p>The term '%s' is not in the schema.org core, but is described by the following extension(s):</p>\n<ul>\n" % node.id)
                for x in all_terms[node.id]:
                    x = x.replace("#","")
                    self.response.out.write("<li><a href='?ext=%s'>%s</a>" % (x, x) )

            else:
              self.error(404)
              self.response.out.write('<title>404 Not Found.</title><a href="/">404 Not Found.</a><br/><br/>')
              self.response.out.write("<br /><br /><br /><br /><br /><!-- %s -->" % ",".join(layerlist))
              return

read_schemas()
schemasInitialized = True

app = ndb.toplevel(webapp2.WSGIApplication([("/(.*)", ShowUnit)]))
