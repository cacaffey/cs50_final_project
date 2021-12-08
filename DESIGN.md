For "Zhournalism", a web app was the natural choice since it builds on current RSS news feeds from two large news publications. I intentionally kept the interface clean and light so that the emphasis was on the Chinese characters - the focus of the app. 

## scrape_rss.py
In "scrape_rss.py", Zhournalism ingests recent headlines via RSS feeds from The People's Daily and the New York Times Chinese edition. For each paper, and each headline, four pieces of information are identified in the XML of the RSS feed page and processed into a dataframe: headline title, publication date, live URL, and source (which paper). The headlines are then run through Stanford's CoreNLP tokenizer to obtain the tokenized version. This was a critical step for Mandarin since whitespace cannot be used as a word deliniator (whitespace only occurs between sentences, and sometimes around special punctuation, such as quotation marks or brackets). CoreNLP is specificially designed to handle Chinese, as specified in their usage guide: https://stanfordnlp.github.io/CoreNLP/corenlp-server.html. 

Once tokenization is complete, the headlines are analyzed for matching HSK tokens in the 5000 character HSK database. If no HSK match is found, the headline is discarded. After HSK matching is complete, the headlines are iteratively added to the "rss_items" SQLite database by looping over each row in the dataframe. For each headline, the source, title, tokenized title, highest HSK level, publication date, and live link are added to the database. 

CoreNLP is an enhanced version of the nltk package, which is commonly used in natural language processing tasks. Additional references can be found in the "resources" section of this document below. 


## ingest_data.bash
This script executes scrape_rss.py and connects the project to the CoreNLP server. This process is done within a virtual environment to manage package versioning. Ideally, everything would be run within the venv, however, something about the CS50/Flask/Codespaces interaction would not generate the correct URL when "flask run" was executed within a venv. 

NOTE: In a future interation of this project, I would like to learn more about how to make ingestion pipelines more stable, as I'm not currently very familiar with
how to best make Python and Java work together. In some instances while testing, the Java errored out due to failed connection to the CoreNLP server. This was 
resolved after waiting a few minutes to run again.


## convertjson.py & insertsql.py
** Source for 5000 character HSK database: https://github.com/gigacool/hanyu-shuiping-kaoshi/blob/master/hsk.json. **
In "convertjson.py", the JSON download from Gigacool's GitHub repository was converted from JSON into a CSV. This CSV was then inserted into the "hsk_data" SQLite database via "insertsql.py".


## helpers.py
Borrowing from the Finance problem set, this file contains two helper functions - apology and login required. Both remain the same as in Finance, except that I updated the apology image from grumpy cat to a funny still from Kung Fu Panda.


## app.py
This is the primary function that brings all elements of the app together, including connecting the SQL backend functionality with the user-facing HTML pages. I chose to code in Python, using the Flask framework, HTML, SQlite, CSS, JavaScript, and Jinja as these are all tools I am (somewhat) comfortable with using since the conclusion of the course. This file is thoroughly commented with further details on a function-by-function basis. 


## Templates [Folder]
This folder contains all of the HTML pages that comprise the web app. "layout.html" is the foundational page, which is extended via Jinja to the rest of the pages. JavaScript supports advanced functionality in many of the pages, such as retrieving user actions (ex. button clicks).


## ** Utilized Resources **
A non-comprehensive list of resources utilized in development of this project. 

CoreNLP Server: https://stanfordnlp.github.io/CoreNLP/corenlp-server.html
* wget https://nlp.stanford.edu/software/stanford-corenlp-latest.zip
* wget https://search.maven.org/remotecontent?filepath=edu/stanford/nlp/stanford-corenlp/4.3.2/stanford-corenlp-4.3.2-models-chinese.jar
* Running the server (from stanford-corenlp-4.3.2 directory): java -Xmx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -serverProperties StanfordCoreNLP-chinese.properties -port 9002 -timeout 15000

CoreNLP + NLTK: https://github.com/nltk/nltk/wiki/Stanford-CoreNLP-API-in-NLTK

