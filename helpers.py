import os
import requests
import urllib.parse

from flask import redirect, render_template, request, session
from functools import wraps


def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def lookup(isbn):
    """Look up review info for book."""

    # Contact API
    try:
        #api_key = os.environ.get("API_KEY")
        api_key = "S730F93eVFnTGMA613bRUQ"
        """ We set verify to False as there is an API certificate issue, We should remove"verify = False" in normal cases """
        #response = requests.get(f"https://cloud-sse.iexapis.com/stable/stock/{urllib.parse.quote_plus(symbol)}/quote?token={api_key}", verify=False)
        response = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": api_key, "isbns": isbn}, verify=False)
        response.raise_for_status()
    except requests.RequestException:
        return None
 
    # Parse response
    try:
        book_infos = response.json()
        return {
            "rating_count": book_infos["books"][0]["work_ratings_count"],
            "average_rating": book_infos["books"][0]["average_rating"]
        }
    except (KeyError, TypeError, ValueError):
        return None


