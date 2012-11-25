'''
 Parse the yelp academic data  set into proper structures
'''
from set import Set
uids = Set()

class business():
    def __init__(self):
        self.id = None
        
def parsecorpus(fname):
    '''
    read the yelp file line by line
    '''
    fhandle = open(fname)
    import json
    for line fhandle:
        obj = json.load(line)
        if obj.get('votes') is not None:
           obj['useful'] = obj['useful']
           obj['funny']= obj['funny']
           obj['cool'] = obj['cool']
           obj['votes']= None
        print 'got json obj'   
