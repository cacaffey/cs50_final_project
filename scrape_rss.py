import requests
import pandas as pd
from requests_xml import XMLSession
from nltk.parse import CoreNLPParser
from cs50 import SQL

# People's Daily (人民日报) RSS feed ingestion and parsing
source_1 = {"url": "http://www.people.com.cn/rss/world.xml", "source_name": "The People\'s Daily"}

# New York Times - Chinese (Simplified) Edition
source_2 = {"url": "https://cn.nytimes.com/rss/", "source_name": "The New York Times (CN)"}

sources = [source_1, source_2]

db = SQL("sqlite:///zhournalism.db")

parser = CoreNLPParser(url='http://localhost:9002')

# Return source code for URL
def get_source(url):
    try:
        session = XMLSession()
        response = session.get(url)
        return response

    except requests.exceptions.RequestException as e:
        print(e)

# Return Pandas dataframe containing RSS feed contents
def get_feed(url, source_name):
    response = get_source(url)

    # Initialize dataframe containing specified column headers
    df = pd.DataFrame(columns = ['title', 'pubDate', 'description', 'link'])

    # Find corresponding items in XML and populate dataframe
    with response as r:
        items = r.xml.find("item", first=False)

        for item in items:
            title = item.xpath('title', first=True).text
            pubDate = item.xpath('pubDate', first=True).text
            link = item.xpath('link', first=True).text

            row = {'title': title, 'pubDate': pubDate, 'link': link, 'source': source_name}
            df = df.append(row, ignore_index=True)
    return df


# Run each returned item through Stanford Core NLP parser to tokenize.
# Note: Tokenization is critical for Chinese as whitespace is not used to separate words. Thus a word like "国家" needs to be identified
# as a single word meaning "country" rather than each character, "国" (country) and "家" (house/home/family). 
def tokenize(item): 
    tokens = list(parser.tokenize(item))
    return tokens

# Run each returned item through HSK-identifier to identify level of each token - and the highest level therein
# max_level returns "None" if no token matches. Filtered out in analyze_by_article function below.
def analyze_hsk(tokens):
    max_level = db.execute("SELECT MAX(hsk_level) FROM hsk_data WHERE hanzi IN (?)", tokens)[0]["MAX(hsk_level)"]
    return max_level

# Iterates over each line (article) in the dataframe to tokenize the title and determine the highest contained HSK level.
def analyze_by_article(df):
    counter = 0
    for row in df.itertuples():
        tokens = tokenize(row.title)
        highest_hsk_level = analyze_hsk(tokens)

        # If no HSK level, does not add title to database
        if highest_hsk_level == None:
            continue

        # If identical title already exists, does not add title to database
        if len(db.execute("SELECT title FROM rss_items WHERE title LIKE ?", row.title)) != 0:
            print("Title already in database.")
            continue

        # Insert each analyzed title into SQL database
        db.execute("INSERT INTO rss_items (source, title, tokenized_title, highest_hsk_level, pub_date, link) VALUES(?, ?, ?, ?, ?, ?)", row.source, row.title, ",".join(tokens), highest_hsk_level, row.pubDate, row.link)
        counter += 1
    return counter

for source in sources:
    df = get_feed(source["url"], source["source_name"])
    article_count = analyze_by_article(df)
    print("Added " + str(article_count) + " articles to database.")