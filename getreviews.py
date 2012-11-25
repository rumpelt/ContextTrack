#!/usr/bin/python
"""
get the review for the yelp
"""
import sys
import saxparser
import json
import time
from searchpl import yelpsearch as yp
contextlist = list()
chandler = saxparser.ContextFileHandler(contextlist)
ckey = sys.argv[1]
csecret = sys.argv[2]
token = sys.argv[3]
tokensecret = sys.argv[4]
idir = sys.argv[5]
odir = sys.argv[6]
startcontext = int(sys.argv[7])
togetcount = int(sys.argv[8])
saxparser.parse('/usa/arao/trec/contexttrec12/contexts.txt',chandler)

for context in contextlist[startcontext -1 : ]:
    exbusiness = json.load(open(idir+'/'+context.attribute['number']))
    bid = dict()
    for business in exbusiness['businesses']:
        bid[business['id']] = 1
    count = len(exbusiness['businesses'])
    if togetcount < count:
        count = togetcount
    args = []
    args.append('--consumer_key='+ckey)
    args.append('--consumer_secret='+csecret)
    args.append('--token='+token)
    args.append('--token_secret='+tokensecret)

    for i in range(0, count):
        business = exbusiness['businesses'][i]
        if business.get('reviews') is not None:
            continue
        newargs = list(args)
        newargs.append('--id='+business['id'].encode('ascii','ignore'))
        print newargs
        result = yp.main(newargs)
        if result is None or result.get('reviews') is None:
            print 'cannot get for context number ',context.attribute['number'] ,'  ' ,result
            continue
        business['reviews'] = result['reviews']
        time.sleep(3)
    print 'got the context', ' ', context.attribute['number']
    fh = open(odir+'/'+context.attribute['number'],'wb')
    json.dump(exbusiness, fh)       
    fh.close()
    
        
    

