import os
from dotenv import load_dotenv
from openai import OpenAI
import json
from prompts import basic_rag_system_prompt
from vector_db import get_data
from advance_rag import parallel_query


load_dotenv()

gemini_api_key = os.getenv('GEMINI_API_KEY')
chat_model = os.getenv('CHAT_MODEL_NAME')
base_url = os.getenv('BASE_URL') or "https://generativelanguage.googleapis.com/v1beta/openai/"

client = OpenAI(
    api_key=gemini_api_key,
    base_url=base_url
)

messages = []
messages.append({'role':'system','content':basic_rag_system_prompt})

while True:
    query=input(" > ")
    if query == "end":
        break
    messages.append({'role':'user','content':query})
    
    # ----------basiic-rag---------------------------
    # pdf_content = get_data('genai_cohort_v01',query)
    # pdf_content = [data.page_content for data in pdf_content]

    # ----------parallel-retrival-query--------------
    pdf_content = parallel_query(query,max_queries=10)
    


    separator = "\n---\n"
    combined_pdf_content = separator.join(pdf_content)

    messages.append(({'role':'user','content':combined_pdf_content}))

    while True:
        response = client.chat.completions.create(
            model=chat_model,
            response_format={'type':'json_object'},
            messages=messages
        ) 
        # 🧠 🔎 🤖 🌐

        parsed_output = json.loads(response.choices[0].message.content)
        # print(parsed_output)
        messages.append({'role': 'assistant', 'content': response.choices[0].message.content})
        if parsed_output.get('step') == 'plan':
            print(f"🧠  - {parsed_output.get('response')}")
        
        if parsed_output.get('step') == 'search':
            print(f"🔎  - {parsed_output.get('response')}")

        if parsed_output.get('step') == 'analyze':
            print(f"🌐  - {parsed_output.get('response')}")

        if parsed_output.get('step') == 'output':
            print("_"*100)
            messages = []
            print(f"🤖  - {parsed_output.get('response')}")
            break
    