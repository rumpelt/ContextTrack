'''
Created on May 24, 2012

@author: ashwani
'''
import xml.sax
from xml.sax.saxutils import unescape
from lxml import etree
from parser import siteparser
import time
def parse(filename, handler):
    ifile = open(filename)
    xml.sax.parse(ifile,handler)


class profile():
    '''
     A profile reprsenting the profile number and a set examples and profils initial liking and final liking.
    '''
    def __init__(self):
        self.number = None
        self.examples = dict()
    
    def getgoodexamples(self):
        '''
        Returns  a list of good examples liked by this profile after going through the
        example website
        '''
        result = list()
        for key, val in self.examples.items():
            if val[1] == '1':
                result.append(key)
        return result
    
    def getnegexamples(self):
        '''
        Returns  a list of neg examples liked by this profile after going through the
        example website
        '''
        result = list()
        for key, val in self.examples.items():
            if val[1] == '-1':
                result.append(key)
        return result
    
       
class profilefilehandler(xml.sax.ContentHandler):
    '''
    Due to problem in the profile file this handler will not work.
    The profile file is not in a proper xml format
    '''
    def __init__(self, profilelist):
        self.profilelist = profilelist      
    
    def lineparse(self, filename):
        fh = open(filename)
        profiles = list()
        for line in fh:
            line = line.split()
            if line[0] == '<profile':
                prf = profile()
                pnum = line[1]
                prf.number = pnum[pnum.find('"') + 1 : pnum.rfind('"')]
            if line[0] == '</profile>':
                profiles.append(prf)
            if line[0] == '<example':
                enum = line[1]
                enum = enum[enum.find('"') + 1 : enum.rfind('"')]
                init = line[2]
                init  = init[init.find('"')+1 : init.rfind('"')]
                final = line[3]
                final = final[final.find('"')+1 : final.rfind('"')]
                prf.examples[enum] = (init, final)
        return profiles     

    def startElement(self, name, attrs):
        if name == 'profile':
            self.profile = profile()
            self.profile.number = str(attrs.getValue('number'))
        if name == 'example':
            self.profile.examples[attrs.getValue('number')] = (attrs.getValue('initial'), attrs.getValue('final'))
        
    def endElement(self, name, attrs):
        if name == 'profile':
            self.profilelist.add(self.profile)
            self.profile = None
    def characters(self, content):
        return None

class Example():
    def __init__(self):
        self.attribute = dict()

class ExampleFileHandler(xml.sax.ContentHandler):
    def __init__(self, exlist):
        self.attribute = dict()
        self.exlist = exlist
        self.content = []
        self.tempexample = None
        
    def startElement(self, name, attrs):
        if name == 'example':
            self.tempexample = Example()
            self.tempexample.attribute['number'] = str(attrs.getValue('number'))
                
    def endElement(self, name):        
        if name == 'example':
            self.exlist.append(self.tempexample)
        if name == 'title':
            self.tempexample.attribute['title'] = ''.join(self.content)
        if name == 'descriptiom':
            self.tempexample.attribute['description'] = ''.join(self.content)
        if name == 'url':
            self.tempexample.attribute['url'] = ''.join(self.content)
        self.content = []
        
    def characters(self, content):
        content = str(content.encode('ascii', 'ignore'))
        content = content.strip('\n\t')
        content = unescape(content)
        if (len(content) > 0):
                self.content.append(content)
class Context():
    def __init__(self):
        self.attribute = dict()
        
class  ContextFileHandler(xml.sax.ContentHandler):
    def __init__(self, contextlist):
        self.contextlist = contextlist
        self.tempcontext = None
        self.content = []
    def startElement(self, name, attrs):
        if name == 'context':
            self.tempcontext = Context()
            self.tempcontext.attribute['number'] = str(attrs.getValue('number')) 
     
    def endElement(self, name):
        if name == 'context':
            self.contextlist.append(self.tempcontext)            
        if name == 'city':
            self.tempcontext.attribute['city'] = ''.join(self.content)
        if name == 'state':
            self.tempcontext.attribute['state'] = ''.join(self.content)
        if name == 'lat':
            self.tempcontext.attribute['lat'] = ''.join(self.content)
        if name == 'long':
            self.tempcontext.attribute['long'] = ''.join(self.content)
        if name == 'day':
            self.tempcontext.attribute['day'] = ''.join(self.content)
        if name == 'time':
            self.tempcontext.attribute['time'] = ''.join(self.content)
        if name == 'season':
            self.tempcontext.attribute['season'] = ''.join(self.content)
        self.content = []
            
        
    def characters(self, content):
        content = str(content)
        content = content.strip('\n\t')
        if (len(content) > 0):
                self.content.append(content)



class suggestion(xml.sax.ContentHandler):

    def __init__(self,wfname):
        self.profile = None
        self.rank = None
        self.context = None
        self.title = None
        self.description   = None
        self.url = None
        self.content = ''
        self.wfname = wfname 
        self.cache = dict()
        

    def startElement(self, name, attrs):
        if name == 'suggestion':
           self.profile = unicode(attrs['profile'])
           self.context = unicode(attrs['context'])
           self.rank = unicode(attrs['rank'])

    def endElement(self, name):

        if name == 'title':
            self.title = self.content.strip()
            self.content = ''

        if name == 'description':
            self.description = self.content.strip()
            self.content = ''
            
        if name == 'url':
            self.url = self.content.strip()
            self.content = ''
 
        if name == 'suggestion':
             process(self.wfname, self.cache, self.profile, self.rank, self.context, self.title, self.description, self.url)

    def characters(self, content):
        content = unicode(content)
        if len(content) > 0:
            self.content = self.content + content


def process(fname, cache, profile, rank, context, title, description, url):
    
    sugg = etree.Element("suggestion")
    sugg.set("profile", profile)
    sugg.set("context" , context)
    sugg.set("rank", rank)
    ct = cache.get(url)
    if ct is None:
        ct = siteparser.sitecontent()
        print 'getting url', url
        f = siteparser.openurl(unicode.encode(url,"utf-8", 'ignore'))
        if f is not None:
            s = ct.soup(f.read())
            time.sleep(2)
            ct.getheader(s)
        else:
           print ' cannot open url ', url
        cache[url] = ct

    ttl = etree.Element("title")
    if ct.title is not  None:
        ttl.text = ct.title
    elif ct.keywords is not None:
        ttl.text = ct.keywords
    else:
        ttl.text = title
    
    desp = etree.Element("description")
   
    if ct.description is not  None:
        desp.text = ct.description
    elif ct.keywords is not None:
        desp.text = ct.keywords
    else:
        desp.text = description

    ul = etree.Element("url")
    
    ul.text = url
    sugg.append(ttl)
    sugg.append(desp)
    sugg.append(ul)
    hand = open(fname, 'ab')
    hand.write(etree.tostring(sugg, pretty_print=True))
    hand.close()
    return None










