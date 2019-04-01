import logging
logging.basicConfig(level=logging.INFO) # dev_appserver.py --log_level debug .
log = logging.getLogger(__name__)

import markdown2
from markdown2 import Markdown
import re
import threading
import sdoutil
WIKILINKPATTERN = r'\[\[([\w0-9_ -]+)\]\]'

class MarkdownTool():
    def __init__ (self):
        #from markdown.extensions.wikilinks import WikiLinkExtension
        #self._md = markdown2.Markdown(extensions=[WikiLinkExtension(base_url='/', end_url='', html_class='localLink')])
        self._md = Markdown()
        self.wclass = "localLink"
        self.wpre = "/"
        self.wpost = ""
        self.parselock = threading.Lock() 
    
    def setPre(self,pre="./"):
        self.wpre = pre
        
    def setPost(self,post=""):
        self.wpost = post
        
    def parse(self,source,preservePara=False,wpre=None):
        if not source or len(source) == 0:
            return ""
        source = source.strip()
        source = source.replace("\\n","\n")
    	try:
            self.parselock.acquire()
            ret = self._md.convert(source)
    	finally:
    		self.parselock.release()
        
        if not preservePara:
            #Remove wrapping <p> </p>\n that Markdown2 adds by default
            if len(ret) > 7 and ret.startswith("<p>") and ret.endswith("</p>\n"):
                ret = ret[3:len(ret)-5]
            
            ret = ret.replace("<p>","")
            ret = ret.replace("</p>","<br/><br/>")
            if ret.endswith("<br/><br/>"):
                ret = ret[:len(ret)-10]
        
        return self.parseWiklinks(ret,wpre=wpre)
    
    def parseWiklinks(self,source,wpre=None):
        sdoutil.setAppVar("MKDOWNWPRE",wpre)
        return re.sub(WIKILINKPATTERN, self.wikilinkReplace, source)
        
    def wikilinkReplace(self,match):
        wpre = sdoutil.getAppVar("MKDOWNWPRE")
        if not wpre:
            wpre = self.wpre
        t = match.group(1)
        return '<a class="%s" href="%s%s%s">%s</a>' % (self.wclass,wpre,t,self.wpost,t)
        

Markdown = MarkdownTool()
