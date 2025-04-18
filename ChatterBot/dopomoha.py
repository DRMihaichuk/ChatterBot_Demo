from flask import Flask, request, jsonify, render_template
from chatterbot import ChatBot
from chatterbot.trainers import JsonFileTrainer
import subprocess
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)

# MongoDB URI for ChatterBot
database = 'mongodb+srv://togekip00:BKOErjhmcKwUVNxF@chatterbotdb.f5fwu81.mongodb.net/Dopomoha'

# Instantiate the chatbot
chatbot = ChatBot('Elena', 
                  read_only=True,
                  storage_adapter='chatterbot.storage.MongoDatabaseAdapter',
                  logic_adapters=['chatterbot.logic.BestMatch'],
                  database_uri=database)

trainer = JsonFileTrainer(
    chatbot,
    field_map={
        'persona': 'persona',
        'text': 'text',
        'conversation': 'conversation',
        'in_response_to': 'in_response_to',
        'tags': 'tags'
    }
)

@app.route('/')
def index():
    return render_template('chat.html')

@app.route('/train', methods=['GET'])
def train():
    # Call sheet_conv.py and then train
    result = subprocess.run(["python", "ChatterBot/sheet_conv.py"])
    if result.returncode == 1:
        return jsonify({"status": "No new data was added to training"}), 200
    else:
        trainer.train('./training_data.json')
        return jsonify({"status": "Training completed successfully"}), 200

@app.route('/talk', methods=['POST'])
def talk():
    user_input = request.json.get("message")
    if not user_input:
        return jsonify({"error": "Missing 'message' in request body"}), 400

    response = chatbot.get_response(user_input)
    return jsonify({"response": str(response)}), 200

@app.route('/untrain', methods=['GET'])
def untrain():
    result = subprocess.run(["python", "ChatterBot/sheet_conv.py", "--extract", "Untrain"])
    if result.returncode == 1:
        return jsonify({"status": "No new data was added to training"}), 200
    else:
        trainer.untrain('./training_data.json')
        return jsonify({"status": "Removed training successfully"}), 200
    
@app.route('/scrape_data', methods=['GET'])
def scrapedData():
    file_path = os.path.join(os.path.dirname(__file__), 'scrape_data.json')
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return jsonify(data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)