from flask import Flask, request, jsonify
from flask_cors import CORS
import tkinter as tk
from tkinter import filedialog
import praw
from openai import OpenAI
from nltk.corpus import stopwords
import os
from dotenv import load_dotenv
from final import setup, create_thread,start,prompt, get_response, thread_id, assistant_id

load_dotenv()

openai_api_key = os.getenv('OPENAI_API_KEY')
reddit_client_id = os.getenv('REDDIT_CLIENT_ID')
reddit_client_secret = os.getenv('REDDIT_CLIENT_SECRET')
reddit_username = os.getenv('REDDIT_USERNAME')
reddit_password = os.getenv('REDDIT_PASSWORD')
reddit_user_agent = os.getenv('REDDIT_USER_AGENT')

reddit = praw.Reddit(client_id=reddit_client_id,
                     client_secret=reddit_client_secret,
                     username=reddit_username,
                     password=reddit_password,
                     user_agent=reddit_user_agent)

client = OpenAI(api_key=openai_api_key)

app = Flask(__name__)
CORS(app)

file_path = ""

@app.route('/set-keys', methods=['POST'])
def set_keys():
    global openai_api_key, reddit_client_id, reddit_client_secret, reddit_username, reddit_password, reddit_user_agent
    data = request.json
    openai_api_key = data.get('openai_api_key')
    reddit_client_id = data.get('reddit_client_id')
    reddit_client_secret = data.get('reddit_client_secret')
    reddit_username = data.get('reddit_username')
    reddit_password = data.get('reddit_password')
    reddit_user_agent = data.get('reddit_user_agent')

    # Initialize Reddit and OpenAI clients with new keys
    init_clients()

    return jsonify({"message": "Keys set successfully"}), 200

@app.route('/input-keys', methods=['POST'])
def input_keys():
    global openai_api_key, reddit_client_id, reddit_client_secret, reddit_username, reddit_password, reddit_user_agent
    openai_api_key = request.json.get('openai_api_key')
    reddit_client_id = request.json.get('reddit_client_id')
    reddit_client_secret = request.json.get('reddit_client_secret')
    reddit_username = request.json.get('reddit_username')
    reddit_password = request.json.get('reddit_password')
    reddit_user_agent = request.json.get('reddit_user_agent')

    # Initialize Reddit and OpenAI clients with new keys
    init_clients()

    return jsonify({"message": "Keys set successfully"}), 200

def init_clients():
    global reddit, client
    reddit = praw.Reddit(client_id=reddit_client_id,
                         client_secret=reddit_client_secret,
                         username=reddit_username,
                         password=reddit_password,
                         user_agent=reddit_user_agent)

    client = OpenAI(api_key=openai_api_key)

@app.route('/upload', methods=['POST'])
def upload_file():
    global file_path
    file = request.files['file']
    file.save(file.filename)
    file_path = file.filename
    return jsonify({"message": "File uploaded successfully"}), 200

@app.route('/start', methods=['GET'])
def start_assistant():
    with open(file_path, "rb") as file:
        file = client.files.create(
            file=file,
            purpose='assistants'
        )

    assistant_id = setup()
    thread_id = create_thread()
    start(thread_id, prompt)

    return jsonify({"message": "Assistant started successfully"}), 200

@app.route('/get-response', methods=['GET'])
def get_assistant_response():
    response = get_response(thread_id, assistant_id)
    return jsonify({"response": response}), 200

if __name__ == '__main__':
    app.run(debug=True)
