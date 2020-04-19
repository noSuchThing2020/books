import os, requests, datetime

from flask import Flask, session,render_template,request,redirect, url_for, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, login_required, lookup
from flask_paginate import Pagination, get_page_parameter

app = Flask(__name__)
app.config['ENV']='development'
app.config['DEBUG']=True
#app.config.from_pyfile('myconfig.cfg')


app.config["TEMPLATES_AUTO_RELOAD"] = True
# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure database URL
# Using set DATABASE_URL="VALUE" IN COMMAND Line
os.environ["FLASK_DEBUG"] = '1'
os.environ["FLASK_ENV"] = 'development'
# Check for environment variable
print(os.getenv("DATABASE_URL"))
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
print(engine)
print(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))
@app.route("/")
def index():
    recentReviews = db.execute("SELECT * FROM reviews ORDER BY id DESC LIMIT 3").fetchall()
    return render_template("index.html", reviews = recentReviews)


@app.route("/register",methods=["GET","POST"])
def register():
    if request.method == "GET":
        # If the user already logged in then we redirect the user to the homepage
        if session:
            return redirect("/")
        return render_template("register.html")
    else: 
        username = request.form.get("username")
        display_name = request.form.get("display_name")
        hash = generate_password_hash(request.form.get("password"))
        confirmation = request.form.get("confirmation")
        row = db.execute("SELECT * FROM users WHERE username = :username",{"username": username}).fetchone()
        row1 = db.execute("SELECT * FROM users WHERE display_name = :display_name",{"display_name": display_name}).fetchone()
        if not username:
            return render_template("message.html", message="You must provide a username")
        elif not display_name:
            return render_template("message.html", message="You must create a display name")
        elif row and username == row["username"]:
            return render_template("message.html", message="Your username already exists")
        elif row1 and display_name == row["display_name"]:
            return render_template("message.html", message="Your display name already exists")
        elif not request.form.get("password"):
            return render_template("message.html", message="You must provide a password")
        elif not confirmation:
            return render_template("message.html", message="You must confirm your password")
        elif request.form.get("password") != confirmation:
            return render_template("message.html", message="Your password doesn't match")
        db.execute("INSERT INTO users(username, hash, display_name) VALUES (:username, :hash, :display_name)", {"username": username,"hash": hash, "display_name": display_name})
        db.commit()
        return render_template("login.html",message = "Register successful!")

# Login route
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        # If the user already logged in, then we redirect the user to index to solve the back button issue after login page
        if session:
            return redirect("/")
        return render_template("login.html")
    else:
        username = request.form.get("username")
        row = db.execute("SELECT * FROM users WHERE username = :username",{"username": username}).fetchone()
        # Ensure username exists and password is correct
        if not row:
            return apology("invalid username and/or password", 403) 
        if  not check_password_hash(row["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)    
        session["user_id"] = row["id"]
        session["display_name"] = row["display_name"]
        session["reviewSubmitted"] = False
        print(f'The user_id is: {session["user_id"]}')
        return render_template("search.html", loggedin = "You have successfully logged in, you can start your search now!")

# Logout   
@app.route("/logout")
def logout():
    # Clear the session for the logged in user 
    session.clear()
    # Redirect the user to the index page
    return redirect("/")


# search page
@app.route("/search", methods=["GET","POST"])
@login_required
def search():
    session["reviewSubmitted"] = False
    if request.method == "GET":
        return render_template("search.html")
    else:
        searchText = request.form.get("searchText")
        if searchText == "":
            return render_template("search.html", message="Please provide a book name, isbn or author name to search!" ) 
        results=db.execute("SELECT * FROM books WHERE isbn iLIKE '%"+searchText+"%' OR title iLIKE '%"+searchText+"%' OR author iLIKE '%"+searchText+"%'").fetchall() 
        # We save the results in the session so that when user refreshes the page we don't need to get data from database again
        session["results"] = results
        session["resultCount"] = len(results)
        return render_template("search.html",searchText = searchText, results=session["results"], resultCount = session["resultCount"])

@app.route("/books/<isbn>", methods=["GET","POST"])
@login_required
def book(isbn):
    goodreads_review = lookup(isbn)
    # Make sure the book exists. 
    book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()
    if book is None:
        return render_template("error.html", message="No such book.")
    if request.method == "GET":
        userInfo = db.execute("SELECT * FROM users WHERE display_name = :display_name", {"display_name": session["display_name"]}).fetchone()
        oldReviews = db.execute("SELECT * FROM reviews WHERE isbn = :isbn ORDER BY id DESC", {"isbn": isbn}).fetchall()
        submitted = session["reviewSubmitted"]
        print(session["display_name"])
        return render_template("book.html", book=book, goodreads_review = goodreads_review, reviews = oldReviews, display_name = session["display_name"], userInfo = userInfo, submitted = submitted)
    else:
        # Preparing data for the db query
        now = datetime.datetime.now()
        user_id = session["user_id"]
        score = request.form.get("rating")
        text = request.form.get("comment")
        time = now.strftime("%m/%d/%Y, %H:%M:%S")
        checkReviews = db.execute("SELECT * FROM reviews WHERE user_id = :user_id AND isbn = :isbn", {"user_id":user_id, "isbn": isbn}).fetchall()
        if len(checkReviews) > 0:
            session["reviewSubmitted"] = True
            return redirect(url_for('book',isbn=book.isbn, message="You have already submitted!"))
        db.execute("INSERT INTO reviews(user_id, isbn, review_score, review_text, time, display_name) VALUES (:user_id, :isbn, :review_score, :review_text, :time, :display_name)",
         {"user_id": user_id,"isbn": isbn, "review_score": score , "review_text": text, "time": time, "display_name":session["display_name"]})
        db.commit()
        # Use url_for instead of render_template to avoid resubmit the form when user refresh the page
        return redirect(url_for('book',isbn=book.isbn))


# Creating API 
@app.route("/api/<isbn>", methods = ["GET"])
def bookReviewAPI(isbn):
    if request.method == "POST":
        return jsonify({"error": "Invalid method"}), 405
    else:
        bookInfo = lookup(isbn)
        book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()
        if book is None:
            return jsonify({"error": "Invalid isbn"}), 422
        else:
            return jsonify(
                {
                'title': book.title,
                'author':book.author,
                'year': book.year,
                'isbn': book.isbn,
                'work_reviews_count': bookInfo["rating_count"],
                'average_rating': bookInfo["average_rating"]
                }
            ), 200

@app.route("/api", methods = ["GET"])
def API():
    return render_template("api.html")
