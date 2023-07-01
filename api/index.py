''' index '''
import os
from flask import Flask
from langchain.llms import OpenAI
from langchain.document_loaders import NotionDBLoader

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
NOTION_INTEGRATION_SECRET = os.getenv('NOTION_INTEGRATION_SECRET')
NOTION_DB = os.getenv('NOTION_DB')

app = Flask(__name__)

llm = OpenAI(openai_api_key=OPENAI_API_KEY)


def sanitize_string(input_string):
    """ to show the API key """
    first_letter = input_string[0]
    last_letter = input_string[-1]
    middle_length = len(input_string) - 2
    transformed_string = first_letter + '*' * middle_length + last_letter
    return transformed_string


@app.route('/')
def home():
    """ home """
    return llm.predict("What would be a good company name for a company that makes colorful socks?")


@app.route('/about')
def about():
    """ about """
    return f"API key: {sanitize_string(OPENAI_API_KEY)}\nNotion DB: {sanitize_string(NOTION_DB)}"

# instructions
# [
#     Document(
#         page_content='test of the first instruction',
#         metadata={'description': None, 'tags': [], 'name': 'first instruction', 'id': '99743a38-f434-4a2e-bc0a-6ecdcd0856b1'}),
#     Document(
#         page_content='',
#         metadata={'description': None, 'tags': [], 'name': 'third instruction', 'id': 'a8a1dd4b-9e69-4920-bfd2-9025095ccd44'}),
#     Document(
#         page_content='',
#         metadata={'description': None, 'tags': [], 'name': 'second instruction', 'id': 'ebe2b3c6-a118-4eac-be20-d8c1bfea72a4'})
# ]


@app.route('/instructions')
def instructions():
    """ instrustions """
    loader = NotionDBLoader(
        integration_token=NOTION_INTEGRATION_SECRET,
        database_id=NOTION_DB,
        request_timeout_sec=15,  # optional, defaults to 10
    )
    docs = loader.load()
    output = 'output: \n'
    for doc in docs:
        output = f"{output}\n# {doc.metadata['name']}\n{doc.page_content}"

    return output
