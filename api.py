#!/usr/bin/env python
#

import webapp2
from google.appengine.ext import ndb
from google.appengine.ext import blobstore
from google.appengine.api import users
from google.appengine.ext.webapp import blobstore_handlers
import logging
import parsers
import headers

# This is the triple store api.
# We have a number of triple sets. Each is from a user / tag combination


# models

class Triple(ndb.Model):
    source = ndb.StringProperty()
    arc = ndb.StringProperty()
    target = ndb.StringProperty()
    text = ndb.TextProperty()

class TripleSet(ndb.Model):
    user = ndb.StringProperty()
    tag = ndb.StringProperty()
    format = ndb.StringProperty()
    iscurrent = ndb.StringProperty()
    base = ndb.StringProperty()


    def AddTriple(self, source, arc, target):
        if (source == None or arc == None or target == None):
            return
        nts = Triple(parent=self.key)
        nts.source = source
        nts.target = target
        nts.arc = arc
        nts.put_async()
        return nts

    def AddTripleText(self, source, arc, text):
        if (source == None or arc == None or text == None):
            return
        nts = Triple(parent=self.key)
        nts.source = source
        nts.text = text
        nts.arc = arc
        nts.put_async()
        return nts

    def DeleteTripleSet(self):
        found = 1
        while (found == 1):
            q = Triple.query()
            q.ancestor(self.key)
            triples_to_delete = []
            found = 0
            for triple in q.run(limit=1000):
                triples_to_delete.append(triple)
                found = 1
            for tr in triples_to_delete:
                tr.delete_async()
        self.delete_async()

def DeleteAllTriples ():
    q = Triple.query()
    triples_to_delete = []
    for triple in q:
        triples_to_delete.append(triple)
    for tr in triples_to_delete:
        tr.key.delete_async()
    

def GetTripleSet (tstag):
    q = TripleSet.query(TripleSet.tag == tstag)
    logging.info("Tag = " + tstag)
    for ts in q:
        return ts

def GetUserTripleSets (user):
    q = TripleSet.query(TripleSet.user == user)
    logging.info("Tag = " + user)
    tssets = []
    for ts in q:
        tssets.append(ts)
    return tssets


def GetTargets(tripleSet, arc, source):
    q = Triple.query(Triple.source == source, Triple.arc == arc, ancestor = tripleSet.key)
    targets = {}
    for triple in q:
        if (triple.target != None):
            targets[triple.target] = 1
        if (triple.text != None):
            targets[triple.text] = 1
    return targets.keys()

def GetSources(tripleSet, arc, target):
    q = Triple.query(Triple.target == target, Triple.arc == arc, ancestor = tripleSet.key)
    sources = {}
    for triple in q:
        sources[triple.source] = 1
    return sources.keys()

def GetArcsIn(tripleSet, target):
    q = Triple.query(Triple.target == target, ancestor = tripleSet.key)
    arcs = {}
    for triple in q:
        arcs[triple.arc] = 1
    return arcs.keys()

def GetArcsOut(tripleSet, source):
    q = Triple.query(Triple.source == source, ancestor = tripleSet.key)
    arcs = {}
    for triple in q:
        arcs[triple.arc] = 1
    return arcs.keys()

def GetComment(tripleSet, node) :
    q = Triple.query(Triple.source == node, Triple.arc == "rdfs:comment", ancestor = tripleSet.key)
    for triple in q:
        return triple.text
    return "No comment"

class SchemaFileUploadPage (webapp2.RequestHandler):
    def get(self):
        headers.OutputSchemaorgHeaders(self)
        if (users.get_current_user()):
            user = users.get_current_user()
            upload_url = blobstore.create_upload_url('/api/add')
            self.response.out.write('<html><body>')
            self.response.out.write('<form action="%s" method="POST" enctype="multipart/form-data">' % upload_url)
            self.response.out.write("<input type=hidden name=user value=" + user.user_id() + ">  Tag =  <input type=text name=tag> <br>  Base = <input type=text name=base><br>  Format = <select name=format><option value=rdfa>RDFA</a><option value=mcf>MCF</option></select><br>  content <input type=file name=content> <br> <input type=submit> </form> </body></html>")
        else:
            greeting = ("<a href=%s>Please sign in</a>" % users.create_login_url("/api/ap"))
            self.response.out.write(greeting)


class ShowUserSchemas (webapp2.RequestHandler):
    def get(self):
        headers.OutputSchemaorgHeaders(self)
        if (users.get_current_user()):
            user = users.get_current_user()
            self.response.out.write('<html><body>')
            triplesets = GetUserTripleSets(user.user_id())
            if (len(triplesets) == 0):
                self.response.out.write("<br><br>You have not uploaded anything<br><br>")
            for ts in triplesets:
                self.response.out.write("<li> Tag = %s, Base = %s, Format = %s, <a href=/Thing?tag=%s>Thing</a>" % (ts.tag, ts.base, ts.format, ts.tag))
        else:
            greeting = ("<a href=%s>Please sign in</a>" % users.create_login_url("/api/showTripleSets"))
            self.response.out.write(greeting)


