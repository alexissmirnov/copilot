''' index '''
from flask import Flask

app = Flask(__name__)

''' home '''
@app.route('/')
def home():
    return 'Hello, World!'

''' about '''
@app.route('/about')
def about():
    return 'About'
