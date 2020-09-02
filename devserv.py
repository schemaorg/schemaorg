#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import sys
import os
for path in [os.getcwd(),"Util"]:
  sys.path.insert( 1, path ) #Pickup libs from local  directories

from flask import Flask, render_template,after_this_request
import re
from schemaversion import getVersion


# create the application object
app = Flask(__name__, static_folder='site', static_url_path='')


    
@app.route('/')
def serve_home():
    @after_this_request
    def add_headers(response):
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Allow-Headers'] = 'Accept'
        response.headers['Access-Control-Allow-Origin'] = '"*"'
        response.headers['Access-Control-Allow-Methods'] = 'GET'
        response.headers['Access-Control-Expose-Headers'] = 'Link'
        response.headers['link'] = '</docs/jsonldcontext.jsonld>; rel="alternate"; type="application/ld+json"'
        return response
    path = 'docs/home.html'
    print("Serving file: " + path)
    return app.send_static_file(path)

@app.route('/favicon.ico')
def serve_favicon():
    path = 'docs/favicon.ico'
    print("Serving file: " + path)
    return app.send_static_file(path)

@app.route('/robots.txt')
def serve_robots():
    path = 'docs/robots-blockall.txt'
    print("Serving file: " + path)
    return app.send_static_file(path)

@app.route('/devnote.css')
def serve_devnote():
    path = 'docs/sitemap.xml_no_serve'
    print("Serving file: " + path)
    return app.send_static_file(path)

@app.route('/sitemap.xml')
def serve_sitemap():
    return app.send_static_file('docs/sitemap.xml_no_serve')
    path = 'docs/favicon.ico'
    print("Serving file: " + path)
    return app.send_static_file(path)

@app.route('/<path>')
def serve_terms(path):
    if not path.endswith(".html"):
        m = re.match("^([a-z])(.*)$",path)
        if m:
            path = "terms/properties/%s/%s%s.html" % (m.group(1),m.group(1),m.group(2))
        else:
            m = re.match("^([0-9A-Z])(.*)$",path)
            if m:
                path = "terms/types/%s/%s%s.html" % (m.group(1),m.group(1),m.group(2))
    
    print("Serving file: " + path)
  
    return app.send_static_file(path)

@app.route('/version/<ver>/<path>')
def serve_downloads(ver,path):
    if ver == "latest":
        ver = getVersion()
    path = "data/releases/%s/%s" % (ver,path) 
    print("Serving file: " + path)
    return app.send_static_file(path)

# start the server with the 'run()' method
if __name__ == '__main__':
    app.run(debug=True)