class DeleteEverythingHandler (webapp2.RequestHandler) :
    def get(self):
        if (users.get_current_user()):
            user = users.get_current_user()
            if (user == "guha"):
                DeleteAllTriples()
                self.response.out.write('Everything deleted')
            else:
                self.response.out.write("You do not have the rights to do that :(")
        else:
            greeting = ("<a href=%s>Please sign in</a>" % users.create_login_url("/api/showts"))
            self.response.out.write(greeting)


    
#class AddTripleSet(webapp2.RequestHandler):
class AddTripleSet(blobstore_handlers.BlobstoreUploadHandler):

    def ml(self, node):
        return "<a href=/%s?tag=%s>%s</a>" % (node, self.tag, node)


    def post(self):
        user = self.request.get("user")
        tag = self.request.get("tag")
        self.tag = tag
        base = self.request.get("base")
        ft = self.request.get("format")
    #    filename = self.request.get("content")
        upload_files = self.get_uploads()
        content = upload_files[0].open().read()
        ts = TripleSet(user = user, tag = tag, base = base, format = format)
        ts.put()
        parser = parsers.MakeParserOfType(ft, self.response)
        items = parser.parse(content, ts)

        self.response.write("Done")
        for item in items:
            self.response.write("<li> %s" % (self.ml(item)))
    #    self.response.headers['Content-Type'] = 'text/plain'
    #self.response.write("%s %s %s %s %i \n %s" % (user, tag, base, ft, len(upload_files), content))



class ShowUnit (webapp2.RequestHandler) :

    def getParentStack(self, node):
        if (node not in self.parentStack):
            self.parentStack.append(node)
            for p in GetTargets(self.tripleset, "rdfs:subClassOf", node):
                self.getParentStack(p)

    def ml(self, node):
        return "<a href=%s?tag=%s>%s</a>" % (node, self.tag, node)

    def UnitHeaders(self, node):
        self.response.write("<h1 class=page-title>")
        ind = len(self.parentStack)
        while (ind > 0) :
            ind = ind -1
            nn = self.parentStack[ind]
            self.response.write("%s &gt; " % (self.ml(nn)))
        self.response.write("</h1>")
        comment = GetComment(self.tripleset, node)
        self.response.write("<div>%s</div>" % (comment))
        self.response.write("<table cellspacing=3 class=definition-table>        <thead><tr><th>Property</th><th>Expected Type</th><th>Description</th>               </tr></thead>")



    def ClassProperties (self, cl):
        headerPrinted = False 
        for prop in GetSources(self.tripleset, "domainIncludes", cl):
            ranges = GetTargets(self.tripleset, "rangeIncludes", prop)
            comment = GetComment(self.tripleset, prop)
            if (not headerPrinted):
                self.response.write("<thead class=supertype><tr><th class=supertype-name colspan=3>Properties from %s</th></tr></thead><tbody class=supertype" % (self.ml(cl)))
                headerPrinted = True
        
            self.response.write("<tr><th class=prop-nam' scope=row><code>%s</code></th>" % (self.ml(prop)))
            self.response.write("<td class=prop-ect>")
            first_range = True
            for r in ranges:
                if (not first_range):
                    self.response.write("<br>")
                    first_range = False
                self.response.write(self.ml(r))
            self.response.write("</td>")
            self.response.write("<td class=prop-desc>%s</td>" % (comment))
            self.response.write("</tr>")

    def get(self, node):

        if (node == "favicon.ico"):
            return

        self.tag = self.request.get("tag")
        if (self.tag == None):
            self.tag = "TX1"

        headers.OutputSchemaorgHeaders(self)

        self.tripleset = GetTripleSet(self.tag)
        if (self.tripleset == None):
            self.response.write("No such tag : %s" % (self.tag))
            return

        self.parentStack = []
        self.getParentStack(node)

        self.UnitHeaders(node)

        for p in self.parentStack:
            logging.info("Doing " + p)
            self.ClassProperties(p)

        self.response.write("</table>")

        children = GetSources(self.tripleset, "rdfs:subClassOf", node)
        if (len(children) > 0):
            self.response.write("<br>More specific Types");
            for c in children:
                self.response.write("<li> %s" % (self.ml(c)))
                                    

app = ndb.toplevel(webapp2.WSGIApplication([("/api/add", AddTripleSet),
                                            ("/api/ap", SchemaFileUploadPage),
                                            ("/api/deleteEverything", DeleteEverythingHandler),
#                                            ("/api/deleteTripleSet", DeleteTripleSet),
                                            ("/api/showTripleSets", ShowUserSchemas),
                                            ("/(.*)", ShowUnit)]))

