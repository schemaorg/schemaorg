#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import sys
if not (sys.version_info.major == 3 and sys.version_info.minor > 5):
    print("Python version %s.%s not supported version 3.6 or above required - exiting" % (sys.version_info.major,sys.version_info.minor))
    sys.exit(1)

import os
for path in [os.getcwd(),"Util","SchemaTerms","SchemaExamples"]:
  sys.path.insert( 1, path ) #Pickup libs from local  directories

import logging
#Suppress WARNING messages from rdflib
logger = logging.getLogger("rdflib.term")
logger.setLevel(level=logging.ERROR)

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-e","--example",default= [],action='append',nargs='*',  help="example to validate(repeatable) - default: all examples")
parser.add_argument("-i","--invalidonly",default=False, action='store_true', help="Only report invalid examples")
parser.add_argument("-s","--sourceoutput",default=False, action='store_true', help="Output invalid example source")
args = parser.parse_args()

EXLIST = []
for ex in args.example:
    EXLIST.extend(ex)



import io
import re
import rdflib
from rdflib.serializer import Serializer
from rdflib.parser import Parser

from pyRdfa import pyRdfa
RDFaProcessor = pyRdfa("")


from schemaexamples import SchemaExamples, Example


def validate():
    COUNT = 0
    ERRORCOUNT = 0

    SchemaExamples.loadExamplesFiles("default")
    print("Loaded %d examples " % (SchemaExamples.count()))

    print("Processing")


    for ex in SchemaExamples.allExamples(sort=True):
        if len(EXLIST) == 0 or ex.getKey() in EXLIST:
            COUNT += 1
            if not validateExample(ex):
                ERRORCOUNT += 1

    print ("Processed %s examples %s invalid" % (COUNT,ERRORCOUNT))

TMPLOCATION= "./tmp"

def tmpfilecreate(data,name=None,prefix="",suffix="",ext=None):
    global TMPLOCATION
    if not name:
        name="tmpfile-%s" % os.getpid()
    if not ext:
        ext = "tmp"
    if TMPLOCATION.startswith('./'):
        TMPLOCATION = os.getcwd() + '/' + TMPLOCATION[2:]
    if not os.path.exists(TMPLOCATION):
        os.makedirs(TMPLOCATION)
    filename = TMPLOCATION + "/" + prefix + name + suffix + "." + ext

    #with open(filename,'w') as w:
        #w.write(data)

    return filename

def validateExample(ex):
    valid = True
    err,source = validateJsonld(ex)
    #err,source = validateRdfa(ex)
    if err:
        valid = False
        print("Validating: %s (entry: %s in file %s)" % (ex.getKey(),ex.getMeta('filepos'),ex.getMeta('file')))
        print(err)
        if args.sourceoutput:
            print(source)
        print()
    elif not args.invalidonly:
        print("Validating: %s" % ex.getKey())
    
    return valid

 
def validateRdfa(ex):
    from colorama import Fore, Back, Style
    global RDFaProcessor
    ret = None
    exGraph = None
    exrdfa = ex.getRdfa()
    exrdfa = exrdfa.strip()
    if len(exrdfa):
        #tmpfile = io.StringIO(exrdfa)
        tmpfile = tmpfilecreate(exrdfa,name=ex.getKey(),prefix="tmp-",ext="rdfa")
        #print(">>> %s" % tmpfile)
        try:    
            
            exGraph = RDFaProcessor.graph_from_source(tmpfile,rdfOutput=True)
            print("%d %d" % (len(exrdfa),len(exGraph)))
        except Exception as e:
            print(e)
            ret = "    RDFa Parse Error: %s" % str(e)
    if ret:
        ret = Fore.RED + ret + Style.RESET_ALL

    return ret, exrdfa


ldscript_match = re.compile('[\s\S]*<\s*script\s+type="application\/ld\+json"\s*>(.*)<\s*\/script\s*>[\s\S]*',re.S)
context_match = re.compile('([\S\s]*"@context"\s*:\s*\[?[\S\s]*")https?:\/\/schema\.org\/?("[\S\s]*)',re.M)
current_context_file = '%s/site/docs/jsonldcontext.jsonld' % os.getcwd()
valid_comments = [re.compile('No JSON-?LD',re.I)]
valid_comments.append(re.compile('This example is in microdata only',re.I))
valid_comments.append(re.compile('No Json example available',re.I))

if not os.path.isfile(current_context_file):
    print("ERROR: jsonldcontext.jsonld file not in site/docs - check site build")
    sys.exit(1)

def validateJsonld(ex):
    from colorama import Fore, Back, Style
    ret = None
    exGraph = rdflib.Graph()
    exjson = ex.getJsonld()
    exjson = exjson.strip()
    if len(exjson):
        jsonmatch = ldscript_match.match(exjson)
        if jsonmatch:
            #extract json from within script tag
            exjson = jsonmatch.group(1).strip()
        while True:
            cmatch = context_match.match(exjson)
            if cmatch:
                tmp = [cmatch.group(1), "file://", current_context_file, cmatch.group(2)]
                exjson = ''.join(tmp)
            else:
                break


        #print(exjson)
 
        try:
            exGraph.parse(data=exjson,format="json-ld",base="http://example.com/%s" % ex.getKey())
        except Exception as e:
            ret = "    JSON-LD Parse Error: %s" % str(e)
    source = '\n'.join(['{:4d}: {}'.format(i, x.rstrip()) for i, x in enumerate(exjson.splitlines(), start=1)])
    if ret: #Possible error
        for c in valid_comments:
            if c.match(exjson):
                ret = None
                break
        
        if ret and len(exjson.split('\n')) == 1:
            ret = "Non-JSON-LD: " + exjson
    if ret:
        ret = Fore.RED + ret + Style.RESET_ALL

    return ret, source


if __name__ == "__main__":
    validate()

