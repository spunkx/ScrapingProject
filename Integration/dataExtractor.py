#library calls
import os
import re
import random
import time
import sys
import json
import urllib
import piexif
import piexif.helper
import urllib.request
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from google_images_download import google_images_download
response = google_images_download.googleimagesdownload()


#add stego functionality at some point

#--------generic functions--------

#def searchProfileType(arg):
#    if arg == ...:
#        call get

def getImageExtension():
    #must remember to do different methods for gifs and png!
    imageExtension = ["jpg"]
    #allow specification of image extension later
    #imageExtension.append(arg)

    return imageExtension

#--------download images--------

def divdeNumber(numExtensions, numOfImgToDL):
    #get the distribution for each image for the number of extensions
    divideResult = numOfImgToDL // numExtensions

    return divideResult


def getRemainder(numExtensions, numOfImgToDL):
    #get the remainder to do the final distribution
    modResult = numOfImgToDL % numExtensions

    return modResult

def downloadImages(query, imgDLNum):
    #specify the extenstions for image download

    imageExtension = getImageExtension()
    numExtensions = len(imageExtension)
    divideResult = divdeNumber(numExtensions, imgDLNum)

    #get the remainder to add onto the most common image extension
    remainder = getRemainder(numExtensions, imgDLNum)

    #the google image include does magic things!!
    for i in range(len(imageExtension)):
        if(i == (numExtensions - 1)):
            arguments = {
                "keywords": query,
                "format" : imageExtension[i],
                "limit" : divideResult + remainder,
                "print_urls":True,
                "size" : "medium",
            }
        else:
            arguments = {
                "keywords": query,
                "format" : imageExtension[i],
                "limit" : divideResult,
                "print_urls":True,
                "size" : "medium",
            }
        response.download(arguments)


#--------extract image metadata--------

#prior index everything, place previous info into different folder

#checkIfMdExists

#getImageHash

def getAllImages(directory):
    imageExtensions = getImageExtension()

    allImages = []
    #os.getcwd() this gets where to start the search from
    rootDir = os.getcwd()
    #os.walk goes from the rootDir and starts at a point within the root dir
    #topdown=True works from the root node and works its way to the children (topdown)
    fullDir = "downloads\\" + directory
    for directory, subDirectory, listOfFiles in os.walk(fullDir, topdown=True):
        for fileName in listOfFiles:
            #find way around 3 for loop
            for extension in imageExtensions:
                allImages.append(fileName)
    return allImages


def dumpJson(tagDictionary):
    jsonString = json.dumps(tagDictionary, indent=4)
    return jsonString

#load the exif data
#The exif tool used does magic things!
#it is worth noting that google image also does a little bit of this
#but it is not as rich as this library
def readImage(imageName, dirName):
    try:
        os.chdir('downloads')
    except:
        print("ERROR: downloads file doesn't exist\nExiting Gracefully...")
        sys.exit(1)
    os.chdir(dirName)
    try:
        exif_dict = piexif.load(imageName)
    except:
        exif_dict = {}
    os.chdir('..')
    os.chdir('..')
    return exif_dict

#reverse a string so that the extension removal is more efficient
#extensions are towards the end of a string

def reverse(aString):
    reversedString = "".join(reversed(aString))
    return reversedString

def removeExtension(imageName):
    reversedImageName = reverse(imageName)
    #reversedImageName.spilt('.', 1)[1] -> split the image at the...
    #dot and grab the second half of the split
    #unreverse the image name
    imageNameNoExtension = reverse(reversedImageName.split('.', 1)[1])
    return imageNameNoExtension

#write metadata to file
def writeMDtoFile(dirName, imageName, data):
    try:
        os.chdir('metaZone')
    except:
        os.mkdir('metaZone')
        os.chdir('metaZone')
    try:
        os.chdir(dirName)
    except:
        os.mkdir(dirName)
        os.chdir(dirName)
    imageName = imageName + ".json"
    f = open(imageName, "w")
    f.write(data)
    f.close
    os.chdir('..')
    os.chdir('..')


def extractMetaData(dirName):
    #query is dirName
    print("Extracting MetaData...")
    allImageNames = getAllImages(dirName)
    for imageName in allImageNames:
        exif_dict = readImage(imageName, dirName)
        if exif_dict == {}:
            continue
        tagDictionary = {}
        for ifd in ("0th", "GPS", "1st", "Interop", "Exif"):
            for tag in exif_dict[ifd]:
                tags = piexif.TAGS[ifd][tag]['name']
                data = exif_dict[ifd][tag]

                tagDictionary.update({tags : str(data)})
                jsonString = dumpJson(tagDictionary)
                noexImageName = removeExtension(imageName)
                writeMDtoFile(dirName, noexImageName, jsonString)

    print("done!")