http://sites.cognitivescience.co/knowledgebase/resources/using-google-sites/creating-mouseover-text-with-html
https://csveda.com/python-flask-website-adding-routes-to-link-pages/
https://developer.mozilla.org/en-US/docs/Learn/HTML/Howto/Use_data_attributes
https://developer.mozilla.org/en-US/docs/Web/API/Document/getElementsByClassName
https://developer.mozilla.org/en-US/docs/Web/API/Document/querySelector
https://developer.mozilla.org/en-US/docs/Web/API/Document/querySelectorAll
https://developer.mozilla.org/en-US/docs/Web/API/EventTarget/addEventListener
https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch
https://docs.microsoft.com/en-us/previous-versions/dotnet/netframework-4.0/ms256086(v=vs.100)?redirectedfrom=MSDN
https://docs.python.org/3/library/json.html
https://docs.python.org/3/library/venv.html
https://getbootstrap.com/docs/4.0/components/buttons/
https://github.com/erinxocon/requests-xml
https://jinja.palletsprojects.com/en/3.0.x/templates/
https://medium.com/@crawftv/javascript-jinja-flask-b0ebfdb406b3
https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.itertuples.html#pandas.DataFrame.itertuples
https://practicaldatascience.co.uk/data-science/how-to-read-an-rss-feed-in-python
https://stackoverflow.com/questions/11124940/creating-link-to-an-url-of-flask-app-in-jinja2-template
https://stackoverflow.com/questions/11620698/how-to-trigger-a-file-download-when-clicking-an-html-button-or-javascript
https://stackoverflow.com/questions/1269589/css-center-block-but-align-contents-to-the-left
https://stackoverflow.com/questions/15547198/export-html-table-to-csv-using-vanilla-javascript
https://stackoverflow.com/questions/16250623/sqlite-delete-one-single-row
https://stackoverflow.com/questions/16476924/how-to-iterate-over-rows-in-a-dataframe-in-pandas
https://stackoverflow.com/questions/16815995/dynamic-table-width
https://stackoverflow.com/questions/18075794/bootstrap-table-without-stripe-borders
https://stackoverflow.com/questions/18239430/cannot-set-property-innerhtml-of-null
https://stackoverflow.com/questions/20819010/bootstrap-3-does-form-horizontal-work-for-radio-buttons-with-a-control-label
https://stackoverflow.com/questions/21070101/show-hide-div-using-javascript
https://stackoverflow.com/questions/21214270/how-to-schedule-a-function-to-run-every-hour-on-flask
https://stackoverflow.com/questions/29775797/fetch-post-json-data
https://stackoverflow.com/questions/30024948/flask-download-a-csv-file-on-clicking-a-button
https://stackoverflow.com/questions/33501696/how-to-return-value-from-addeventlistener
https://stackoverflow.com/questions/33760520/how-can-i-get-the-values-of-data-attributes-in-javascript-code
https://stackoverflow.com/questions/35470875/passing-python-dict-to-template
https://stackoverflow.com/questions/40620823/if-statement-in-jinja2-template
https://stackoverflow.com/questions/42317868/flask-jinja2-table-generation-with-variable
https://stackoverflow.com/questions/4291236/edit-the-values-in-a-list-of-dictionaries
https://stackoverflow.com/questions/48076908/jinja2-writing-data-in-tag-attribute-within-a-loop
https://stackoverflow.com/questions/51925804/javascript-highlight-an-element-on-hover
https://stackoverflow.com/questions/56774542/colored-text-in-jinja2-template-depending-on-condition-in-python/56775992
https://stackoverflow.com/questions/580639/how-to-randomly-select-rows-in-sql
https://stackoverflow.com/questions/6116978/how-to-replace-multiple-substrings-of-a-string
https://stackoverflow.com/questions/61457754/how-to-insert-multiple-foreign-key-in-db-browser-for-sqlite-gui
https://stackoverflow.com/questions/6191672/python-dictionary-creation-syntax
https://stackoverflow.com/questions/6957443/how-to-display-div-after-click-the-button-in-javascript
https://stackoverflow.com/questions/7184562/how-to-get-elements-with-multiple-classes
https://stackoverflow.com/questions/7436267/python-transform-a-dictionary-into-a-list-of-lists
https://stackoverflow.com/questions/8318591/javascript-addeventlistener-using-to-create-a-mouseover-effect
https://stackoverflow.com/questions/9157314/how-do-i-write-data-into-csv-format-as-string-not-file
https://stackoverflow.com/questions/9835727/jinja2-translation-of-links
https://unix.stackexchange.com/questions/124127/kill-all-descendant-processes
https://www.digitalocean.com/community/tutorials/how-to-make-a-web-application-using-flask-in-python-3
https://www.geeksforgeeks.org/convert-json-to-csv-in-python/
https://www.nltk.org/_modules/nltk/tokenize/stanford_segmenter.html
https://www.programiz.com/python-programming/datetime/current-datetime
https://www.sqlite.org/autoinc.html
https://www.sqlite.org/foreignkeys.html
https://www.sqlitetutorial.net/sqlite-foreign-key/
https://www.sqlitetutorial.net/sqlite-import-csv/
https://www.sqlitetutorial.net/sqlite-max/
https://www.w3schools.com/cssref/sel_hover.asp
https://www.w3schools.com/howto/howto_css_border_image.asp
https://www.w3schools.com/howto/howto_css_images_side_by_side.asp
https://www.w3schools.com/html/html_tables.asp
https://www.w3schools.com/jsref/met_element_queryselector.asp
https://www.w3schools.com/python/ref_string_split.asp
https://www.w3schools.com/sql/sql_join.asp
https://www.w3schools.com/tags/att_input_max.asp
https://www.w3schools.com/tags/tag_col.asp
https://www.w3schools.com/tags/tag_figcaption.asp
