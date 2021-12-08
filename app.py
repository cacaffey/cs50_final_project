import io
import csv

from cs50 import SQL
from flask import Flask, redirect, render_template, request, session, Response
from flask_session import Session
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import date

from helpers import apology, login_required

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///zhournalism.db")

# Create all SQL tables 
def setup_sqlite_tables(): 
    # Table: users
    db.execute("CREATE TABLE IF NOT EXISTS users ( \
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, \
                username TEXT NOT NULL, \
                password TEXT NOT NULL, \
                hsk_level NUMERIC)")

    db.execute("CREATE INDEX IF NOT EXISTS users_username \
                ON users(username)")

    # Table: all ingested HSK data
    db.execute("CREATE TABLE IF NOT EXISTS hsk_data ( \
                id INTEGER PRIMARY KEY NOT NULL, \
                hsk_level INTEGER NOT NULL, \
                hanzi TEXT NOT NULL, \
                pinyin TEXT NOT NULL, \
                translations TEXT NOT NULL)")

    db.execute("CREATE INDEX IF NOT EXISTS hsk_data_hanzi \
                ON hsk_data(hanzi)")

    # Table: scraped RSS feeds from People's Daily and NYT
    db.execute("CREATE TABLE IF NOT EXISTS rss_items ( \
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, \
                source TEXT NOT NULL, \
                title TEXT NOT NULL, \
                tokenized_title TEXT, \
                highest_hsk_level INTEGER, \
                pub_date TEXT NOT NULL, \
                link TEXT NOT NULL)")

    db.execute("CREATE INDEX IF NOT EXISTS rss_items_highest_hsk \
                ON rss_items(highest_hsk_level)")

    # Table: log of all user-viewed headlines
    db.execute("CREATE TABLE IF NOT EXISTS user_headline_history ( \
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, \
                user_id INTEGER NOT NULL, \
                date_viewed TEXT NOT NULL, \
                headline_id INTEGER NOT NULL, \
                FOREIGN KEY(headline_id) REFERENCES rss_items(id), \
                FOREIGN KEY(user_id) REFERENCES users(id))")

    db.execute("CREATE INDEX IF NOT EXISTS user_and_headline_id_headline_history \
                ON user_headline_history(user_id, headline_id)")

    # Table: log of all user-saved vocabulary
    db.execute("CREATE TABLE IF NOT EXISTS user_vocab_history ( \
                id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, \
                user_id INTEGER NOT NULL, \
                vocab_id INTEGER NOT NULL, \
                FOREIGN KEY(vocab_id) REFERENCES hsk_data(id), \
                FOREIGN KEY(user_id) REFERENCES users(id))")

    db.execute("CREATE INDEX IF NOT EXISTS user_and_vocab_id_vocab_history \
                ON user_vocab_history(user_id, vocab_id)")


