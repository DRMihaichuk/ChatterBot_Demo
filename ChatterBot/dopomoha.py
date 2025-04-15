from chatterbot import ChatBot
from chatterbot.trainers import JsonFileTrainer
import argparse
import subprocess
import json

database = 'mongodb+srv://togekip00:BKOErjhmcKwUVNxF@chatterbotdb.f5fwu81.mongodb.net/Dopomoha'

def parse_arguments():
    parser = argparse.ArgumentParser(description="Process some parameters.")
    parser.add_argument('--mode', type=str, help='What mode should the bot be run in', default='talk')
    
    args = parser.parse_args()
    return args

args = parse_arguments()
args.mode = args.mode.upper()

if (args.mode != "TALK") and (args.mode != "TRAIN") and (args.mode != "ALL"):
    print(f"Invalid mode has been entered")
    exit()

# print(f"Mode: {args.mode}")

# Create a new chat bot named Elena
chatbot = ChatBot('Elena', 
                  read_only=True,
                  storage_adapter='chatterbot.storage.MongoDatabaseAdapter',
                  logic_adapters=['chatterbot.logic.BestMatch'],
                  database_uri=database)
username = "User"

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

if (args.mode == "TRAIN") or (args.mode == "ALL"):
    train_result = subprocess.run(["python", "sheet_conv.py"])
    if train_result.returncode == 1:
        print("No new data was added to training")
    else:
        trainer.train('./training_data.json')


if (args.mode == "TALK") or (args.mode == "ALL"):
    print(f"{chatbot.name}: Hello, my name is {chatbot.name}. How can I help you today?")
    # Working interface to work with chatbot (only console for now)
    while True:
        query = input(username + ": ")
        if query.upper() == "EXIT":
            break
        response = chatbot.get_response(query)
        print(f"{chatbot.name}: {response}")

##### Instructions to run #####
# To run chatbot for training and talking type "python ./dopomoha.py"
    # To run only to train the chatbot with new data type "python ./dopomoha.py --mode train"
    # To run only to talk to the chatbot type "python ./dopomoha.py --mode talk"
# Type exit while running chatbot to return back to terminal