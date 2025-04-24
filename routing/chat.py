from openai import OpenAI
from dotenv import load_dotenv
from routing_prompt import model_routing_system_prompt,chat_system_prompt
from models import all_avaliable_models
from model_select import choose_model
import os
import json


load_dotenv()

base_url = os.getenv('BASE_URL')
groq_base_url = os.getenv('GROQ_BASE_URL')
gemini_api_key = os.getenv('GEMINI_API_KEY')
groq_api_key = os.getenv('GROQ_API_KEY')
open_ai_key = os.getenv('OPEN_AI_KEY')

messages = []
messages.append({'role':'system','content':chat_system_prompt})

while True:
    query = input(' >> ')
    if query == 'end':
        break
    
    
    model_name = choose_model(query=query)

    model_url = model_name.split('-')[0]

    final_url = None
    final_api_key = None
    if model_url == "gemini":
        final_url = base_url
        final_api_key = gemini_api_key
    elif model_url == 'deepseek':
        base_url = groq_base_url
        final_api_key = groq_api_key
    else:
        final_api_key = open_ai_key

    client = OpenAI(
        api_key=final_api_key,
        base_url=final_url
    )

    messages.append({'role':'user','content':query})

    while True:
        response = client.chat.completions.create(
            model=model_name,
            response_format={'type':'json_object'},
            messages=messages
        )
        
        parsed_output = json.loads(response.choices[0].message.content)

        # 💭 🧠 🔎 🌐 🤖

        messages.append({'role':'assistant','content':response.choices[0].message.content})

        if parsed_output.get('step') == 'plan':
            print(f"💭  - {parsed_output.get('response')}",'\n')
        
        if parsed_output.get('step') == 'think':
            print(f"🧠  - {parsed_output.get('response')}",'\n')

        if parsed_output.get('step') == 'output':
            print(f"🌐  - {parsed_output.get('response')}",'\n')

        if parsed_output.get('step') == 'validate':
            print(f"🔎  - {parsed_output.get('response')}",'\n')

        if parsed_output.get('step') == 'response':
            print("_"*100)
            print(f"🤖  - {parsed_output.get('response')}")
            break
