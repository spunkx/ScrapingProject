#custom functions
from interface import calls
#library calls
import bson
import sys
import pprint
import re
import math
import socket
import signal
import spacy
import datetime
import time
import hashlib
import json
import binascii
import pymongo
import argparse
from pymongo import MongoClient
from random import SystemRandom
#import queue
#import multiprocessing

#https://www.tutorialdocs.com/article/python-class-dynamically.html
#https://docs.python.org/fr/3/library/wsgiref.html#module-wsgiref
#https://www.rfc-editor.org/rfc/pdfrfc/rfc7540.txt.pdf
#explore usage of queues
#useful information

#spacy training https://spacy.io/usage/training#ner

#doesn't need to be in a class, is just a clean way of doing it


#doesn't need to be in a class
class sockConnection(object):
    def __init__(self, ipAddress, port):
        self.ipAddress = ipAddress
        self.port = port
    
    def setSocket(self):
        newSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        newSock.bind((self.ipAddress, self.port))

        return newSock

#A query object is the thing that is searched initially
#A query object may have one or many EntityProfiles
class Query(object):
    def __init__(self, _queryId, query, queryTimeStamp, websiteSelection, contents, wordList):
        self._queryId = _queryId
        self.query = query
        self.queryTimeStamp = queryTimeStamp
        self.websiteSelection = websiteSelection
        self.contents = contents
        if contents != None:
            entityInfo = []
            entityList = []
            frequencies = []
            intFrequencies = []
            entitIds = []
            #loop through each website to visit in order to
            #generate the EntityProfile objects
            for webite in websiteSelection:
                for content in contents[0]:
                    #self.searchForEmails(currContents)

                    #call the entity list function and append the return
                    #to a list
                    currProfile = self.getEntityList(webite, content, wordList)
                    frequencies = currProfile.frequencies
                    #pnounFrequencies = currProfile.frequencyPnoun
                    entityInfo.append(currProfile.getCurrEntity())
                    entityList.append(currProfile.__dict__)
                    #print("Here are my unique list of pnouns", pnounFrequencies)
                    vectorSet = self.getIntFreqencies(frequencies)
                    intFrequencies.append(vectorSet[1])
                    entitIds.append(vectorSet[0])
                    #so if I have 5 vectors, the cosine similarity for vector 1 is located at location 0 in the list
            
            aunitVect = []
            #same thing as test script
            if(wordList != None):
                #pseudo ranking is getting the sum of the frequency and ordering it from highest to lowest
                #this is to create vectors of equal length. It is not the best approach
                pseduoRanked = self.pseudoRank(intFrequencies)
                #this will convert the vectors to unit vectors through normalisation
                vects = []
                indexes = []
                for vect in range(len(pseduoRanked)):
                    vects.append(pseduoRanked[vect][1])
                    indexes.append(pseduoRanked[vect][0])

                unitVects = self.getUnitVects(vects)
                #this is a list of all the angles between all the vectors
                thetasbetwVects = self.getTheta(unitVects, indexes, entitIds)

            else:
                print("No wordlist specified")

            rankedAngles = thetasbetwVects
            self.rankedAngles = rankedAngles
            self.matchedEntities = self.matchEntities(rankedAngles, entitIds)
            self.groupedEntities = self.groupEntities(self.matchedEntities)

            self.entityInfo = entityInfo
            self.entityList = entityList


    def groupEntities(self, matchedEntities):
        groupedEntities = []
        for i in range(len(matchedEntities)):
            decision = []
            for j in range(len(matchedEntities[i][2])):
                #print("test", matchedEntities[i][2][j])
                if matchedEntities[i][1][0] == matchedEntities[i][2][j][0]:
                    continue
                else:
                    decision.append((matchedEntities[i][2][j][0], self.similarityPicker(matchedEntities[i][2][j][1])))

            groupedEntities.append((matchedEntities[i][1], decision))

        return groupedEntities


    #1-10 Very High Similiarity
    #11-25 High Similiarity
    #26-40 Medium Similiarity
    #41-70 Low Similiarity
    #71-89 Very Low Similiarity
    #90 No Similarity
    def similarityPicker(self, angle):
        decision = ""
        if angle > 0.0 and angle < 10.0:
            decision = "Very High Similiarity"
        elif angle > 10.0 and angle < 26:
            decision = "High Similiarity"
        elif angle > 25 and angle < 41:
            decision = "Medium Similiarity"
        elif angle > 40 and angle < 71:
            decision = "Low Similiarity"
        elif angle > 70 and angle < 90:
            decision = "Very Low Similiarity"
        elif angle == 90:
            decision = "No Similiarity"
        else:
            decision = "How did that happen"
            
        return decision


    def matchEntities(self, rankedAngles, entitIds):
        matchedEntities = []
        pairedEntities = []
        for i in range(len(entitIds)):
            for j in range(len(rankedAngles)):
                if(i == rankedAngles[j][0]):
                    matchedEntities.append((rankedAngles[j][0], rankedAngles[j][1][0], rankedAngles[j][1]))
        return matchedEntities

    def getTheta(self, unitVects, indexes, entitIds):
        
        maxVectors = len(unitVects)
        controlMaxVectors = maxVectors
        totalElements = len(unitVects[0])

        vectCount = 0
        iterator = 0
        counter = 0

        #calculate all the operations to be performed by the dot product operation (a*b) is two operations, and (a*b)+(b*c) is (2*1)*2 opertions
        totalOperations = int(0.5 * float(maxVectors) * (maxVectors + 1))
        allThetas = []
        thetas = []
        while iterator != totalOperations:
            product = 0

            if counter == controlMaxVectors:
                #this is to ensure that elements aren't calculated twice (see documentation)
                vectCount+=1
                counter = vectCount
                allThetas.append(thetas)
                thetas = []
            for integer in range(totalElements):
                #dot product calculation

                #NOTE -DANGER- FOR ALL FUTURE PEOPLE THIS HAS A SERIOUS FLAW -DANGER-
                #THIS IS FLOATING POINT OPERATION AND IS CUMLATIVE
                #THEREFORE THE ACCURACY WILL DECREASE WITH EVERY OPERATION
                #DO NOT USE THIS FOR ANYTHING LIFE-CRITICAL UNTIL THE FLOATING POINT ERROR IS FIXED
                product = product + (unitVects[vectCount][integer] * unitVects[counter][integer])
                if vectCount == counter and integer == totalElements-1 and product == 0:
                    product = 1.0


            #calculating the angle of theta which is the angle between two vectors
            #math.acos is to radians and math.degrees converts it to degrees
            #thetas.append(round(math.degrees(math.acos(round(product, 12))), 4))
            thetas.append((entitIds[counter],round(math.degrees(math.acos(round(product, 12))), 4)))
            counter+=1
            iterator+=1
        #this is to show which entities are associated with which values
        allThetas.append(thetas)
        thetasIndex = list(zip(*[[x for x in indexes], [y for y in allThetas]]))
        #return list of theta angles
        return thetasIndex


    def getUnitVects(self, pseduoRanked):
        unitVects = []
        for i in range(len(pseduoRanked)):
            vectMag = 0
            powOperationList = []
            for j in range(len(pseduoRanked[i])):
                #square all elements in list 
                powOperationList.append(math.pow(pseduoRanked[i][j],2))

            #sum all elements and sqrt them to get the magnitude
            vectMag = math.sqrt(sum(powOperationList))
            aunitVect = []
            for j in range(len(pseduoRanked[i])):
                if vectMag != 0 and pseduoRanked[i] != 0:
                    #normalise all elements in the list by dividing them by the magnitude
                    unitvectEle = pseduoRanked[i][j] / vectMag
                    aunitVect.append(unitvectEle)
                    #if the unitVector is equal to 1 as a magnitude, it is right
                elif vectMag == 0 and pseduoRanked[i][j] == 0:
                    #append 0 if mags are 0, to avoid dividing by 0
                    unitvectEle = pseduoRanked[i][j]
                    aunitVect.append(unitvectEle)
                    
            unitVects.append(aunitVect)
            #return a list of unit vectors
        return unitVects

    
    def pseudoRank(self, frequencies):
        vectorSums = []
        for i in range(len(frequencies)):
            vectorSums.append(sum(frequencies[i]))
        #enumberates and sorts the vectors, (why enum? this is to ensure each elements is assoicated with a key)
        enumSortedVects = [(i[0],i[1]) for i in sorted(enumerate(vectorSums), key=lambda x:x[1], reverse=True)]

        arrangedVectors = []
        listIndexes = []
        rankedVectors = []
        for i in range(len(frequencies)):
            #append the value to the arrangedVectors list
            arrangedVectors.append(frequencies[enumSortedVects[i][0]])
            listIndexes.append(enumSortedVects[i][0])
        
        rankedVectors = list(zip(listIndexes, arrangedVectors))
        return rankedVectors


    def getIntFreqencies(self, frequencies):
        frequencyInteger = []
        integerFrequencies = []
        entityId = frequencies[0]
        for element in range(len(frequencies)):
            if element == 0:
                continue
            else:       
                frequencyInteger.append(int((frequencies[element].split("|"))[1]))
                #all frequencies, regardless of parent array
                #get the word part of the split as well
        
        return (entityId, frequencyInteger)

    #this is to display the current entity(ies)
    def getEntityList(self, webite, currContents, wordList):
        print("Creating Entity please wait...")
        newProfile = EntityProfile(self._queryId, self.query, self.queryTimeStamp, currContents, webite, False, wordList)
        return newProfile

    def insertQuery(self, currQuery, dbConnection):
        valueBeingInserted = dbConnection.insert_one(currQuery)
        print("Query value inserted into db!", valueBeingInserted)

    def insertEntity(self, currProfile, dbConnection):
        valueBeingInserted = dbConnection.insert_one(currProfile)
        print("Entity value inserted into db!", valueBeingInserted)



