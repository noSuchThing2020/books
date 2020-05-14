# Project 1

Web Programming with Python and JavaScript

##### Course Link:
##### https://cs50.harvard.edu/web/2018/

##### Deployed to Heroku:

##### https://book-fun.herokuapp.com/

## Main Features
* Register
* Search books by name, author or ISBN
* Get info about a book and submit your own review!

##### Personal touch
* API call page and execution Example
* Scroll top function
* Display recent reviews on the homepage(No login needed)

## Setup 

##### Clone repo
$ git clone https://github.com/me50/noSuchThing2020.git

##### Create a virtualenv 
$ python3 -m venv myvirtualenv

##### Activate the virtualenv
$ venv/bin/activate

##### Install all the softwares required
$ pip install -r requirements.txt

######  Set ENV Variables
$ export FLASK_APP = application.py

$ export DATABASE_URL = Heroku Postgres DB URI(You can get a free addon database on Heroku)

$ export API_KEY = Goodreads API Key(You have to register on goodreads to get your own key). 

##### Start on your localhost
$ flask run
