# [START imports]
import logging
logging.basicConfig(level=logging.INFO) # dev_appserver.py --log_level debug .
log = logging.getLogger(__name__)
import traceback        

import os
import datetime, time
import cloudstorage
import mimetypes
import StringIO
import json

from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers

from testharness import *
from sdoutil import *

if not getInTestHarness():
    from google.appengine.api import app_identity

# [START retries]
cloudstorage.set_default_retry_params(
    cloudstorage.RetryParams(
        initial_delay=0.2, max_delay=5.0, backoff_factor=2, max_retry_period=15
        ))
# [END retries]
BUCKETROOT = "sdoapp"
DEFAULTCURRENT = "TestData"
CLOUDCACHEENABLE = False
CLOUDAUTOAPPENDHTMLEXT = False

class StoreLocation():
    def __init__(self):
        self.intitialise()
        
    def intitialise(self):
        self.root = BUCKETROOT
        self.current = self._findCurrent()
        
    def _findCurrent(self):
        
        if not getInTestHarness():
            from google.appengine.api.modules.modules import get_current_version_name
            ret = get_current_version_name()
        
        if ret:
            return ret
        
        return DEFAULTCURRENT
        
    def getRoot(self):
        return self.root
    
    def getCurrentLoc(self):
        return self.current
        
    def locate(self,path=""):
        ret = self.getRoot() + "/" + self.getCurrentLoc()
        if path and len(path):
            ret += '/' + path
        return ret
        
    def checkConfig(self):
        changed = False
        prev = self.current
        new = self._findCurrent()
        if new != prev:
            changed = True
            self.current = new
        return changed
        
            
        

STORELOC = StoreLocation()

class bucketCacheItem():
    def __init__(self,stat=None,content=None):
        self.stat = stat
        self.content = content
    
class SdoCloudStore():
    def __init__(self):
        if getInTestHarness():
            self.bucket_name = os.environ.get('BUCKET_NAME',"app_default_bucket")
        else:
            self.bucket_name = os.environ.get('BUCKET_NAME', app_identity.get_default_gcs_bucket_name())
            
        log.info("Storage Bucket: %s" % self.bucket_name)
        self.cleanCache()
#        self.cleanCache()
#        self.bucket_name = "sdo-rjwtest.appspot.com"
#        self.storageClient =  cloudstorage.Client()
#        self.bucket = self.storageClient.bucket(self.bucket_name)
    
        
    def buildNameType(self,filename,ftype):
        dataext = os.path.splitext(filename)
        ext =  dataext[1]
        if ext and len(ext) and ext.startswith('.'):
            ext = ext[1:]
        if ftype and ext != ftype:
            if ftype != "html" or CLOUDAUTOAPPENDHTMLEXT:
                filename = filename + '.' + ftype
            
        #log.info("buildNameType: filename:%s ftype: %s  ext: %s" % (filename, ftype, ext))
                    
        return filename
        
    def buildBucketFile(self,filename,ftype,location):
        #log.info("buildBucketFile( %s %s %s )" % (filename,ftype,location))
        
        filename = self.buildNameType(filename,ftype)
        
        if not location:
            if ftype:
                location = ftype
        if location:        
            bucketFile = location + "/" + filename
        else:
            bucketFile = filename

        mimetype, contentType = mimetypes.guess_type(bucketFile)
        
        if not mimetype and ftype == "html":
            mimetype = "text/html"

        #log.info("buildBucketFile: %s %s (%s)" % (bucketFile,mimetype,contentType))

        return bucketFile, mimetype
        
    def getPath(self,bucketFile):
        bucketFile = "/" + self.bucket_name + "/" + STORELOC.locate(bucketFile)
        return bucketFile
        
        
