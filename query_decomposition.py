import os
from dotenv import load_dotenv
from openai import OpenAI
from prompts import basic_rag_system_prompt
from advance_rag import query_decomposition
from vector_db import get_data
import json

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
    query = input(' > ')
    if query == 'end':
        break

    messages.append({'role':'user','content':query})

    multi_query=query_decomposition(query)

    for sub_query in multi_query:

        pdf_chunk = get_data('genai_cohort_v01',sub_query)

        final_pdf_content = [data.page_content for data in pdf_chunk]

        seperator = '\n---\n'
        pdf_string = seperator.join(final_pdf_content)

        messages.append({'role':'user','content':pdf_string})

        response = client.chat.completions.create(
            model=chat_model,
            response_format={'type':'json_object'},
            messages=messages
        )

        parsed_otput = json.loads(response.choices[0].message.content)

        messages.pop()

        messages.append({'role': 'assistant', 'content': response.choices[0].message.content})
    

    print('_'*100)
    print('OUTPUT','\n\n')
    final_ans = json.loads(messages[len(messages)-1]['content'])
    print(final_ans.get('response'))
    


