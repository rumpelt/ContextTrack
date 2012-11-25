#!/usr/bin/python
"""
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
startcontext = int(sys.argv[5])
endcontext = int(sys.argv[6])
saxparser.parse('/usa/arao/trec/contexttrec12/contexts.txt',chandler)
for context in contextlist[startcontext -1: endcontext]:
    exbusiness = json.load(open('/usa/arao/trec/contexttrec12/yelpplaces/'+context.attribute['number']))
    bid = dict()
    for business in exbusiness['businesses']:
        bid[business['id']] = 1
    count = len(exbusiness['businesses'])
    args = []
    args.append('--consumer_key='+ckey)
    args.append('--consumer_secret='+csecret)
    args.append('--token='+token)
    args.append('--token_secret='+tokensecret)
#args.append('--location='+context.attribute['city']+','+context.attribute['state']+',USA')
#    args.append('-p='+pl)
#   args.append('-m='+'1')
#    print pl
    newbusiness = list(exbusiness['businesses'])
    for i in range(0, count):
        business = exbusiness['businesses'][i]
        address = ''
        for adpart in business['location']['display_address']:
            address = address +","+str(adpart)    
      #  pl = lat+','+lng    
        ypargs = list(args)
        ypargs.append('-l='+address)
        print args
        result = yp.main(ypargs)
        if result is None or result.get('businesses') is None:
            print 'cannot get for context number ',context.attribute['number'] ,'  ' ,result
            continue
        for newb in result['businesses']:
            if len(newbusiness) > 250:
                break
            if bid.get(newb['id']) is  None:
                bid[newb['id']] = 1
                newbusiness.append(newb)
        time.sleep(3)
    print 'content number ' , context.attribute['number'], ' got new business places =  ', len(newbusiness)
    exbusiness['businesses'] = newbusiness
    fh = open('/usa/arao/trec/contexttrec12/yelpplaces2/'+context.attribute['number'],'wb')
    json.dump(exbusiness, fh)       
    fh.close()
