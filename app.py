from flask import Flask, request, jsonify, redirect
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_random_exponential
from dotenv import load_dotenv
import os
import json
import logging


load_dotenv()

app = Flask(__name__)

logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

api_key = os.getenv("OPENAI_API_KEY")
print("OpenAI API Key:", api_key)
if not api_key:
    raise ValueError("OpenAI API key not found. Make sure to set the OPENAI_API_KEY environment variable.")
client = OpenAI(api_key=api_key)

# Loding scraped data
scraped_data = {}
try:
    with open("scraped_data.json", "r") as json_file:
        scraped_data = json.load(json_file)
except FileNotFoundError:
    logging.warning("scraped_data.json not found. Make sure the file exists.")

#Dictionary to story cached response
response_cache = {}    

@retry(
    stop=stop_after_attempt(2),  # Stop retrying after 2 attempts
    wait=wait_random_exponential(multiplier=1, max=60),  # Apply exponential backoff with random jitter
)
def call_openai_chat_api(conversation):
    user_input = conversation[-1]["content"]

    # Check if user input exists in cache
    if user_input in response_cache:
        return response_cache[user_input]

    # Check if user input matches any question in scraped data
    for category, data in scraped_data.items():
        for qa_pair in data:
            if user_input.lower() == qa_pair["question"].lower():
                return qa_pair["answer"]
                                                                               
    #if not     
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=conversation,
        max_tokens=100,           
        n=1,
        stop=None
    )
    response_content = response.choices[0].message.content.strip()
    response_cache[user_input] = response_content  # Cache the response
    return response_content
   
                                                                                                                                              

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message')

    if not user_input:
        logging.error('No message provided in the request')
        return jsonify({'error': 'No message provided in the request'}), 400

    # Log the user input
    logging.info(f'User input: {user_input}')

    # Craft conversation history for the model
    conversation = [{"role": "user", "content": user_input}]
  
    try:
        bot_response = call_openai_chat_api(conversation)
    except Exception as e:
        bot_response = f"An error occurred: {str(e)}"

    return jsonify({'message': bot_response})

@app.route('/', methods=['GET'])
def index():
    return redirect('/chat')

@app.route('/chat', methods=['GET'])
def handle_get():
    return jsonify({'message': 'GET requests are not allowed for this endpoint'}), 405

if __name__ == '__main__':
    app.run(debug=True, port=5003)
