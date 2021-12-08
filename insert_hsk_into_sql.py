import csv
from cs50 import SQL

filename = "raw_hsk_data.csv"

db = SQL("sqlite:///zhournalism.db")

with open(filename, "r") as csvfile:
    datareader = csv.reader(csvfile)
    for row in datareader:
        # Skip header row, any other invalid rows (if present)
        if row[0].isnumeric():
            db.execute("INSERT INTO hsk_data (hsk_level, id, hanzi, pinyin, translations) VALUES(?, ?, ?, ?, ?)", int(row[0]), int(row[1]), row[2], row[3], row[4])
