'''
Created on Jun 6, 2012
Original Code : retirever-mulit.py can be found at link http://pycurl.cvs.sourceforge.net/pycurl/pycurl/examples/retriever-multi.py?view=markup
posted on pycurl sourceforge site for examples
@author: ashwani
'''
#
import urllib
import pycurl
import StringIO
from bs4 import BeautifulSoup
import os
import html5lib
import urlparse

# We should ignore SIGPIPE when using pycurl.NOSIGNAL - see
# the libcurl tutorial for more info.


import re
import codecs
def getlinks(htmldoc , currentlink, parentdomain):
    """
    This function returns all the links in the html doc such that
    the links belong the parent domain given.
    beautifulsoup returns url in unicode format.
    Need to conver it into string class with proper encoding.
    
    """
   # print 'current ', currentlink
    if htmldoc is None or len(htmldoc) <= 0:
        return []
    try:
        soup = BeautifulSoup(htmldoc,'html5lib')
    except TypeError:
#       print 'curlcrawl.py:getlinks <weird htmlcontent> :',' ', htmldoc
       return []
   # print soup
    result = list()
    links = soup.find_all('a')
    for link in links:
        link = link.get('href')
        if link is None:
            continue
        ln = link.encode('utf-8')
        relativepath = re.compile('^[.][.]/.+')
        if relativepath.match(ln):
            #print 'adding relative apt ' ,ln
            result.append(currentlink+'/'+urllib.quote(ln))
            continue 

        absolutepath = re.compile('^/.+')
        if absolutepath.match(ln):
            #print 'adding absolute apt ' ,ln
            result.append(parentdomain+urllib.quote(ln))
            continue

        absolutename = re.compile('^[^:]+$')
        if absolutename.match(ln):
           #print 'adding absolute name ' ,ln
           result.append(parentdomain+'/'+urllib.quote(ln))
           continue  
        
        parsedurl = urlparse.urlparse(parentdomain)
        netloc = None
        if parsedurl.netloc == '':
            netloc = '((://)|(www[s]?[.]))'+parsedurl.path.replace('.','[.]')
        else:
            netloc = '://'+  parsedurl.netloc.replace('.','[.]')
        fullcheck = re.compile(netloc+'.+')
        if fullcheck.search(ln):
           #print ' adding full searhc', ' ', ln
           result.append(urllib.quote(ln,':/')) 
  
    return result
class urlbuffer:
    def __init__(self, dumpdir , url, mode, preservepath=False):
        self.dumpdir = dumpdir
        self.url = url
        self.mode = mode
        self.preservepath = preservepath
        self.fullpath = None
       # self.writeobject = StringIO.StringIO()

    def creatediskspace(self):
        if self.dumpdir is None:
            return
        parsedurl = urlparse.urlparse(self.url)
        if self.preservepath:
            path = parsedurl.path.strip()
        else:
            path = parsedurl.path.replace('/','')
        if path == '' or path == '/':
            path = 'base.html'
 
        if path[-1] == '/':
            path = path[:-1]

        self.fullpath = unicode(self.dumpdir)+unicode('/')+path
        try:
            os.makedirs(os.path.dirname(self.fullpath),self.mode)
        except:
            pass
            
               
    def write(self,buff):
        if self.dumpdir is None:
            print buff
            return
        if self.fullpath is None:
            self.creatediskspace()            
        fhandle = codecs.open(self.fullpath, encoding='utf-8',mode='ab',errors='ignore')
        fhandle.write(unicode(buff, encoding="utf-8", errors="ignore"))
        fhandle.close()
  
    def getvalue(self):
        if self.fullpath is not None:
            return codecs.open(self.fullpath,encoding="utf-8").read()
        return None    
    def dumpcontent(dirName , url, htmlcontent ,  mode , preservepath=False ):
        # print url
        parsedurl = urlparse.urlparse(url)

        if preservepath:
            path = parsedurl.path.strip()
        else:
            path = parsedurl.path.replace('/','')
 
        if path == '' or path == '/':
            path = 'base.html'
 
        if path[-1] == '/':
            path = path[:-1]
