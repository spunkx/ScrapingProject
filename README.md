# H1 Final Semester Scraping Project
In 2019, during my final semester, SpinelessCoder and I completed this project for work experience.
My focus was on scraping using selenium, integrating spaCy NLP, creating the engine to collate results using cosine similarity and integrating everything together. SpinelessCoder focused on the front end development with flask and researching scraping/crawling techniques.
This project took a total of 7 weeks. Which required both of us learning flask and selenium from scratch.

# H2 What it does
The idea was to make a scraper/crawler that targets information provided on a specific wordlist and presents the results on a webpage.
Capturing lots of data and storing it somewhere is not much use unless you can sift through it somehow. we used NLP and cosine similarity to sort and filter the results, much like how a search engine might do it.
### H3 Intergration High Level
Import wordlist -> run selenium -> perform NLP using spaCy on webpages -> Compare similarity of each website to wordlist -> store in mongodb
### H3 Front end
The front end uses flask as we wanted to be lightweight and low on dependencies.


## H2 Deprecated project
This project uses outdated versions of libraries and browser executables, so it is currently not recommended to be used. The intention is to archive this project for people that are interested in projects I have completed in the past.

At some point I might remake it to do something else.