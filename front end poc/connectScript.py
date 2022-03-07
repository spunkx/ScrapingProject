import pymongo #this package is the backbone of the integration of the database and the web-server
import subprocess
import hashlib
import binascii
from pymongo import MongoClient #mongoclient is what allows the http server to connect to the 
from flask import  render_template, Flask, request #relevant flask packages we will utilize


app = Flask(__name__)  #instantiate a flask class object titled app
client = pymongo.MongoClient("mongodb://localhost:27017/")  #connection to mongoDB is made, localhost is the hostname, 27017 is the port. Refer to your mongoDB client pre-connection to ensure details are correct.
mydb = client["FootPrint"] #connect to the footprint database, this DB is what is used throughout the project. this is global as it allows for many functions to access the one same connection.
queries = mydb['Queries']


#notice how everything below has an "app" preceding the route?; it all belongs to this one project!

@app.route("/", methods=['GET','POST']) #route for URL i.e. https:linktosite/  <--- this is the link to visually see this function in a web browser.
def home():  #function definition, things could be done differently.
    return render_template('home.html') #the render_template() function will return a webpage corresponding to the route defined with the variables mentioned and displayed. SEE HTML file for more info.


@app.route("/searchPage", methods=['GET','POST'])
def index():

    queries = mydb['Queries']
    queryData = list(queries.find()) #convert table into a list of dictionary, thus python operations could be easily applied.

    return render_template('searchPage.html', queryData=queryData)
#view index.html for more information to see how the data here aligns and is presented visually within index.html

@app.route("/table", methods=['GET', 'POST']) 
def twitterData(): 
    profiles = mydb['ProfileEntities'] #connect to the collection we need data from
    Data = list(profiles.find({"websiteType": "twitter.com"})) #dump the data from the db as a list of dictionary for easy interaction. Filter to find "twitter.com" for the field "websiteType"
    #easy way to filter data ^ ; read this for more info; https://docs.mongodb.com/manual/tutorial/query-documents/
    #if find command used correctly it will be in the correct data format to be used on the front end
    tableHeaders = ['name', 'alias','url']
    entityInfo = ['Name','Alias','Bio','Location','Media count','Join date','Url']
    queryInfo = ['Entity ID', 'Website','Query Term','Query timestamp']
    queryData = list(queries.find())

    #explicit declaration of a list with which the data we have will populate; can be done another way.
    queryData = list(queries.find())
    return render_template('table.html', Data=Data, tableHeaders=tableHeaders, tbHeaderLength=len(tableHeaders), dataLength=len(Data), \
    queryInfo=queryInfo, entityInfo=entityInfo, queryData=queryData)
    #passing more variables to display visually on the front end

if __name__ == '__main__': #program will jump here to execute instructions 
    app.run(debug=True, port=31337) #set the port on which you'd like to run, left debugging on to see incase things go wrong.
