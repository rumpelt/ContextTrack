'''
script to go over each profile and each context
'''
import sys
import saxparser
import json
from docs import document
import os
import utfcsv
import codecs 
from xml.sax.saxutils import escape
cfile = '/usa/arao/trec/contexttrec12/contexts.txt'
pfile = '/usa/arao/trec/contexttrec12/profiles.txt'
exdir = '/usa/arao/trec/contexttrec12/parsedexample'
ypdir = '/usa/arao/trec/contexttrec12/yelpplaces'
suggdir = '/usa/arao/trec/contexttrec12/sites'
urlfile = '/usa/arao/yelpbiz.csv'
catfile = '/usa/arao/trec/contexttrec12/categories'
temporal = False
ranklambda = 0.8
supercache = dict()
def getcategories(ifile):
    hand = open(ifile)
    result = list()
    for line in hand:
        val = line.split()
        for v in val:
            if v[0] == '(':
                result.append(v[1:len(v)-1])
    return result

def outputrun(fname, profile, results, contnumber):
    '''
     fname is the name of file to which suggestions will be made.
     profile is profile for which suggestions will be made.
     suggestions is list of docs in the ranked order;
    '''
    handle = codecs.open(fname, 'ab' , encoding='utf-8', errors='replace')
    rank = 1
    for result in results:
        s = "\n<suggestion profile=\"%s\" context=\"%s\" rank=\"%s\">\n" %(profile.number, contnumber, str(rank))
        handle.write(s)
        
        title = result.doc.tokens("<title>",'</title>', stem=False, stoplanguage=None, lowercase=False)
        if title is None:
            title = result.doc.tokens("<keywords>",'</keywords>', stem=False, stoplanguage=None, lowercase=False)
        if title is None:
            title = result.doc.tokens("<description>",'</description>', stem=False, stoplanguage=None, lowercase=False)
        if title is None:
            title = result.doc.fid
        s = ' '.join(title)
        s = escape(s, {"&":" and ", "<" : " less than ", ">" : " greater than " })
        if len(s) > 64:
            s = s[0:64]
        s = "<title>%s</title>\n" %(s)
        handle.write(s)
        
        description = result.doc.tokens("<description>",'</description>', stem=False, stoplanguage=None, lowercase=False)
        if description is None:
            description = result.doc.tokens("<title>",'</title>', stem=False, stoplanguage=None, lowercase=False)
        if description is None:
            description = result.doc.tokens("<keywords>",'</keywords>', stem=False, stoplanguage=None, lowercase=True )
        if description is None:
            description = result.doc.fid
        s = ' '.join(description)
        s = escape(s, {"&":" and ", "<" : " less than ", ">" : " greater than " })
        if len(s) > 511:
            s = s[0:511]
        s = "<description>%s\n</description>\n" %(s)
        handle.write(s)
        
        s = "<url>%s</url>\n" %(result.doc.url)
        handle.write(s)
        handle.write('</suggestion>\n')

        rank = rank + 1
        
def getyelpsuggestions(contextnum, yelpdir, suggdir , urlfile ,categories):
    handle = open(os.path.join(yelpdir,contextnum))
    result = dict()
    load = json.load(handle)
    reader = open(urlfile)
    csvrd = utfcsv.UnicodeReader(reader)
    idurl = dict()
    for row in csvrd:
        if len(row) > 3:
            idurl[row[1]] = row[3]

    for business in load['businesses']: 
        cats = business.get('categories')
        if cats is None:
            continue
        found = False
        for cat in cats:
            if len(cat) > 1 and cat[1] in categories:
                found = True
                break
        if not found:
            continue
        if supercache.get(business['id']) is not None:
            result[business['id']] = supercache.get(business['id'])
            continue

        fpath = os.path.join(suggdir, business['id'])
        if not os.path.exists(fpath):
            continue
        doc = document.document(business['id'], fpath)
        doc.gmaptime = business.get('gmaptime')
        doc.url = idurl[doc.fid]
        result[doc.fid] = doc
        supercache[doc.fid] = doc

    reader.close()
    return result

def makeexampledocs(exdir):
    result = dict()
   # print exdir
    for fname in os.listdir(exdir):
        doc = document.document(fname, os.path.join(exdir, fname))
        result[doc.fid] = doc
    return result    

def gettemporaldocs(context, cdir):
    resutl = list()
    day = context.attribute['day']
    time = context.attribute['time']
    season = context.attribute['season']
    daydoc = document.document(day, os.path.join(cdir,day))
    timedoc = document.document(time, os.path.join(cdir, time))
    seasondoc = document.document(season, os.path.join(cdir, season))
    return [daydoc, timedoc, seasondoc] 

