''' index '''
from flask import Flask
from langchain.llms import OpenAI
import os

openai_api_key=os.getenv('OPENAI_API_KEY')
app = Flask(__name__)

llm = OpenAI(openai_api_key=openai_api_key)

def sanitize_string(input_string):
    first_letter = input_string[0]
    last_letter = input_string[-1]
    middle_length = len(input_string) - 2
    transformed_string = first_letter + '-' + '*' * middle_length + last_letter
    return transformed_string

''' home '''
@app.route('/')
def home():
    return 'Hello, World! API key: ' + sanitize_string(openai_api_key)

''' about '''
@app.route('/about')
def about():
    return 'About'