# [START write]
    def writeFormattedFile(self, filename, ftype=None, location=None, content="", raw=False, private=False, extrameta=None):
        """Create a file."""
        bucketFile, mtype  = self.buildBucketFile(filename,ftype,location)
        if ftype != 'html':
            raw = True
        self.write_file(bucketFile, mtype, content, raw=raw, private=private, extrameta=extrameta)

    def write_file(self, bucketFile, mtype=None, content="", raw=False, private=False, extrameta=None):
        """Create a file."""

        log.info('Creating file {} ({})'.format(bucketFile,mtype))
        bucketFile = self.getPath(bucketFile)
        return self._write_file(bucketFile=bucketFile, mtype=mtype, content=content, raw=raw, private=private, extrameta=extrameta)

    def _write_file(self, bucketFile, mtype=None, content="", raw=False, private=False, extrameta=None):
        log.info("Attempting to write: %s %s %s" % (bucketFile, mtype, raw))
        # The retry_params specified in the open call will override the default
        # retry params for this particular file handle.

        setAppVar(CLOUDSTAT,None)
        moremeta = getAppVar(CLOUDEXTRAMETA)
        setAppVar(CLOUDEXTRAMETA,None) #clear out now potentially stale values
        
        if extrameta and moremeta:
            extrameta.update(moremeta)
        else:
            extrameta = moremeta

        try:
            write_retry_params = cloudstorage.RetryParams(backoff_factor=1.1)
            write_options = {}
            if not private:
                write_options.update({'x-goog-acl': 'public-read'})
            if extrameta:
                write_options.update(extrameta)
            if private:
                write_options=""
            if not raw:
                log.info("Encoding to utf8")
                content = content.encode('utf-8')
            with cloudstorage.open(
                    bucketFile, 'w',
                    content_type=mtype,
                    options=write_options,
                    retry_params=write_retry_params) as cloudstorage_file:
                        cloudstorage_file.write(content)
        except Exception as e:
            log.error("File write error: (%s): %s" % (bucketFile,e))
            log.error(traceback.format_exc())
            return False
        
        setAppVar(CLOUDSTAT,self._stat_file(bucketFile,cache=False))
        return True

    def write_json_file(self, bucketFile, mtype="application/json", data={}, private=False):
        """Create a file."""
        
        bucketFile = self.getPath(bucketFile)
        return self._write_json_file(bucketFile=bucketFile, mtype=mtype, data=data, private=private)


    def _write_json_file(self, bucketFile, mtype="application/json", data={}, private=False):
        # The retry_params specified in the open call will override the default
        # retry params for this particular file handle.
        log.info("Attempting to write: %s" % bucketFile)
        try:
            write_retry_params = cloudstorage.RetryParams(backoff_factor=1.1)
            write_options = {'x-goog-acl': 'public-read'}
            if private:
                write_options=""
            with cloudstorage.open(
                bucketFile, 'w',
                    content_type=mtype,
                    options=write_options,
                    retry_params=write_retry_params) as cloudstorage_file:
                        json.dump(data,cloudstorage_file)
        except Exception as e:
            log.info("File write error: (%s): %s" % (bucketFile,e))
            return False
        return True
                    
# [END write]

# [START stat]
    def statFormattedFile(self, filename, ftype="html", location=None, cache=True):
        log.info("statFormattedFile(%s,%s,%s,%s)" % (filename, ftype, location, cache))
        bucketFile, mtype  = self.buildBucketFile(filename,ftype,location)
        return self.stat_file(bucketFile, ftype, cache)
        
    def stat_file(self, bucketFile, ftype=None, cache=True):
        bucketFile = self.getPath(bucketFile)
        return self._stat_file(bucketFile, ftype=ftype, cache=cache)

    def _stat_file(self, bucketFile, ftype=None, cache=True):
        log.info("_stat_file(%s,%s,%s)" % (bucketFile, ftype, cache))
        ret = None
        if cache:
            item = self.readCache(bucketFile,ftype)
            if item:
                ret = item.stat
                log.info("Got from readCache")
            
        if not ret:
            #log.info('Stating file {}'.format(bucketFile))
            try:
                ret = cloudstorage.stat(bucketFile)
            except cloudstorage.NotFoundError:
                log.info("File not found: %s" % bucketFile)
            except Exception as e:
                log.info("Stat error(%s): %s" % (bucketFile,e))

            if ret:
                log.info("Stat {}".format(ret))
                itm = bucketCacheItem(ret,None)
                self.writeCache(bucketFile, itm, ftype)
        return ret

# [END stat]

