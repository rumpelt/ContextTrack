'''
Created on May 23, 2012

@author: ashwani
'''
import unittest
import json
import urllib
import sys
'''
Madatory parameters for Googlge Place api to request for information on 
near a place are as following.
    key : application key
    location : latitude,longitude
    radius: to be used when rankby='distance' option is used
    sensor : if request is from gps or anyother sensor
'''
class Place():
    
    def __init__(self, keylocation, language = 'en', rankby='prominence'
                 , sensor = True, distance = 800000):
        self.__language= language
        self.__rankby = rankby
        self.__keyfile = keylocation
        self.__sensor = sensor
        self.__distance = distance
        
    def getrawinfo(self, latitude, longitude):
        #params = dict()
        params ='location='+ str(latitude)+','+str(longitude)
        
        if (self.__rankby == 'prominence'):
            params = params+ '&radius='+str(self.__distance)
        else:
            params = params + '&rankby='+self.__rankby
        if self.__sensor:
            params =  params + '&sensor='+'true'
        else:
            params= params+'&sensor'+'false'
        params = params + '&language=' +self.__language
        
       # print(params)
        
        fhandle = open(self.__keyfile,'r')
        key = fhandle.read()
        fhandle.close()
        
        params = params+ '&key='+ key
        #print '***'
       # print params
        urladd = 'https://maps.googleapis.com/maps/api/place/search/json?'
        #print urladd+params
        f = urllib.urlopen(urladd+params)
        content = f.read()
        return content
    
    def getplacefromcontext(self, contexts, dirtowrite):
        for context in contexts:
            content = self.getrawinfo(context.attribute['lat'], context.attribute['long'])
            js = json.loads(content)
            if str(js['status']) != 'OK':
                print 'could not get for '+context.attribute['number']
                print str(js['status'])
                continue
            fwrite = dirtowrite+'/'+'context'+context.attribute['number']
            fhandle = open(fwrite,'w')
            fhandle.write(content)
            fhandle.close()
            
    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testName(self):
        pass

    
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()