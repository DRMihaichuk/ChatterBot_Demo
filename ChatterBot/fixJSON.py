import json

# Load the data
with open('scrape_data.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# Iterate and add 'subject' based on user input or logic
for entry in data['conversation']:
    entry['Subject'] = ''
    entry['Language'] = 'English'
    entry['Verified Language'] = 'Yes'
    entry['Status'] = 'Imported'

# Save the updated data back to the file
with open('data_updated.json', 'w', encoding='utf-8') as file:
    json.dump(data, file, indent=4, ensure_ascii=False)