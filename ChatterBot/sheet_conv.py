from pymongo import MongoClient
import requests
import csv
import io
import json

client = MongoClient("mongodb+srv://togekip00:BKOErjhmcKwUVNxF@chatterbotdb.f5fwu81.mongodb.net/")
db = client["Dopomoha"]
collection = db["statements"]

# Replace with your sheet's ID
sheet_id = "1QMV6EBLcvzgh_vQPs7wRQo6kwOwqc5UBZW6izwp33aU"
sheet_name = "Data"
csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"

response = requests.get(csv_url)
response.raise_for_status()  # Will raise an error if request failed

# Decode and parse the CSV content
csv_file = io.StringIO(response.text)
reader = csv.DictReader(csv_file)

conversation_list = []
for row in reader:
    existing = collection.find_one({"in_response_to": row["Prompt"]})

    if row["Verified"] == "Yes":
        row["Verified"] = "Verified"
    else:
        row["Verified"] = "Unverified"

    if (row["Response"] != "") and (row["Prompt"] != "") and (row["Language"] != "") and (not existing):
        conversation_entry = {
            "text": row["Response"],
            "in_response_to": row["Prompt"],
            "persona": "user 1",
            "conversation": row["Subject"],
            "tags": [row["Language"], row["Verified"]]
        }
        conversation_list.append(conversation_entry)

final_json = {"conversation": conversation_list}

with open("training_data.json", "w", encoding='utf-8') as f:
    json.dump(final_json, f, indent=4)

if len(conversation_list) > 0:
    print("conversation_data.json created with", len(conversation_list), "entries.")
else:
    exit(1)