#    print path
        fullpath = unicode(dirName)+unicode('/')+unicode(path,'utf-8','ignore')
        try:
            os.makedirs(os.path.dirname(fullpath), mode)
        except:
            pass
        try:
            fhandle = codecs.open(fullpath, encoding='utf-8',mode='ab')
            fhandle.write(htmlcontent)
            fhandle.close()
        except:
            return
        
     
        
    
def curlcrawl(urls,  num_conn=1 , maxlink=100,dumpdir = None , mode=0750):
    """    
    crawl a list of sites. 
OA    this function contains urlmap dict which we keeps on growing.
    Ideally there should be very limited amount of urls.
    This method cause memory to bloat. Need to improve upon this.
    """

    totalfetched = 0
    try:
        import signal
        from signal import SIGPIPE, SIG_IGN
        signal.signal(signal.SIGPIPE, signal.SIG_IGN)
    except ImportError:
        pass
    queue = []
    # urlmap will keep on growing so we need to call this functon with better strcuture
    
    urlmap = dict()
    linkcounts = dict()
    globalbuffer = dict()
    for url in urls:
        url = url.strip()
        if not url:
            continue
        queue.append(url )
        linkcounts[urlparse.urlparse(url).netloc] = 0
        urlmap[url] = urlparse.urlparse(url).netloc
    
#    print queue
    num_urls = len(queue)
    num_conn = min(num_conn, num_urls)

    assert 1 <= num_conn <= 10000, "invalid number of concurrent connections"  
    m = pycurl.CurlMulti()
    m.handles = []
    
    for i in range(num_conn):
        c = pycurl.Curl()
        c.fp = None
        c.setopt(pycurl.FOLLOWLOCATION, 1)
        c.setopt(pycurl.MAXREDIRS, 5)
        c.setopt(pycurl.CONNECTTIMEOUT, 30)
        c.setopt(pycurl.TIMEOUT, 300)
        c.setopt(pycurl.NOSIGNAL, 1)
        m.handles.append(c)
        
    freelist = m.handles[:]
    num_processed = 0
    while num_processed < num_urls:
    # If there is an url to process and a free curl object, add to multi stack
        while queue and freelist:
            url = queue.pop(0)
            c = freelist.pop()
#            globalbuffer[url] = StringIO.StringIO()
            globalbuffer[url] = urlbuffer(dumpdir, url, mode)
            c.fp = globalbuffer[url].write
           # print url
            c.setopt(pycurl.URL,url.encode('utf-8'))
            
            # in following use WRITE_FUNC to write the data STORE use from StringIO import StringIO
            c.setopt(pycurl.WRITEFUNCTION, c.fp)
        #    print 'adding url ', ' ', url
            m.add_handle(c)
            # store some info
            c.url = url
        # Run the internal curl state machine for the multi stack
        while 1:
            ret, num_handles = m.perform()
            if ret != pycurl.E_CALL_MULTI_PERFORM:
                break
        # Check for curl objects which have terminated, and add them to the freelist
        while 1:
            # numq is the number of messages still queued
            num_q, ok_list, err_list = m.info_read()
            for c in ok_list:
                c.fp = None
                m.remove_handle(c)
                eurl =  c.getinfo(pycurl.EFFECTIVE_URL)
                parent =  urlmap[c.url]
                freelist.append(c)
 
                if linkcounts[parent] > maxlink:
                    htmlc = None
                links = getlinks(globalbuffer[c.url].getvalue() , eurl,
                                 parent)
             #   print 'gt links' + len(links)
            #    if dumpdir is not None:
                     
                for link in links:
                    if linkcounts[parent] <= maxlink and urlmap.get(link) is None:
                        queue.append(link)
                        urlmap[link] = parent
                        num_urls = num_urls +1
                        linkcounts[parent] = linkcounts[parent] + 1
                totalfetched = totalfetched + 1
         #       print 'fetched ', ' ', eurl
            
            for c, errno, errmsg in err_list:
                c.fp = None
                m.remove_handle(c)
 #               print "Failed: ", c.url, errno, errmsg 
                freelist.append(c)
            num_processed = num_processed + len(ok_list) + len(err_list)
            if num_q == 0:
                break
        # Currently no more I/O is pending, could do something in the meantime
        # (display a progress bar, etc.).
        # We just call select() to sleep until some more data is available.
        m.select(1.0)
    for c in m.handles:
        if c.fp is not None:
            c.fp = None
            c.close()
    m.close()
    return totalfetched