#The EntityProfile is each "page" that is queried and the results returned from that specifc page
#A query may have one or many entities. The greater then websites, the greater the entities
#people objects are constructed from their presence on each EntityProfile
class EntityProfile(object):
    def __init__(self, _queryId, query, queryTimeStamp, contents, websiteType, isSignedIn, wordList):
        nlp = spacy.load("en_core_web_sm")
        self._queryId = _queryId
        self.query = query
        self.queryTimeStamp = queryTimeStamp
        self.aboutContents = self.getAboutContents(contents)
        self.posts = self.getPosts(contents)
        self.propperNouns = self.getProperNouns(self.posts, self.aboutContents, nlp)
        #self.adjectives = getAdjectives(posts, aboutContents, noun)
        self.websiteType = websiteType
        self.isSignedIn = False
        self.profileOwner = self.getOwner(self.aboutContents, nlp)
        self.EntityId = self.getUniqueIdentifier(self.profileOwner)
        self.frequencies = self.getWordFrequency(self.propperNouns, wordList, self.EntityId)
        #use the poppernouns as its own wordlist to get a unique list of each word for non-wordlist correlation
        #self.frequencyPnoun = self.getWordFrequency(self.propperNouns, self.propperNouns, self.EntityId)


    #this will count the amount of times words appear
    def getWordFrequency(self, propperNouns, wordList, EntityId):
        frequencies = []
        freqCounter = 0
        frequencies.append(EntityId)
        for j in range(len(wordList)):
            for i in range(len(propperNouns)):
                if wordList[j].lower() == propperNouns[i].lower():
                    freqCounter += 1

            frequencies.append(str(wordList[j]) + "|" + str(freqCounter))

        return frequencies


    def getOwner(self, aboutContents, nlp):
        nameIndex = 0
        nameList = []
        for i in range(len(aboutContents)):
            if aboutContents[i] == "name":
                nameList.append(aboutContents[1])
            if "name" not in aboutContents:
                nlpAbout = nlp(str(aboutContents))
                for aboutToken in nlpAbout.ents:
                    if aboutToken.label_ == "PERSON":
                        nameList.append("Spacy Detected: " + str(aboutToken.label_) + " " + str(aboutToken.text))
        return nameList


    #code rep, good idea to make a generic Identifer creator rather then a copy of the other one
    def getUniqueIdentifier(self, string):
        timeStamp = getTimeStamp()
        cryptoSecGen = SystemRandom()
        secureSeed = str([cryptoSecGen.randrange(100) for i in range(10)])
        sha1Hash = hashlib.sha1()
        sha1Hash.update(str(string).encode())
        sha1Hash.update(timeStamp.encode())
        sha1Hash.update(secureSeed.encode())
        uid = binascii.hexlify(sha1Hash.digest()).decode()

        return uid


    def getAboutContents(self, contents):
        aboutContents = []
        for content in contents:
            if content == 'tweets:':
                break
            aboutContents.append(content)
        return aboutContents

    def getPosts(self, contents):
        posts = []
        for i in range(6,len(list(contents))):
            posts.append(list(contents)[i])

        return posts

    def getCurrEntity(self):
        entityInfo = str(self._queryId) + ", " + str(self.query) + ", " + str(self.websiteType) + ", " + str(self.propperNouns)
        return entityInfo

    def getProperNouns(self, posts, aboutContents, nlp):
        #explore dictionary options
        #be sure to install spacy and install
        #en_core_web_sm
        properNouns = []
        
        nlpPosts = nlp(str(posts))
        nlpAbout = nlp(str(aboutContents))

        for aboutToken in nlpAbout:
            if aboutToken.pos_ == "PROPN":
                properNouns.append(aboutToken.text)

        for postToken in nlpPosts:
            if postToken.pos_ == "PROPN":
                properNouns.append(postToken.text)
        
        return properNouns

    