#--------entry points--------

#----duckduckgoSearch----
def duckDuckGoSearch(query, site):
    duckDuckGoSearch = []
    chromeOptions = Options()
    chromeOptions.add_argument("--headless")
    driver = webdriver.Chrome('chromedriver.exe', options=chromeOptions)
    driver.get("https://duckduckgo.com/?" + urllib.parse.urlencode({'q' : query + ' ' + ' '.join(["site:" + s for s in site])}))

    try:
        resultsList = driver.find_elements_by_xpath('//div[@class="result results_links_deep highlight_d result--url-above-snippet"]')
    except:
        print("No Results returned")

    title = []
    url = []
    desc = []
    for i in resultsList:
        x = i.text.split("\n")
        title.append(x[0])
        url.append(x[1])
        try:
            desc.append(x[2])
        except:
            desc.append(None)

    duckDuckGoSearch.append(title)
    duckDuckGoSearch.append(url)
    duckDuckGoSearch.append(desc)
    return duckDuckGoSearch

#--------html extract--------


def grabHtmlSource(query, sites):
    returnedResults = []
    # try:
    #     #change directory
    #     os.chdir("htmlsource")
    # except:
    #     #make and change directory
    #     newFolder = os.mkdir("htmlsource")
    #     os.chdir("htmlsource")
    accessAlias = -1
    #         try:
    #             open("{}.html".format(site[7:]), "r")
    #         except:
    try:
        urllib.request.urlretrieve("http://twitter.com/{}".format(query.strip()),"{}.html".format(query))
        accessAlias = 0
    except:
        accessAlias = -1
    #                 #urllib.request.urlretrieve("http://linkedin.com/{}".format(query),"{}.html".format(query))
    #                 #urllib.request.urlretrieve("http://au.linkedin.com/{}".format(query),"{}.html".format(query))
    #                 #urllib.request.urlretrieve("http://facebook.com/{}".format(query),"{}.html".format(query))
    #             except:
    #                 #this is to prevent false positives
    #                 print("This is the site info", site)
    #                 urllib.request.urlretrieve("{}".format(site), "{}.html".format(str(site[7:])))

    #             urllib.request.urlretrieve("{}".format(site), "{}.html".format(str(site[7:])))

    if(accessAlias == 0):
        if ("https://twitter.com/{}".format(query)) not in sites:
            sites.insert(0,("https://twitter.com/{}".format(query)))

    print("here's the sites we will visit", sites)
    for site in sites:
        returnedResults.append(selTwitterHtmlScroll(query, site))

    os.chdir('..')

    return returnedResults


#----facebook extract-----

#----twatter extract----

#--twatter nosignin--

#this will do the tag extraction using BeautifulSoup



