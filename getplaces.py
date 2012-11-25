#!/usr/bin/python
"""
This script crawls each of the site mentioned in examples.txt file
of the context trec 2012.
For each of the examples it create a directory with that example number
and stores the crawled pages of that site into that directory.
The pages are stored as per the path in url of the crawled page.
For example 
  http://www.cis.udel.edu/home/main.html : saved to /home dir
 http://www.cis.udel.edu/home/nextdir/text.html will be save to /home/nextdir
"""

import saxparser
import json
from searchpl import yelpsearch as yp
import sys
contextlist = list()
chandler = saxparser.ContextFileHandler(contextlist)
ckey = sys.argv[1]
csecret = sys.argv[2]
token = sys.argv[3]
tokensecret = sys.argv[4]

saxparser.parse('/usa/arao/trec/contexttrec12/contexts.txt',chandler)
for context in contextlist:
    args = []
    args.append('--consumer_key='+ckey)
    args.append('--consumer_secret='+csecret)
    args.append('--token='+token)
    args.append('--token_secret='+tokensecret)
    lat = str(context.attribute['lat'])
    lng = str(context.attribute['long'])
    pl = lat+','+lng    
    args.append('--location='+context.attribute['city']+','+context.attribute['state']+',US')
    #args.append('-p='+pl)
    #args.append('-m='+'1')
#    print pl
    result = yp.main(args)
    print 'content nuber ' , context.attribute['number'], ' got total places =  ', result.get('total')
    if result.get('total') is not None:
        json.dump(result, open('/usa/arao/trec/contexttrec12/yelpplaces/'+context.attribute['number'],'wb'))       
    print result.get('total')
        
    

