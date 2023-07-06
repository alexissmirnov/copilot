''' main '''
import os
import json
import logging
# from urllib.parse import urlparse
from flask import Flask, request
from flask_cors import CORS
from langchain.llms import OpenAI
from langchain.document_loaders import NotionDBLoader
# from notion_pages import NotionPageLoader

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
NOTION_INTEGRATION_SECRET = os.getenv('NOTION_INTEGRATION_SECRET')
NOTION_INSTRUCTIONS_DB = os.getenv('NOTION_INSTRUCTIONS_DB')
NOTION_EXAMPLES_DB = os.getenv('NOTION_EXAMPLES_DB')

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["*dialogue.co", "http://localhost:4200"]}})
logging.getLogger('flask_cors').level = logging.DEBUG

llm = OpenAI(openai_api_key=OPENAI_API_KEY)


# @current_app.before_request
# def basic_authentication():
#     if request.method.lower() == 'options':
#         return Response()
    
def sanitize_string(input_string):
    """ to show the API key """
    first_letter = input_string[0]
    last_letter = input_string[-1]
    middle_length = len(input_string) - 2
    transformed_string = first_letter + '*' * middle_length + last_letter
    return transformed_string


def load_notion_db(database_id):
    """ loads db contents """
    loader = NotionDBLoader(
        integration_token=NOTION_INTEGRATION_SECRET,
        database_id=database_id
    )
    docs = loader.load()
    output = ''
    for doc in docs:
        output = f"{output}# {doc.metadata['name']}\n{doc.page_content}\n\n"

    return output


# def load_notion_page_from_url(url) -> str:
#     """load_notion_page_from_url"""
#     parsed_url = urlparse(url)
#     path = parsed_url.path

#     # Get the last portion of the path
#     page_id = path.rsplit('/', 1)[-1]

#     loader = NotionPageLoader(
#         integration_token=NOTION_INTEGRATION_SECRET
#     )
#     doc = loader.load_page_by_id(page_id)
#     return doc.page_content

@app.route('/', methods=['GET'])
def home():
    """ home """
    return llm.predict("What would be a good company name for telemedicine providing virtual care services via chat and video?")

@app.route('/', methods=['OPTIONS'])
def home_options():
    """ home """
    return ""

@app.route('/about')
def about():
    """ about """
    return f"API key: {sanitize_string(OPENAI_API_KEY)}\nNotion DB: {sanitize_string(NOTION_INTEGRATION_SECRET)}"


@app.route('/instructions')
def instructions():
    """ instrustions """
    return load_notion_db(NOTION_INSTRUCTIONS_DB)


@app.route('/examples')
def examples():
    """ examples """
    return load_notion_db(NOTION_EXAMPLES_DB)


@app.route('/copilot')
def copilot():
    """ copilot """
    prompt = ""

    instructions_content = load_notion_db(NOTION_INSTRUCTIONS_DB)
    examples_content = load_notion_db(NOTION_EXAMPLES_DB)

    # context = load_notion_page_from_url(request.args.get('context_url'))
    context = """
    Member Profile:

    Name: Alexis

    Sex: Male

    Age: 53

    Episode ID: 123abc

    Episode issue type: Intake

    Transcript:

    Chloe: Do you experience chest pain?
    Member: Yes
    Chloe: Do you experience vertigo?
    Member: Yes
    Chloe: Do you have a high heart rate?
    Member: Yes
    """

    prompt = f"""{instructions_content}\n\n\n
    # Examples:\n
    {examples_content}
    \n\n\n
    # Assignement: You are asked for assistance and receive the following episode\n
    {context}"""

    return llm.predict(prompt)

@app.route('/cp', methods=['OPTIONS'])
def cp_options():
    return ""

@app.route('/cp', methods=['POST'])
def cp():
    """ 
    POST handler for copilot
    """
    context = ""
    if request.method == 'POST':
        context = request.json

    instructions_content = load_notion_db(NOTION_INSTRUCTIONS_DB)
    examples_content = load_notion_db(NOTION_EXAMPLES_DB)

    prompt = f"""{instructions_content}\n\n\n
    # Examples:\n
    {examples_content}
    \n\n\n
    # Assignement: You are asked for assistance and receive the following episode\n
    {context}"""

    output = llm.predict(prompt)
    json_output = {
        "summary": output
    }
    return json.dumps(json_output)
