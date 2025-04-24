from openai import OpenAI
from dotenv import load_dotenv
from routing_prompt import model_routing_system_prompt
from models import all_avaliable_models
import os
import json


load_dotenv()

chat_model = os.getenv('CHAT_MODEL_NAME')
base_url = os.getenv('BASE_URL')
gemini_api_key = os.getenv('GEMINI_API_KEY')


client = OpenAI(
    api_key=gemini_api_key,
    base_url=base_url
)


def choose_model(query):
    
    messages = []

    messages.append({'role':'system','content':model_routing_system_prompt})

    array_items = [str(item) for item in all_avaliable_models]
    separator = "\n---\n"
    combined_pdf_content = separator.join(array_items)


    messages.append({'role':'user','content':combined_pdf_content})
    messages.append({'role':'user','content':query})
    response = client.chat.completions.create(
        model=chat_model,
        response_format={'type':'json_object'},
        messages=messages
    )


    parsed_object = json.loads(response.choices[0].message.content)


    recomendations = parsed_object.get('response')
    print(recomendations)
    return recomendations



# recomended_model = choose_model("Write a python script to read,write pdf and excel file")
# print(recomended_model)

