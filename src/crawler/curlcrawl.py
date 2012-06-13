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
import urlparse
# We should ignore SIGPIPE when using pycurl.NOSIGNAL - see
# the libcurl tutorial for more info.


import re

def getlinks(htmldoc , currentlink, parentdomain):
    """
    This function returns all the links in the html doc such that
    the links belong the parent domain given.
    beautifulsoup returns url in unicode format.
    Need to conver it into string class with proper encoding.
    
    """
#    print 'current ', currentlink
    if htmldoc is None:
        return []
    soup = BeautifulSoup(htmldoc)
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

def dumpcontent(dirName , url, htmlcontent , mode ):
    #print url
    parsedurl = urlparse.urlparse(url)
    path = parsedurl.path
    if parsedurl.path == '' or parsedurl.path == '/':
        path = 'base.html'
    fullpath = dirName+'/'+path
    try:
        os.makedirs(os.path.dirname(fullpath), mode)
    except:
        pass
    try:
        fhandle = open(fullpath, 'wb')
        fhandle.write(htmlcontent)
        fhandle.close()
    except:
        return
        
     
        
    
def curlcrawl(urls,  num_conn=1 , maxlink=100,dumpdir = None , mode=750):
    """    
    crawl a list of sites. 
    this function contains urlmap dict which we keeps on growing.
    Ideally there should be very limited amount of urls.
    This method cause memory to bloat. Need to improve upon this.
    """
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
    
    print queue
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
            globalbuffer[url] = StringIO.StringIO()
            c.fp = globalbuffer[url].write
           # print url
            c.setopt(pycurl.URL,str(url))
            
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
                htmlc = globalbuffer[c.url].getvalue()
                #linkcounts[parent] = linkcounts[parent] + 1
                
                if dumpdir is not None:
                    dumpcontent(dumpdir,  eurl,htmlc, mode )
                globalbuffer[c.url].truncate(0)
                globalbuffer[c.url] = None
                freelist.append(c)
 
                if linkcounts[parent] > maxlink:
                    htmlc = None
                links = getlinks(htmlc , eurl,
                                 parent)
                
            #    if dumpdir is not None:
                     
                for link in links:
                    if linkcounts[parent] <= maxlink and urlmap.get(link) is None:
                        queue.append(link)
                        urlmap[link] = parent
                        num_urls = num_urls +1
                        linkcounts[parent] = linkcounts[parent] + 1

#                print 'fetched ', ' ', eurl
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
