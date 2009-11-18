#DSC - damnsimplecrawler.py
import urllib2
import BeautifulSoup
import feedparser
from math import sqrt
import logging 
logging.basicConfig(level = logging.DEBUG)
log = logging.getLogger('damnsimplecrawler')
import traceback

####method decorator
def deco(f):
    """A simple decorator for the entry, exit and exceptions in methods
    It standardises the return value of any decorated method to be 
    Python dict.
    """
    def _deco(request, *args, **kwds):
        result = {'status': False}
        try:
            result.update(f(request, *args, **kwds))
            result['status'] = True
        except Exception,e:
            execinfo = str(e) + '||\n' + str(traceback.format_exc())
            log.exception(' ')
            result['error_message'] = execinfo
        return result
    return _deco


####crawler classes
class Crawler(object):
    """base class for the WebPage and RSS crawlers
    """
    def __init__( self, uri):
        self.uri = uri
      
    @deco
    def runCrawler( self ):
        """ An organizer method
        'organizer' method for the pipile 'hook' methods
        like crawl, tokenize and cluster.
        """
        self.docs  = self.crawl()
        return self.tokenize()

    def crawl( self ):
        """To be implemented/overriden by inherting class
        
        returns: returns a dict with key 'data' whose value type  
        is a list of dicts representing the uri and text of the 
        docuemnt at that uri.
        """
        raise NotImplementedError

    def tokenize( self ):
        """ Tokenizes the documents.

        Base implementation works for most of the derived classes.
        Some special/specific derived class may override this

        returns: a list of dict's
        [....,{'uri':'http://..', 'tokens': [('word', 'frequency'), ...]},...]
        """
        #Assumption for ease: only whitespace is a separator
        if not isinstance(self.docs['data'], list):
            raise TypeError("required list and given %s" % \
                                str(type(self.docs['data'])))
        tokens = [{'uri': doc['uri'],  'text': doc['text'], \
                       'tokens': doc['text'].split()} \
                      for doc in self.docs['data']]
        return {"tokens": tokens}
    
class WebPage( Crawler ):
    """Responsible for crawl if a URL is that of a webpage
    """
    
    @deco
    def crawl( self ):
        data = urllib2.urlopen( self.uri ).read()
        soup = BeautifulSoup.BeautifulSoup(data)
        ps = []
        for div in soup.findAll('div'): #paragraphs from html divs 
            ps.extend( div.findAll('p') )
        text = ' '.join( [p.renderContents() for p in ps] )
        return {'data': [{'uri': self.uri, 'text':text}]}
        

class RSS( Crawler ):
    """Responsible for crawl if a URl is that of a RSS
    """
    
    @deco 
    def crawl( self ):
        presumed_useful_keys = ['author', 'summary', 'title']
        entries = feedparser.parse( self.uri )['entries']
        pages = [{'uri' : entry['link'], 
                  'text' : unicode(' '.join([entry.get(key,'') for key in \
                                                 presumed_useful_keys]
                                            )).encode('utf-8','replace')
                  }
                 for entry in entries]
        return {'data': pages}


####clustering 
def pearson(v1,v2):
    sum1=sum(v1)
    sum2=sum(v2)
    sum1Sq=sum([pow(v,2) for v in v1])
    sum2Sq=sum([pow(v,2) for v in v2])
    pSum=sum([v1[i]*v2[i] for i in range(len(v1))])
    num=pSum-(sum1*sum2/len(v1))
    den=sqrt((sum1Sq-pow(sum1,2)/len(v1))*(sum2Sq-pow(sum2,2)/len(v1)))
    if den==0: 
        return 0
    return 1.0-num/den

class bicluster:
    def __init__(self, vec, left=None, right=None, 
                 distance=0.0, id=None):
        self.left=left
        self.right=right
        self.vec=vec
        self.id=id
        self.distance=distance

def hcluster(rows, distance=pearson):
    distances={}
    currentclustid=-1
    
    #Clusters are initially just the two rows
    clust=[bicluster(rows[i], id=i) for i in range (len(rows))]
    
    while len(clust)>1:
        lowestpair=(0,1)
        closest=distance(clust[0].vec, clust[1].vec)
        
        #loop through every pair looking for the smallest distance
        for i in range(len(clust)):
            for j in range(i+1, len(clust)):
                #distances is the cache of distance calculations
                if (clust[i].id, clust[j].id) not in distances:
                    distances[(clust[i].id, clust[j].id)]=distance(clust[i].vec, clust[j].vec)
                
                d=distances[(clust[i].id, clust[j].id)]
                
                if d<closest:
                    closest=d
                    lowestpair=(i,j)
                
        #calculate the average of the two clusters
        mergevec=[(clust[lowestpair[0]].vec[i]+clust[lowestpair[1]].vec[i])/2.0\
                      for i in range(len(clust[0].vec))]

        #create the new cluster
        newcluster=bicluster(mergevec, left=clust[lowestpair[0]],\
                                 right=clust[lowestpair[1]],\
                                 distance=closest, id=currentclustid)

        #cluster ids that weren't there in the original set are negative
        currentclustid-=1
        print len(clust),i,j,lowestpair[0], lowestpair[1]
        del clust[lowestpair[1]]
        del clust[lowestpair[0]]
        clust.append(newcluster)
    
    return clust[0]    

def printclust(clust, labels=None, n=0):
    #indent to make a hirearchy layout
    for i in range(n): print ' ',
    if clust.id>0:
        #negative id means that its a branch
        print '-'
    else:
        #positive id means that it is an endpoint
        if labels==None: print clust.id
        else: print labels[clust.id]
    
    #now print the right and the left branches
    if clust.left!=None: printclust(clust.left, labels=labels, n=n+1)
    if clust.right!=None: printclust(clust.right, labels=labels, n=n+1)

###show time
def driver ( uris ):
    def makeRows( tokens ):
        """Only implemented in base
        """
        columns = ['uri'] 
        for token in tokens:
            columns.extend(token['tokens'])
        columns = list(set(columns))
        doc_matrix = [columns]
        for token in tokens:
            doc_matrix.append([token['uri']]+[token['text'].count(word) \
                                                  for word in columns[1:]]) 
        return doc_matrix

    class_map = { True: 'RSS', False: 'WebPage'}
    all_tokens = []
    for uri in uris:
        feed = uri[1]
        if feed and feed in ('true', 'True', 'T', 't'):
            feed = True
        #dynamic class resolution and instantiation
        instance = globals()[class_map[feed]]( uri[0] )
        all_tokens.extend(instance.runCrawler()['tokens'])
    rows = makeRows(all_tokens)
    printclust(hcluster([each[1:] for each in rows[1:]]))


if __name__ == '__main__':
    driver( [('http://steveblank.com/category/epiphany/', False),
            ('http://occ-vellore.ning.com/activity/log/list?fmt=rss', True),
            ])
    
