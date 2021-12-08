import json
import csv

# Open raw HSK data as JSON file
with open('raw_hsk_data.json') as json_file:
    data = json.load(json_file)

hsk_data = data

# Open raw HSK CSV file as writeable
raw_hsk_data = open('raw_hsk_data.csv', 'w')

csv_writer = csv.writer(raw_hsk_data)

count = 0

for vocab in hsk_data:
    if count == 0:

        # Write headers of CSV file
        header = vocab.keys()
        csv_writer.writerow(header)
        count += 1

    # Write data of CSV file
    csv_writer.writerow(vocab.values())

# Close newly created CSV file
raw_hsk_data.close()