def main(argv=None):
    stprofile = int(argv[0])
    eprofile = int(argv[1])
    ofile = argv[2]
    profiles = saxparser.profilefilehandler(None).lineparse(pfile)
    contexts = list()
    saxparser.parse(cfile, saxparser.ContextFileHandler(contexts))
    exampledocs = makeexampledocs(exdir)
    categories = getcategories(catfile)
    
    suggestions = dict()
    for context in contexts:
        docs = getyelpsuggestions(context.attribute['number'],ypdir, suggdir, urlfile, categories).values()
        suggestions[context.attribute['number']] = suggestion(docs)
        
    temporaldoccache = dict()


    for profile in profiles[stprofile:eprofile]:
        examples = profile.getgoodexamples()
        negexamples = profile.getnegexamples()                   
        
        for context in contexts[40:]:

            docbag = suggestions[context.attribute['number']].bag
            docscore = dict()
            langresult = list()
            
            if temporal:
                if suggestions[context.attribute['number']].rank is None:
                    temporaldocs = gettemporaldocs(context, '/usa/arao/trec/contexttrec12')
                    doclist = list()
                    for doc in temporaldocs:
                        if temporaldoccache.get(doc.fid) is not None:
                            doclist.append(temporaldoccache.get(doc.fid))
                        else:
                            doclist.append(doc)
                            temporaldoccache[doc.fid] = doc         
                    suggestions[context.attribute['number']].makescore(doclist)
        
          
            for example in examples:
                if exampledocs.get(example) is None:
                    continue
                cdocscore = docbag.multinomial(exampledocs[example], 0.2)               
                for key, value in cdocscore.items():
                    if docscore.get(key) is not None:
                        docscore[key] = docscore.get(key) + (value/ len(examples))
                    else:
                        docscore[key] = value / len(examples)
            
            negdocscore = dict()
            
            for example in negexamples:
                if exampledocs.get(example) is None:
                    continue
                cdocscore = docbag.multinomial(exampledocs[example], 0.2)
                for key, value in cdocscore.items():
                    if negdocscore.get(key) is not None:
                        negdocscore[key] = (value/ len(examples)) + negdocscore[key]
                    else:
                        negdocscore[key] = value / len(examples)

            score = dict() 
            for key in docscore.keys():
                negative = negdocscore.get(key)
                if negative is None:
                    negative = 0
                positive = docscore.get(key)
                score[key] = positive - negative

            docscore = score
            
            for key,value in docscore.items():
                langresult.append(result(key, value, docbag.getdoc(key)))

            finalresult = sorted(langresult, key = lambda item : item.score, reverse=True)
        
            if temporal:
                temprank = suggestions[context.attribute['number']].rank
                combinedresult = list()
                count = 0.0
                for item in finalresult:
                    newrank = ranklambda * count + (1-ranklambda) * temprank.index(item.idt)
                    combinedresult.append(result(item.idt, newrank, item.doc))
                    count = count + 1
                    print count, ' new rank ' , newrank , ' temporal rank ', temprank.index(item.idt) 
                finalresult = sorted(combinedresult, key = lambda item : item.score)

            docbag.flushmemory()

            finalind = len(finalresult)
            if finalind > 50:
                finalind = 50         
            outputrun(ofile,profile, finalresult[0:finalind], context.attribute['number'])
        
class result(object):
    def __init__(self, idt, score=None, doc=None):
        self.idt = idt
        self.score = score
        self.doc = doc

class suggestion(object):
    def __init__(self, documents):
        self.documents = documents
        self.rank = None
        self.bag = document.docbag(self.documents)
 

    def makescore(self, docs):
        score = dict()
        for doc in docs:
            cdocscore = self.bag.multinomial(doc, 0.2)               
            for key, value in cdocscore.items():
                if score.get(key) is not None:
                    score[key] = score.get(key) + (value/ len(docs))
                else:
                    score[key] = value / len(docs)
        ranklist = list()
        for key,value in score.items():
            ranklist.append(result(key, value, None))
        ranklist = sorted(ranklist, key = lambda item : item.score, reverse=True)
        self.rank  = list()
        for item in ranklist:
            self.rank.append(item.idt)
        
    def getrank(self, key):
        if self.rank is None:
            return None
        else:
            return self.rank.index(key)
if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