def createObjects(query, fetchedData, sites):
    #idealy wordList will be a file... but I didn't have time
    wordList = ["perth", "WA", "western australia"]
    dbConnection = pymongo.MongoClient("mongodb://localhost:27017/")
    print("Creating collections...\n")
    #creating mongodb connections
    db = dbConnection["FootPrint"]
    peopleCollection = db["People"]
    ProfileEntities = db["ProfileEntities"]
    Queries = db["Queries"]
    #PasteBin = db["PasteBin"]

    timeStamp = getTimeStamp()
    #below is object creation
    currQuery = Query(queryUid, query, timeStamp, sites, fetchedData, wordList)
    currEntityList = currQuery.entityList
    queryDict = currQuery.__dict__
    currQuery.insertQuery(queryDict, Queries)
    for qDic in currEntityList:
        currQuery.insertEntity(qDic, ProfileEntities)

    
        
def doExtract(query, numOfImg, websiteList):
    dataList = calls(query, numOfImg, websiteList)
    #print("MetaData: ", dataList[0])
    return dataList


def clientConnector():
    #to join the clientConnector with the __name___:
    #fork the thread before client connector is called
    #when recieved information is finished from the client
    #pipe the information to the parent thread running the server
    #keep the child thread of clientConenction open to accept input
    #if the server is running the doExtract, que up the new querys until
    #server has finished its business
    userEntry = []
    ipAddress = '127.0.0.1'
    port = 1337
    newSockConnection = sockConnection(ipAddress,port)
    currSock = newSockConnection.setSocket()
    currSock.listen(5)
    while True:
        c, addr= currSock.accept()
        print("Recieved Connection from", addr)
        c.send(b'welcome client!\n')
        c.send(b'Enter your query for a thing: \n')
        userEntry.append(c.recv(1024).decode())
        c.send(b'Set image limit: \n')
        userEntry.append(c.recv(1024).decode())
        break
    c.close()
    return userEntry


