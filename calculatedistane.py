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
from googlemaps import GoogleMaps
import saxparser
import json
import sys
import time
from searchpl import yelpsearch as yp
contextlist = list()
chandler = saxparser.ContextFileHandler(contextlist)
gkey = sys.argv[1]
print 'google jkeuy' , ' ', gkey
gmap = GoogleMaps(gkey)
saxparser.parse('/usa/arao/trec/contexttrec12/contexts.txt',chandler)

for context in contextlist:
    js =    json.load( open('/usa/arao/trec/contexttrec12/yelpplaces/'+context.attribute['number']))
    businesslist = list()
    print 'num business in this contect' , ' ', len(js['businesses'])
    for business in js['businesses']:
        if business.get('gmaptime') is not None:
            businesslist.append(business)
            continue
     
        destlat = float(str(business['location']['coordinate']['latitude']))
        destlong = float(str(business['location']['coordinate']['longitude']))
        dest = gmap.latlng_to_address(destlat, destlong)
        originlat = float(context.attribute['lat'])
        originlong = float(context.attribute['long'])
        orig = gmap.latlng_to_address(originlat, originlong)
        directions  = None
        try:
            directions = gmap.directions(orig, dest)
        except:
            print 'problem with ', ' ', orig, '  ', dest 
            continue 
        if directions is None:
            continue
        meters = directions['Directions']['Distance']['meters']
        timesec =  directions['Directions']['Duration']['seconds']
        business['gmapdistance'] = meters
        business['gmaptime'] = timesec
        if timesec is not None:
            businesslist.append(business)  
        
        time.sleep(3)
    sortedlist = sorted(businesslist, key=lambda busi : busi['gmaptime'])
    fh = open('/usa/arao/trec/contexttrec12/yelpplaces2/'+context.attribute['number'],'wb')
    js['businesses'] = sortedlist
    json.dump(js,fh)
    fh.close()
    print 'done the contect number' , ' '+context.attribute['number']
