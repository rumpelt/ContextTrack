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
from crawler import curlcrawl
examplelist = list()
exhandler = saxparser.ExampleFileHandler(examplelist)
saxparser.parse('/usa/arao/trec/contexttrec12/examples.txt',exhandler)
for ex in examplelist:
    curlcrawl.curlcrawl([ex.attribute['url']],dumpdir='/usa/arao/trec/contexttrec12/examplesites/'+ex.attribute['number'], mode = 0750)


