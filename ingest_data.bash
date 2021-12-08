#!/bin/bash

echo "Activating our Python venv ..."
source venv/bin/activate

echo "Installing required packages ..."
pip3 install pandas requests_xml nltk

echo "Starting CoreNLP Server ..."
cd stanford-corenlp-4.3.2
# Executes command to initiate CoreNLP processes and runs the command in the background
java -Xmx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -serverProperties StanfordCoreNLP-chinese.properties -port 9002 -timeout 15000 &
cd -

echo "Waiting for server to start ..."
sleep 5

echo "Ingesting the latest headlines ..."
# Executes Scrape RSS python script
python scrape_rss.py

echo "Stopping CoreNLP Server ..."
# Stops the first executed job (CoreNLP server)
kill %1
sleep 5

echo "Deactivating our Python venv ..."
deactivate
