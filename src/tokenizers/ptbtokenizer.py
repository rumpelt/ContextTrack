import nltk

def ptbtokens(sentence, stem=True, stoplanguage='english', lowercase=True):
    tokens   = nltk.tokenize.treebank.TreebankWordTokenizer().tokenize(sentence)
    if lowercase:
        tokens = [w.lower() for w in tokens]
    if stoplanguage is not None:
        sw = nltk.corpus.stopwords.words(stoplanguage)
        tokens = [w for w in tokens if not w in sw]
    if stem:
        stemmer = nltk.stem.PorterStemmer()
        tokens = [stemmer.stem(w) for w in tokens]
    return tokens

def whitespace(sentence, stem=True, stoplanguage='english', lowercase=True):
    tokens   = nltk.tokenize.simple.WhitespaceTokenizer().tokenize(sentence)
    if lowercase:
        tokens = [w.lower() for w in tokens]
    if stoplanguage is not None:
        sw = nltk.corpus.stopwords.words(stoplanguage)
        tokens = [w for w in tokens if not w in sw]
    if stem:
        stemmer = nltk.stem.PorterStemmer()
        tokens = [stemmer.stem(w) for w in tokens]
    return tokens

