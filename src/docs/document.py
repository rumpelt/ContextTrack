"""
"""
from tokenizers import ptbtokenizer as ptb
from nltk import probability
import math
import codecs
class  document(object):
    def __init__(self, fid, path=None):
        self.fid = fid
        self.path = path
        self.frdist = None
        self.terms = None
        self.useptb = True
        self.lenfactorial = None
        self.termfact = None            
    def termfactorial(self, freqdist):
        self.termfact = dict()
        for key, value in freqdist.items():
            lg = logfactorial(value)
            if lg  > 0.0 :
                self.termfact[key] = lg

    def tokens(self, tagname=None , endtag=None, stem=True, stoplanguage='english', lowercase=True):
        '''
          return the content in the file as as list of tokens
          if tagname is not None then this represents a doc with tagging.
          tag must be specified completely for example a title tag must be specified as
         
        '''
        handle = codecs.open(self.path, encoding='utf-8', errors='ignore')
        if tagname is None:
            if self.useptb:
                return ptb.ptbtokens(handle.read(), stem, stoplanguage, lowercase)
            else:
                return ptb.whitespace(handle.read(), stem, stoplanguage, lowercase)

        toks = None
        found = False
        end = False
        for line in handle:
            line = line.strip()
            if found:
                if line != endtag:
                    toks = toks + ptb.ptbtokens(line, stem, stoplanguage, lowercase)
                else:
                    end = True
                    found = False
                    break
            if line == tagname:
                found = True
                toks = []
        if end and len(toks) > 0:
            return toks
        else:
            return None
    
    def getdoclength(self):
        return len(self.tokens(stem=False, lowercase=False))
    
    def fd(self, tokens):
        fd = probability.FreqDist()
        for term in tokens:
            fd.inc(term)
        return fd

    def distribution(self, tokens, laplace=True):
        fd = probability.FreqDist()
        for word in tokens:
           fd.inc(word)
        if laplace:
            return probability.LaplaceProbDist(fd)
        else:
            return probability.MLEProbDist(fd)

class docbag(object):
    def __init__(self, doclist):
        self.docs = doclist
        self.gdist = None
        self.localdist = None
        self.localfd = None

    def getdoc(self, fid):
        for doc in self.docs:
            if doc.fid == fid:
                return doc
        return None

    def cleardoclist(self):
        self.docs = None

    def globaldist(self, laplace=True):
        '''
        return a global probabiliyt distribution for a set of document.
        Memory problem if the set of document is too large.
        Use laplace smooting by default.
        Creates  a storage gdist which holds the global dist
        Must clear this variable after use to free the memory
        '''
        fd = probability.FreqDist()
        for doc in self.docs:
            tokens = None
            if doc.terms is None:
                tokens = doc.tokens()
            else:
                tokens = doc.terms
            for tok in tokens:
                fd.inc(tok)
        if laplace:
            self.gdist = probability.LaplaceProbDist(fd)
        else:
            self.gdist = probability.MLEProbDist(fd)
        return self.gdist

    def savelocaldist(self, laplace = True, savetokens = False):
        self.localdist = dict()
        
        for doc in self.docs:
            if savetokens:
                doc.terms = []
            localfd = probability.FreqDist()
            for tok in doc.tokens():
                if savetokens:
                    doc.terms.append(tok)
                localfd.inc(tok)
            if localfd.N() > 0:
                if laplace:
                    self.localdist[doc.fid] = probability.LaplaceProbDist(localfd)
                else:
                    self.localdist[doc.fid] = probability.MLEProbDist(localfd)
    def savelocalfd(self):
        self.localdist = dict()
        for doc in self.docs:
            localfd = probability.FreqDist()
            for tok in doc.tokens():
                localfd.inc(tok)
            self.localfd[doc.fid] = localfd

    def clearlocaldist(self):
        self.localdist = None
     
    def cleargdist(self):
        '''
        clear self.gdist
        '''
        self.gdist = None
 
    def flushmemory(self):
        self.gdist = None
        self.localdist = None
        self.localfd = None
        for doc in self.docs:
            doc.terms = None    

    def cleardoctokens(self):
        for doc in self.docs:
            doc.terms = None

    def multinomial(self, modeldoc ,lamda): 
        '''
        '''
        result = dict()
       
        if self.localdist is None:
            self.savelocaldist(laplace=False, savetokens = True)
            self.globaldist()
            self.cleardoctokens()

        if modeldoc.lenfactorial is None:
            modeldoc.terms = modeldoc.tokens()
            modeldoc.lenfactorial = logfactorial(len(modeldoc.terms))
            modeldoc.termfactorial(modeldoc.fd(modeldoc.terms))
        
        for doc in self.docs:
            docdist = None
            if self.localdist is not None:
                docdist = self.localdist[doc.fid]
            else:
                print 'cannot be here'
                docdist = doc.distribution(doc.tokens(), laplace= False)
            summ = 0.0
            for term in modeldoc.terms:
                lprob = (1.0 - lamda)* docdist.prob(term)
                gprob = lamda * self.gdist.prob(term)
                prob = lprob + gprob
                prob = math.log(prob)
                summ = summ +  prob 
    
            summ = summ +  modeldoc.lenfactorial
    
            for key, value in modeldoc.termfact.items():
                summ = summ - value

            result[doc.fid] = summ

        return result 

    def docscorebyKL(self, modeldoc):
        '''
        modeldocument is a single document object and doclist is is list of document object.
        Returns a dict of document and kl score for each of the document in the list.
        '''

        result = dict()
        setdist = modeldoc.distribution(modeldoc.tokens(), laplace=False)
        if self.gdist is None:
            self.globaldist()
            self.savelocaldist(laplace=False)
        for doc in self.docs:
            if self.localdist is not None:
                superdist = self.localdist.get(doc.fid)
            else:
                superdist = doc.distribution(doc.tokens(), laplace = False)
            result[doc.fid] =  klscore(setdist, superdist, self.gdist)
        return result

def logfactorial(n):
    if n <= 0:
        return 0
    fact = 0;
    for i in range(1,n+1):
        fact = fact + math.log(i)
    return fact
def klscore(setdist, superdist , globaldist ):
    '''
    setdist and super dist represent nltk.probability.ProbDistI .
    ProbDistI represent interface for probability distribution
    setdist must not be  a laplacian distribution i.e probability of term not in the distribution must be zero
    superdist must not be a laplacian distribution
    
    '''
    
    summation = 0
    for term in setdist.samples():
        termp = setdist.prob(term)
        if termp > 0.0000000:
            termp = math.log(termp)
        termq = superdist.prob(term)
        if termq > 0.00000:
            termq = math.log(termq)
        else:
            termq = math.log(globaldist.prob(term))
        summation = summation + termp * (termp - termq)
    
    return summation

def testklscore(file1, file2, file3):
    doc1 = document('1',file1)
    doc2 = document('2', file2)
    modeldoc = document('3', file3)
    bag = docbag([doc1, doc2])
    return bag.docscorebyKL(modeldoc)

 