# [START read]
    def readFormattedFile(self, filename, ftype="html", location=None, cache=True):
        log.info("readFormattedFile(%s,%s,%s,%s)" % (filename,ftype,location,cache))
        stat, content = self.getFormattedFile(filename, ftype, location, cache)
        return content

    def read_file(self, bucketFile, cache=True, stat=None):
        log.info("read_file(%s,%s,%s)" % (bucketFile,cache,stat))
        stat, content = self.get_file(bucketFile,cache,stat)
        return content
        
        
    def getFormattedFile(self, filename, ftype="html", location=None, cache=True):
        log.info("getFormattedFile(%s,%s,%s,%s)" % (filename,ftype,location,cache))

        bucketFile, mtype  = self.buildBucketFile(filename,ftype,location)
        stat, content = self.get_file(bucketFile,reqtype=ftype, cache=cache)
        return stat, content
        
    def get_file(self, bucketFile, reqtype=None, cache=True):
        bucketFile = self.getPath(bucketFile)
        return self._get_file(bucketFile=bucketFile, reqtype=reqtype, cache=cache)


    def _get_file(self, bucketFile, reqtype=None, cache=True):
        log.info("_get_file(%s,%s)" % (bucketFile,cache))

        setAppVar(CLOUDSTAT,None)
        
        stat = None
        content = None
        cached = False
        if cache:
            item = self.readCache(bucketFile,reqtype)
            if item:
                content = item.content
                stat = item.stat
                if content:
                    cached = True
                    log.info("Got from readCache")
                    
        if not stat:
            stat = self._stat_file(bucketFile,cache=False)
            if stat:
                log.info('Opening file {}'.format(bucketFile))
                try:
                    with cloudstorage.open(bucketFile) as cloudstorage_file:
                        content = cloudstorage_file.read()
                        cloudstorage_file.close()
                        
                except cloudstorage.NotFoundError:
                    log.info("File not found: %s" % bucketFile)
                except Exception as e:
                    log.info("File read error (%s): %s" % (bucketFile,e))
                    
        if not cached and content:
            log.info("Adding to cache: %s" % bucketFile)
            val = bucketCacheItem(stat=stat,content=content)
            self.writeCache(bucketFile,val, reqtype) 

        setAppVar(CLOUDSTAT,stat)
        return stat, content
        
    def delete_file(self, bucketFile, ftype=None):
        bucketFile = self.getPath(bucketFile)
        return _delete_file(bucketFile=bucketFile, ftype=ftype)
        
    def _delete_file(self, bucketFile, ftype=None):
        log.info("Deleting: %s" % bucketFile)
        self.delCache(bucketFile, ftype)
        try:
              cloudstorage.delete(bucketFile)
        except cloudstorage.NotFoundError:
          pass
            
    def get_json_file(self, bucketFile):
        log.info("get_json_file(%s)" % (bucketFile))
        data = None
        stat = self.stat_file(bucketFile,cache=False)
        if stat:
            log.info('Opening file {}'.format(self.getPath(bucketFile)))
            try:
                with cloudstorage.open(self.getPath(bucketFile)) as cloudstorage_file:
                    data = json.load(cloudstorage_file)
                    cloudstorage_file.close()
            except cloudstorage.NotFoundError:
                log.info("File not found: %s" % self.getPath(bucketFile))
            except Exception as e:
                log.info("File read error (%s): %s" % (bucketFile,e))
        return data
            
    def cleanCache(self,reqtype=None):
        self.cache = {}
        
    def emptyCache(self,reqtype):
        log.info("Emptying cache for %s" % reqtype)
        if not reqtype:
            self.cache = {}
        else:
            self.cache[reqtype] = {}
            
    def readCache(self, index, reqtype=None):
        if not CLOUDCACHEENABLE:
            return None
            
        if not reqtype:
            reqtype = "unknown"
        
        ctype = self.cache.get(reqtype)
        if ctype:
            return ctype.get(index)
        return None
        
    def writeCache(self, index, value, reqtype=None):
        if not CLOUDCACHEENABLE:
            return
            
        if not reqtype:
            reqtype = "unknown"

        ctype = self.cache.get(reqtype)
        if not ctype:
            ctype = {}
            self.cache[reqtype] = ctype
        ctype[index] = value
        
    def delCache(self, index, reqtype=None):
        if not CLOUDCACHEENABLE:
            return

        if not reqtype:
            reqtype = "unknown"
        ctype = self.cache.get(reqtype)
        if ctype:
            ctype.pop(index,None)
        
            
# [END read]

# [START delete_file]
    def deleteFormattedFile(self, filename, ftype="html", location=None ):
        bucketFile, mtype  = self.buildBucketFile(filename,ftype,location)
        self.delete_file(bucketFile,ftype)
        
    def delete_file(self,bucketFile,ftype=None):
        log.info('Deleting file {}'.format(bucketFile))
        self.delCache(bucketFile,reqtype=ftype)
        self._delete_file(self.getPath(bucketFile))
        
    def _delete_file(self, file):
        try:
            cloudstorage.delete(file)
        except cloudstorage.NotFoundError:
            log.info("File not found: %s" % file)
            pass

# [END delete_file]

# [START delete_files]

    def delete_files_in_bucket(self,skip = []):
        return self.delete_files_in_folder("",skip)
        
    def delete_files_in_folder(self, folder, skip=[]):
        bucketFolder = self.getPath(folder)
        log.info("bucketFolder %s" % bucketFolder)
        startdel = datetime.datetime.now()
        delcount = 0
        page_size = 100
        stats = cloudstorage.listbucket(bucketFolder, max_keys=page_size)
        files = []
        while True:
            count = 0
            for stat in stats:
                count += 1
                fname = stat.filename
                delete = True
                if skip:
                    for s in skip:
                        if s in fname:
                            delete = False
                            log.info("SKIPPING: %s" % fname)
                            break
                if delete:
                    files.append(stat.filename)
                
            for f in files:
                delcount += 1
                self._delete_file(f)

            if count != page_size or count == 0:
                break
            stats = cloudstorage.listbucket(bucketFolder, max_keys=page_size,marker=stat.filename)
            files = []
        
        log.info("Cloudstorage: deleted %s files in %s seconds" % (delcount, (datetime.datetime.now() - startdel)))
        return delcount

# [END delete_files]


SdoCloud = SdoCloudStore()

        
    

               
            
        
        
        