def selTwitterHtmlScroll(query, site):
    chromeOptions = Options()
    chromeOptions.add_argument("--headless")
    driver = webdriver.Chrome('chromedriver.exe', options=chromeOptions)
    
    
    driver.get(site)

    tweetList = []

    SCROLL_PAUSE_TIME = 0.1

    #the try catch is to see if this element exists first
    try:
        personalName = driver.find_element_by_xpath("//h1[@class='ProfileHeaderCard-name']/*").text
        #if the element does exist and is not blank, append
        tweetList.append("name")
        tweetList.append(str(personalName))
    except:
        tweetList.append(None)

    try:
        alias = driver.find_element_by_xpath("//a[@class='ProfileHeaderCard-screennameLink u-linkComplex js-nav']").text
        tweetList.append("alias")
        tweetList.append(str(alias))
    except:
        tweetList.append(None)

    try:
        bio = driver.find_element_by_xpath("//p[@class='ProfileHeaderCard-bio u-dir']").text
        tweetList.append("bio")
        tweetList.append(str(bio.strip('\n')))
    except:
        tweetList.append(None)

    try:
        location = driver.find_element_by_xpath("//span[@class='ProfileHeaderCard-locationText u-dir']").text
        tweetList.append("location")
        tweetList.append(str(location))
    except:
        tweetList.append(None)

    try:
        mediaCount = driver.find_element_by_xpath("//a[@class='PhotoRail-headingWithCount js-nav']").text
        tweetList.append("mediaCount")
        tweetList.append(str(mediaCount))
    except:
        tweetList.append(None)

    try:
        joinDate = driver.find_element_by_xpath("//span[@class='ProfileHeaderCard-joinDateText js-tooltip u-dir']").text
        tweetList.append("joinDate")
        tweetList.append(str(joinDate))
    except:
        tweetList.append(None)
   
    try:
        url = driver.find_element_by_xpath("//span[@class='ProfileHeaderCard-urlText u-dir']/*").text
        tweetList.append("url")
        tweetList.append(str(url))
    except:
        tweetList.append(None)

    try:
        verification = driver.find_element_by_xpath("//span[@class='ProfileHeaderCard-badges']/*/*/*").text
        tweetList.append("verification")
        tweetList.append(str(verification))
    except:
        tweetList.append(None)

    lastHeight = driver.execute_script("return document.body.scrollHeight")
    scrollLimit = 0
    tweetList.append("tweets:")

    while scrollLimit != 3:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)

        # Calculate new scroll height and compare with last scroll height
        newHeight = driver.execute_script("return document.body.scrollHeight")
        if newHeight == lastHeight:
            break
        lastHeight = newHeight
        scrollLimit += 1
    tweetOBJ = driver.find_elements_by_xpath("//li[@data-item-type='tweet']")
    for i in tweetOBJ:
        #tweetID = i.find_element_by_xpath(".//*[@data-item-id]").text
        tweetText = i.find_element_by_xpath(".//p").text
        #tweetStuffConcat = tweetID + (tweetText.replace('\n', '').strip('\n'))
        tweetList.append(tweetText.replace('\n', '').strip('\n'))

    return tweetList


'''
def getTwatterHtml(query):
    twitterPage = []
    with open ("{}.html".format(query), encoding="utf-8") as twitterHTML:
        requestDict = {'requestURL' : '', 'requestType' : '', 'target' : '', 'profile' : {'name' : '', 'url' : '', 'DoB' : ''},'tweets':''}
        #Store the data derived in the above dictionary
        data = twitterHTML.read()
        soup = BeautifulSoup(data, 'html.parser')

        twitterProfileDetails = soup.find("div","ProfileHeaderCard")
        twitterProInfo = []
        if twitterProfileDetails != None:
            for string in twitterProfileDetails.stripped_strings:
                twitterProInfo.append(string)
        else:
            pass

        fixedElements = fixElements(twitterProInfo)
        twitterPage = fixedElements
        twitterPage.append("tweets:")

        timeline = soup.select('#timeline li.stream-item')
        for tweet in timeline:
            tweetID = tweet['data-item-id'] #attribute selection 
            tweetText = tweet.select('p.tweet-text')[0].get_text()
            tweetString = tweetID + " - " + tweetText
            twitterPage.append(tweetString)
    return twitterPage

'''



#--twatter signin--


#----linkedin extract----


#----alternative extract----
'''
def pasteBin():
    pasteBinText = []
    chromeOptions = Options()
    chromeOptions.add_argument("--headless")
    driver = webdriver.Chrome('D:\\OChewai0\\Downloads\\chromedriver_win32\\chromedriver.exe', options=chrome_options)

    driver.get('https://pastebin.com/search?q="{}"'.format(Query))

    head = driver.find_elements_by_xpath("//div[@class='gs-webResult gs-result']")

    URList = []
    for i in head:
        url = i.find_element_by_xpath(".//div[@class='gs-bidi-start-align gs-visibleUrl gs-visibleUrl-long']")
        URList.append(url.text)

    if len(URList) > 0:
        x = len(URList)
        additionalURL = x - 1
        URList.pop(additionalURL)
        print("Congrats, we found something! (your URLs) \n", URList)
    
    else:
        print("Nothing matches the exact search term you're looking for :( ")

    if len(URList) > 0:
        loopChoice = input(str("Would you like to loop through the URL(s) you may have just found in the list?\n1 for yes\n2 for no\n> "))
        if loopChoice == "1":
            for link in URList:
                driver.get("{}".format(link))
                Rawtext = driver.find_elements_by_xpath("//textarea[@id='paste_code']")
                for i in Rawtext:
                    purifiedText = i.text
                fullText = purifiedText+ " is from " + link
                pasteBinText.append(fullText)
        elif loopChoice == "2":
            print("we hope you enjoyed this service. bye")
    print("The content of pasteBinText is: \n", pasteBinText)
'''
