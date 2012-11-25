"""
This script is for parsing text from html pages of websites.
The html pages of a website is downloaded to a directory.
This script goes over each pages and saves the text in a one single file
"""
import codecs
import os 
import sys
from bs4 import BeautifulSoup
from tokenizers import ptbtokenizer 
import urllib2
from urllib2 import HTTPError
from urllib2 import URLError
import mimetypes
import html5lib
class sitecontent:
    """
    Extracted Content of a webpage.
    makesoup call with the filname of the webpage will extract the information.
    Multiple call to makesoup will append the information.
    Webpages are downloaded and saved on physical disk and makesoup does not try 
    to fetch the page through internet.
    """
    def __init__(self, tokenize=True):
        self.title = None
        self.keywords = None
        self.description = None
        self.bodytext = None
        self.tokenize = tokenize

    def getbodytext(self,soup):
        soup = soup.body
        if soup is None:
            return
        for tag in soup.descendants:
            try:
                tag.name
            except AttributeError:
                if tag.parent.name != 'script':
                    content = tag.string
                    if content is not None:
                        if self.tokenize:
                            content  = ptbtokenizer.ptbtokens(content, stem=False, stoplanguage=None, lowercase = False)
                            content = ' '.join(content)
                        self.bodytext = self.bodytext + ' '+ content

    def getheader(self, soup):
        soup = soup.head
        if soup is None:
            return None
        if soup.title:
            content = soup.title.get_text()
            if content is not None:
                if self.tokenize:
                    content = ptbtokenizer.ptbtokens(content, stem= False, stoplanguage=None, lowercase=False)
                    content = ' '.join(content)
                if self.title is None:
                    self.title = content
                else:
                    self.title = self.title + ' ' + content
        kws = soup.find_all("meta", {"name" : "keywords"})

        if len(kws) > 0:
            content  = kws[0].get("content")
            if content is not None:
                if self.tokenize:
                    content = ptbtokenizer.ptbtokens(content, stem= False, stoplanguage=None, lowercase=False)
                    content = ' '.join(content)
                if self.keywords is None:
                    self.keywords = ''
                self.keywords = self.keywords + ' '+ content

        des = soup.find_all("meta", {"name" : "description"})
        if len(des) > 0:
            content = des[0].get('content')
            if content is not None:
                if self.tokenize:
                    content = ptbtokenizer.ptbtokens(content,stem=False, stoplanguage=None, lowercase=False)
                    content = ' '.join(content)
                if self.description is None:
                    self.description = ''
                self.description = self.description + ' '+ content

    
    def makesoup(self, fname):
        ext = mimetypes.guess_type(fname)
        if ext[0] != 'text/html' and ext[0] is not None:
            #print 'not processing ' , fname
            return
        fhandle = codecs.open(fname, encoding='utf-8')
        try:
            soup = BeautifulSoup(fhandle.read(),'html5lib')
            self.getheader(soup)
            self.getbodytext(soup)
        except TypeError:
            pass
        fhandle.close() 

    def soup(self, content):
        try:
            return BeautifulSoup(content,'html5lib')
        except TypeError:
            return None
        
    def dumpondisk(self, todump, docid = None):
        handle = codecs.open(todump,'wb','utf-8',errors='ignore')
        handle.write('<doc>\n')
        if docid is not None:
            handle.write('<docid>\n')
            handle.write(docid.decode('utf-8'))
            handle.write('\n</docid>\n')
        handle.write('<title>\n'+self.title+'\n</title>\n')
        handle.write('<keywords>\n'+self.keywords+'\n</keywords>\n')
        handle.write('<description>\n'+self.description+'\n</description>\n')
        handle.write('<text>\n'+self.bodytext+'\n</text>\n')
        handle.write('</doc>')

    def clear(self):
        self.title = None
        self.keywords = None
        self.description = None
        self.bodytext = None

def parsesites(idir, odir, mode=0750):
    if not os.path.isdir(idir):
        return 
    
     
    if not os.path.isdir(odir):
        os.mkdir(odir,mode)
    count = 0
    for dirpath, dirnames, filenames in os.walk(idir):
        scontent = sitecontent()
        basepath = os.path.basename(dirpath)
        for fh in filenames:
            outfile = os.path.join(odir, basepath)
            if os.path.isfile(outfile):
                continue
           # print 'making soup' , os.path.join(dirpath,fh)
            scontent.makesoup(os.path.join(dirpath,fh))
        if len(scontent.title) > 0 or len(scontent.bodytext) > 0:
            scontent.dumpondisk(os.path.join(odir, basepath), basepath)
            scontent.clear()
            count = count + 1
    return count

def openurl(url):
    try:
        return urllib2.urlopen(url)
    except urllib2.HTTPError:
        return None
    except urllib2.URLError:
        return None

def main(argv=None):
    if argv is None:
        argv = sys.argv()
    print parsesites(argv[0] ,argv[1])

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
