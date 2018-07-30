import logging
logging.basicConfig(level=logging.INFO) # dev_appserver.py --log_level debug .
log = logging.getLogger(__name__)

import io
import threading


from google.appengine.api import app_identity
from google.appengine.api import mail
def sdo_send_mail(to=None,subject=None,msg=None):
    if not to:
        log.error("No mail recipient!")
        return
    if not subject:
        subject = "Infomation from " + app_identity.get_application_id()
    if not msg:
        msg = "Empty message"
    sender = 'manager@{}.appspotmail.com'.format(app_identity.get_application_id())
    log.info("sdo_send_mail To: %s From: %s Subject: %s Msg: %s" % (to,sender,subject,msg))
    mail.send_mail(sender=sender,to=to,subject=subject,body=msg)
    
# Wrap io.SringIO to ensure that all things written are of type unicode
class sdoStringIO(io.StringIO):
    
    def write(self,s):
        if isinstance(s,str):
            s = s.decode('utf-8')
            
        if not isinstance(s,unicode):
            s = unicode(s)
            
        ret = super(sdoStringIO,self).write(s)
        return ret
        
#On thread varible storage        
ThreadVars = threading.local()
def getAppVar(var):
    ret = getattr(ThreadVars, var, None)
    #log.debug("got var %s as %s" % (var,ret))
    return ret

def setAppVar(var,val):
    #log.debug("Setting var %s to %s" % (var,val))
    setattr(ThreadVars,var,val)

CLOUDSTAT = "CloudStat"
CLOUDEXTRAMETA = "CloudExtraMeta"