# Execute function to create SQL tables
setup_sqlite_tables()


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
def homepage():
    return render_template("home.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["password"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


# On "Study" page: render study.html template to user  
@app.route("/study", methods=["GET"])
@login_required
def start_studying():
    return render_template("study.html")

# On "Studying" page: render studying.html template to user  
@app.route("/studying", methods=["GET"])
@login_required
def display_headline():
    # If no max HSK level selected, set default max level to HSK 6
    max_hsk_level = request.args.get("max_hsk_level")
    if max_hsk_level == None: 
        max_hsk_level = 6

    # Select random headline from the ingested RSS headlines SQLite database that adheres to selected max HSK level
    headline = db.execute("SELECT id, tokenized_title, link FROM rss_items WHERE highest_hsk_level <= ? ORDER BY RANDOM() LIMIT 1", max_hsk_level)

    headline_link = headline[0]["link"]
    tokenized_title = headline[0]["tokenized_title"]

    # Pass today's date into a variable 
    today = date.today()

    # Split tokenized title into comma-separated list
    tokenized_list = tokenized_title.split(",")

    token_dict_list = [] 

    # Iterate over each token in the title to determine if in HSK database; if so, pull HSK level, Pinyin, and English translation(s)
    for token in tokenized_list:
        results = db.execute("SELECT hanzi, hsk_level, pinyin, translations, id FROM hsk_data WHERE hanzi=?", token)
        if len(results) == 0:
            token_dict_list.append({"token": token, "class": "token-grayed"})
        else:
            token_dict_list.append({"token": token, "hsk_level": results[0]["hsk_level"], "pinyin": results[0]["pinyin"], "translations": results[0]["translations"], "id": results[0]["id"], "class": "token"})
    
    # Update user_headline_history table to record article view
    db.execute("INSERT INTO user_headline_history(user_id, headline_id, date_viewed) VALUES (?, ?, ?)", session["user_id"], headline[0]["id"], today)

    # Display studying page to user, passing in token dictionary list and headline link to be used in Jinja template
    return render_template("studying.html", token_dict_list=token_dict_list, headline_link=headline_link)


# On "saveroute" page (not visible to user; under "studying.html" template): record user-saved vocabulary in SQL table
@app.route("/saveword", methods=["POST"])
@login_required
def save_word():
    # Retrieve id of clicked word from the user's click action
    word_id = int(request.json["id"])
    print(word_id)
    print(len(db.execute("SELECT vocab_id FROM user_vocab_history WHERE vocab_id=?", word_id)))

    # If word already saved, don't allow it to be re-saved.
    if len(db.execute("SELECT vocab_id FROM user_vocab_history WHERE vocab_id=?", word_id)) != 0:
        print("Word already saved.")
        return Response(status=400)

    # Update user_vocab_history table to record saved word.
    db.execute("INSERT INTO user_vocab_history(user_id, vocab_id) VALUES (?, ?)", session["user_id"], word_id)

    # Return Flask success code
    return Response(status=201)


# On "deleteword" page (not visible to user; under "studying.html" template): remove user-saved vocabulary word from SQL table
@app.route("/deleteword", methods=["POST"])
@login_required
def delete_word():
    # Retrieve id of clicked word from the user's click action
    word_id = int(request.json["id"])

    # Update user_vocab_history table to remove word
    db.execute("DELETE FROM user_vocab_history WHERE user_id=? AND vocab_id=?", session["user_id"], word_id)

    # Return Flask success code
    return Response(status=200)


# On "register" page: allow user to register. Verifies that user input adheres to guidelines; verifies that passwords match; verifies HSK level digit between 1 and 6
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        username = request.form.get("username") 

        # Confirm username is alphanumeric characters
        if username.isalnum() == False:
            return apology("Alphanumeric characters only, please.")

        # Confirm that password and re-entered password match
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if password != confirmation:
            return apology("Oops! Passwords do not match.")
        
        # Confirm password length between 8 and 20 alphanum. characters 
        elif len(password) < 8 or len(password) > 20:
            return apology("Whoops! Invalid password length. Please try again.")

        # https://werkzeug.palletsprojects.com/en/2.0.x/utils/
        hash_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)

        # Check that HSK level is valid.
        hsk_level = int(request.form.get("hsklevel"))
        if hsk_level < 1 or hsk_level > 6:
            return apology("糟糕！HSK levels are a single digit between 1 and 6.")

        # Add user to registrant database - enforces usernames must be unique
        try:
            db.execute("INSERT INTO users (username, password, hsk_level) VALUES(?, ?, ?)", username, hash_password, hsk_level)
        except ValueError as e:
            print(e)
            return apology("Oops! Username already in use.")

        # Prompt to login
        return render_template("/registered.html")

    else:
        return render_template("register.html")


# On "review" page: display two tables to user - one of viewed headlines, and one of saved vocabulary
@app.route("/review", methods=["GET"])
@login_required
def review():
    # Pull user-viewed headlines from SQL db
    viewed_headlines = db.execute("SELECT rss_items.source, rss_items.title, rss_items.link, rss_items.highest_hsk_level, user_headline_history.date_viewed \
                                   FROM rss_items LEFT JOIN user_headline_history \
                                   ON user_headline_history.headline_id=rss_items.id \
                                   WHERE user_headline_history.user_id = ?", session["user_id"])

    saved_vocab = select_saved_vocab()

    return render_template("review.html", viewed_headlines=viewed_headlines, saved_vocab=saved_vocab)

def select_saved_vocab():
    # Pull user-saved vocabulary from SQL db
    saved_vocab = db.execute("SELECT hsk_data.hsk_level, hsk_data.hanzi, hsk_data.pinyin, hsk_data.translations, hsk_data.id \
                                   FROM hsk_data LEFT JOIN user_vocab_history \
                                   ON user_vocab_history.vocab_id=hsk_data.id \
                                   WHERE user_vocab_history.user_id = ?", session["user_id"])

    for vocab in saved_vocab:
        # Clean translations list to remove brackets, single quotations
        translations_list = vocab['translations']
        cleaned_translations_list = translations_list.replace("[", "").replace("]", "").replace("'", "")

        # Replace bracketed, quoted translations list with cleaned list
        vocab['translations'] = cleaned_translations_list

    return saved_vocab


# On "downloadcsv" page (not visible to user; under "review.html" template): write and execute downloadable CSV containing user-saved vocabulary
@app.route("/downloadcsv", methods=["GET"])
@login_required
def downloadcsv():
    # Sources: https://stackoverflow.com/questions/30024948/flask-download-a-csv-file-on-clicking-a-button, https://stackoverflow.com/questions/9157314/how-do-i-write-data-into-csv-format-as-string-not-file
    saved_vocab = select_saved_vocab()
    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_NONNUMERIC)
    writer.writerow(["HSK Level", "Hanzi", "Pinyin", "Translation(s)"])

    for vocab in saved_vocab:
        writer.writerow([vocab['hsk_level'], vocab['hanzi'], vocab['pinyin'], vocab['translations']])

    return Response(output.getvalue(),
        mimetype="text/csv",
        headers={"Content-disposition":
                 "attachment; filename=zhournalism_saved_vocab.csv"})


# On "sources" page, render "source.html" page to user
@app.route("/sources", methods=["GET"])
@login_required
def sources():
    return render_template("sources.html")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
