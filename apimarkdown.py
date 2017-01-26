import markdown2
from markdown2 import Markdown
import re
import threading
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
    
    def setPre(self,pre="/"):
        self.wpre = pre
        
    def setPost(self,post=""):
        self.wpost = post
        
    def parse(self,source,preservePara=False):
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
        
        return self.parseWiklinks(ret)
    
    def parseWiklinks(self,source):
        return re.sub(WIKILINKPATTERN, self.wikilinkReplace, source)
        
    def wikilinkReplace(self,match):
        t = match.group(1)
        return '<a class="%s" href="%s%s%s">%s</a>' % (self.wclass,self.wpre,t,self.wpost,t)
        

Markdown = MarkdownTool()
