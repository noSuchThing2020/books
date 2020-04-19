import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

os.environ["DATABASE_URL"] = 'postgresql://postgres:Amadeus@123@localhost/books'
#engine = create_engine("postgres://ocnbwkgoujtzqa:46cf6de0b76cfab36d06d62c9379c192bcb179e6fce5d8daebbdbf9205b967d8@ec2-18-209-187-54.compute-1.amazonaws.com:5432/dcqatei2rpi1ma")
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

"""
isbn,title,author,year

CREATE TABLE books (
      isbn VARCHAR NOT NULL,
      title VARCHAR NOT NULL,
      author VARCHAR NOT NULL,
      year INTEGER NOT NULL
);

"""

def main():
    f = open("books.csv")
    reader = csv.reader(f)
    for isbn, title, author, year in reader:
        db.execute("INSERT INTO books(isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
        {"isbn": isbn, "title": title, "author": author, "year": year})
        print(f"Added books  {title} by {author} from {year}.")
    db.commit()



if __name__ == "__main__":
    main()
