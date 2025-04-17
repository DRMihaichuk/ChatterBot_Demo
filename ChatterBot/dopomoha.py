from flask import Flask, request, jsonify
from chatterbot import ChatBot
from chatterbot.trainers import JsonFileTrainer
import subprocess

app = Flask(__name__)

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
    return jsonify({"message": "Chatbot API is running"}), 200

@app.route('/train', methods=['GET'])
def train():
    # Call sheet_conv.py and then train
    result = subprocess.run(["python", "sheet_conv.py"])
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)