from pymongo import MongoClient
import requests
import csv
import io
import json

# Replace with your sheet's ID
sheet_id = "1QMV6EBLcvzgh_vQPs7wRQo6kwOwqc5UBZW6izwp33aU"
sheet_name = "Data"
csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
script_id = "AKfycbxukihwVvSvLFBHOeEcrMPlCfk4TBNyLUqRUefo9_3WWdI0C2BzBUeyw8M-CHnKeuep"
script_url = f"https://script.google.com/macros/s/{script_id}/exec"

response = requests.get(csv_url)
response.raise_for_status()  # Will raise an error if request failed
resp = requests.get(script_url)
if resp.status_code == 200:
    print("Successfully triggered the Apps Script function!")
else:
    print(f"Failed to trigger Apps Script: {resp.status_code}")

# Decode and parse the CSV content
csv_file = io.StringIO(response.text)
reader = csv.DictReader(csv_file)

# Filtering out already trained data
filtered_data = [row for row in reader if row['Status'] == 'Ready']

conversation_list = []
for row in filtered_data:
    if row["Verified Translation"] == "Yes":
        row["Verified Translation"] = "Verified Translation"
    else:
        row["Verified Translation"] = "Unverified Translation"

    if (row["Response"] != "") and (row["Prompt"] != "") and (row["Language"] != ""):
        conversation_entry = {
            "text": row["Response"],
            "in_response_to": row["Prompt"],
            "persona": "user 1",
            "conversation": row["Subject"],
            "tags": [row["Language"], row["Verified Translation"]]
        }
        conversation_list.append(conversation_entry)

final_json = {"conversation": conversation_list}

with open("training_data.json", "w", encoding='utf-8') as f:
    json.dump(final_json, f, indent=4)

if len(conversation_list) > 0:
    print("conversation_data.json created with", len(conversation_list), "entries.")
else:
    exit(1)