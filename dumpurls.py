import sys
import json
import csv
import codecs
import utfcsv  as sf
whandle = open('/usa/arao/yelpbiz2.csv','wb')
cv = sf.UnicodeWriter(whandle)
for i in range(1,51):
    rhandle = open('/usa/arao/trec/contexttrec12/yelpplaces/'+str(i))
    bs = json.load(rhandle)
    for b in bs['businesses']:
#        print b
        row = list()
        row.append(str(i))
        row.append(b.get('id'))
        row.append(b.get('url'))
        cv.writerow(row)
    rhandle.close()
whandle.close()
