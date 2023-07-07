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
CORS(app)

llm = OpenAI(openai_api_key=OPENAI_API_KEY, temperature=0, model_name='gpt-3.5-turbo-16k')


def sanitize_string(input_string):
    """ to show the API key """
    first_letter = input_string[0]
    last_letter = input_string[-1]
    middle_length = len(input_string) - 2
    transformed_string = first_letter + '*' * middle_length + last_letter
    return transformed_string


def load_notion_db(database_id, requested_tag):
    """ loads db contents """
    loader = NotionDBLoader(
        integration_token=NOTION_INTEGRATION_SECRET,
        database_id=database_id
    )
    docs = loader.load()
    output = ''
    for doc in docs:
        doc_tags = doc.metadata.get('tags')
        if requested_tag in doc_tags:
            output += f"# {doc.metadata['name']}\n{doc.page_content}\n\n"
    return output


@app.route('/', methods=['GET'])
def home():
    """ home """
    return llm.predict("Company name for providing virtual care services?")


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
def cp_post():
    """ 
    POST handler for copilot
    """
    cmd = request.args.get('cmd')
    context = ""

    if request.method == 'POST':
        context = request.json
    if cmd == "write-careplan":
        consult_note = context['note']
        print(consult_note)
        diagnosis = consult_note['values']['icd11_diagnosis']
        assessment = consult_note['values']['assessment']
        plan = consult_note['values']['treatment_plan']
        context = f""" ASSESSMENT AND PLAN:
        ICD-11 Diagnosis: {diagnosis}
        Assessment: {assessment}
        Treatment Plan: {plan} """
    
    if cmd == 'suggest-next-steps':
        consult_note = context['note']
        print(consult_note)
        context = consult_note['subNotes']['next_steps_md_np']
        

    instructions_content = load_notion_db(NOTION_INSTRUCTIONS_DB, requested_tag=cmd)
    examples_content = load_notion_db(NOTION_EXAMPLES_DB, requested_tag=cmd)

    prompt = f"""
    You are a knowledgeable and effective medical assistant. Please follow the instructions carefully. Look at the Examples and only use Context-Input to generate.

    ### Instructions ###
    {instructions_content}
    \n\n

    ### Example ###
    {examples_content}
    \n\n
    
    ### Context-Input ### 
    {context}
    \n Output: \n
    
    """
    output = llm.predict(prompt)
    if cmd == 'write-careplan':
        json_output = {
            "summary": output.split('Recommendation:')[0],
            "recommendation": 'Recommendation:' + output.split('Recommendation:')[1]
        }
    elif cmd == 'suggest-next-steps':
        output = output.split('\n')
        final = []
        try:
            for item in output:
                final.append(item[2:])
        except KeyError:
            pass
        json_output = {
            "summary": output,
            "next-steps": final
        }
    else:
        json_output = {
            "summary": output
        }
    return json.dumps(json_output)

