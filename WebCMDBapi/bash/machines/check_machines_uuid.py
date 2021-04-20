#!/usr/bin/python3
import csv, uuid
import re

newfile = []
uuid4hex = re.compile('[0-9a-f]{8}\-[0-9a-f]{4}\-4[0-9a-f]{3}\-[89ab][0-9a-f]{3}\-[0-9a-f]{12}', re.I)

def valid_uuid(uuidstr):
    return uuid4hex.match(uuidstr)

with open('machines_tri.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter='|')
    counter = 0
    for index, row in enumerate(csv_reader):
        print(row[21])
        if row[0] != "1 NAME":
            if row[20] == "":
                row[20] = str(uuid.uuid4())
                uuidstr = row[20]
                print(f"Row {index}: UUID not found, assigning {uuidstr}")
                counter += 1; #detect changes
            elif not valid_uuid(row[20]):
                row[20] = str(uuid.uuid4())
                uuidstr = row[20]
                print(f"Row {index}: UUID wrong, assigning {uuidstr}")
                counter += 1; #detect changes
        newfile.append(row)

if counter >= 1:
    print(f"UUID check failed in {counter} lines. Rewriting file.")
    with open("machines_tri.csv", "w") as csv_file:
        csv_writer = csv.writer(csv_file, delimiter="|")
        for row in newfile:
            csv_writer.writerow(row)
else:
    print("UUID: OK")