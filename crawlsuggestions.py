#!/usr/bin/python
"""
script to crawl the suggestions websities.
Suggestion websites links are present in a csv file.
first row is the context number
second row biz id 
third row thw url on yelp
forth row is the actual url of the business
"""
import utfcsv
import sys
from crawler import curlcrawl
import utfcsv
import os
import codecs
def main(argv):
    ifile = open(argv[1])
    dumpdir = argv[2]
    startrow = int(argv[3])
    creader = utfcsv.UnicodeReader(ifile)
    rowc = 0
#    print startrow
    for row in creader: 
        rowc = rowc + 1
        if rowc < startrow:
            continue
        context = row[0]
        idt = row[1]
        #print idt
        if len(row) > 3 and len(row[3]) > 0:
            url = row[3]
        else:
            continue
    
        dirc = dumpdir+'/'+idt
        if os.path.exists(dirc):
            continue
        print 'getting url' , ' ', url.encode('ascii','ignore')
        fetched = curlcrawl.curlcrawl([url], maxlink=10, dumpdir=dirc, mode=0750)
        if os.path.exists(dirc):
            idfile = codecs.open(dirc+'/'+'idfile',encoding="utf-8",mode='wb')
            idfile.write(idt)
            idfile.close()
        print 'got context ' , context , ' for id ' , idt.encode('ascii','ignore') , ' feteched ' , fetched

if __name__ == "__main__":
    sys.exit(main(sys.argv))
