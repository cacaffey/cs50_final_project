Environment: 
GitHub Codespaces

Preparatory Steps: 
Ensure Codespace is the 8GB RAM version (default is 4GB):
    (Logged into GitHub)
    https://github.com/codespaces
    Under cs50 codespace, set machine type to 4 core/8GB ram

Ensure running Python version 3.x

In the Codespaces Terminal:
Clone the GitHub repo (https://github.com/cacaffey/cs50_final_project) or unzip the the `project.zip` file using preferred method within Codespaces (ex. `unzip project.zip`). This will depend on whether the GitHub repo version or backup Google Drive .zip version is being used.

Execute: 
`cd Zhournalism`

This web app is shipping with the SQL tables already created (code in `app.py`) and the HSK data ingested (via `insert_hsk_into_sql.py`). 

This web app is shipping with sample headlines. To ingest the latest news headlines, from within the Zhournalism directory, please run:
`./ingest_data.bash`

This will execute a series of commands to scrape the latest headlines from RSS feeds, tokenize, and ingest the headlines into a SQL database. 
Progress commands will print to the terminal to keep you updated. This script contains the virtual environment - no need to set up or manipulate the venv yourself.

NOTE: ingestion will not be re-triggered automatically over time. If you wish to ingest new headlines (possibly a day or two later), please re-run this script. 
Titles are checked to ensure that no duplicates will be added to the SQL database.

NOTE: As noted in the DESIGN.md file, in some instances while testing, the Java errored out due to failed connection to the CoreNLP server. If this occurs, please
wait a few minutes to try running again. As a failsafe, this project is shipped with some data preloaded. 

Once ingestion has completed, execute:
`flask run`

This will launch the web app. Click on the provided URL to view and interact with the web app. It should resemble:

Zhournalism/ $ flask run
 * Environment: development
 * Debug mode: off
 * Running on https://cacaffey-code50-39955645-67rpj5jvfr59j-5000.githubpreview.dev/ (Press CTRL+C to quit)
 * Restarting with stat

** Within the website **
## Registration
Click `Register` in the navbar to create a user account. Completing the self-assessment to enter HSK level is optional - account creation can proceed without. 
Passwords are stored salted and hashed in a SQL database. Usernames must be unique - this is enforced in the backend. 

## Log In
Once registered, either navigate natively or by clicking `Log In` to log into your account. 

## Begin Studying
Once logged in, click `Study` in the navbar. Click one of the blue buttons to select the maximum HSK level of headline you wish to see (ex. "Max HSK 5"
will limit headlines to only those containing HSK 5 vocabulary and below.) Usage instructions are also provided on the page. 

## Studying 
Once you've selected an HSK difficulty, you will see a news headline. Non-HSK words are greyed out. HSK words will be labeled with their HSK level. Hovering
over the word will show the Pinyin via a hover label. Clicking a word will show the Pinyin, character (Hanzi), and English translation(s) below the headline.
Once a word is clicked, you also have the option to save the word to your personal study database (viewable in the `Review` section of the site). 

The "New Headline" button will change the headline in your view. Clicking the full article link will navigate to the corresponding URL with the full article.

## Sources
This page contains the logo image for both of the underlying sources: People's Daily and The New York Times (Chinese Edition). This page is not interactive.

## Review
This page displays the headlines you have viewed with metadata, such as the date viewed and the full URL link.

Additionally, you can see and interact with all saved vocabulary. Here, you can delete saved words. Additionally, you can download all saved words as a CSV file. 
This CSV file can be ingested into flaskcard apps (such as Anki) for further study. 