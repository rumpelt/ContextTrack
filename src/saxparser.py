'''
Created on May 24, 2012

@author: ashwani
'''
import xml.sax
from xml.sax.saxutils import unescape
def parse(filename, handler):
    ifile = open(filename)
    xml.sax.parse(ifile,handler)



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