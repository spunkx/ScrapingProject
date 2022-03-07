#custom classes
#custom functions
from dataExtractor import downloadImages
from dataExtractor import extractMetaData
from dataExtractor import grabHtmlSource
from dataExtractor import duckDuckGoSearch
#library calls
import time
#import multiprocessing


#why use an interface?
#It is a nice logical separation that makes handling the data
#between the two different scripts easy and neat
#particuarly when concurrency is concerned

def calls(query, imgLimit, sites):
    gotData = []
    #downloadImages(query, int(imgLimit))
    #extractMetaData(query)
    duckData = duckDuckGoSearch(query, sites)
    
    webSitestoVisit = []
    for url in list(duckData[1]):
        webSitestoVisit.append(url)

    gotData.append(grabHtmlSource(query, webSitestoVisit))

    #print("This is the gotDAta", gotData)
    #also data from html object
    return gotData


if __name__ == '__main__':
    calls()