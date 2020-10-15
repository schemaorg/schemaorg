#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import sys
if not (sys.version_info.major == 3 and sys.version_info.minor > 5):
    print("Python version %s.%s not supported version 3.6 or above required - exiting" % (sys.version_info.major,sys.version_info.minor))
    sys.exit(1)

import os
import argparse
for path in [os.getcwd(),"util"]:
  sys.path.insert( 1, path ) #Pickup libs from local  directories

from flask import Flask, render_template,after_this_request
import re
from schemaversion import getVersion


parser = argparse.ArgumentParser()
parser.add_argument("--host", default="localhost", help="Host (default: localhost)")
parser.add_argument("--port", default=8080, help="Port (default: 8080")
args = parser.parse_args()


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

@app.route('/version/<ver>')
@app.route('/version/<ver>/')
@app.route('/version/<ver>/<path>')
def serve_downloads(ver,path=""):
    if ver == "latest":
        ver = getVersion()
    if not len(path):
        path="schema-all.html"
    path = "releases/%s/%s" % (ver,path) 
    print("Serving file: " + path)
    return app.send_static_file(path)

# start the server with the 'run()' method
if __name__ == '__main__':
    print("Local dev server for Schema.org version: %s" % getVersion())
    app.run(host=args.host, port=args.port,debug=True)