def getTimeStamp():
    ts = time.time()
    st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    return st

#it is necessary to create an identifier that doesn't "collide" with
#another identifier. This is to identify each query.
#this function is likely overkill, but it illistrates an important
#point when it comes to identifiers and by extension, security
def getUniqueIdentifier(string):
    timeStamp = getTimeStamp()
    #Cryptographic pseudo-random number generator (CPRNG) to get a UID
    #overly secure uid, possibly remove later for performance reasons
    cryptoSecGen = SystemRandom()
    secureSeed = str([cryptoSecGen.randrange(100) for i in range(10)])
    sha1Hash = hashlib.sha1()
    sha1Hash.update(string.encode())
    sha1Hash.update(timeStamp.encode())
    sha1Hash.update(secureSeed.encode())
    uid = binascii.hexlify(sha1Hash.digest()).decode()

    return uid

if __name__ == "__main__":
    print("Welcome to the backend!\n")
    
    #function calls are here to centralise all I/O to functions
    fetchedData = []
    userEntry = clientConnector()

    #userEntry[0] will access the query and userEntry[1] will access the number of images to download
    queryUid = getUniqueIdentifier(userEntry[0])
    timeStamp = getTimeStamp()
    sites = ["twitter.com"]
    fetchedData = doExtract(userEntry[0], userEntry[1], sites)
    createObjects(userEntry[0], fetchedData, sites)
    
