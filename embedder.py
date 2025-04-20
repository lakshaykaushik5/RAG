from langchain_openai import OpenAIEmbeddings
import os
from dotenv import load_dotenv

load_dotenv()

model_name = os.getenv('EMBEDDING_MODEL_NAME')
openai_api_key = os.getenv('OPEN_AI_KEY')

def openai_embedder():
    try:
        embedder = OpenAIEmbeddings(model=model_name,api_key=openai_api_key)
        return embedder
    except Exception as err:
        print(f"Error in openai_embedder :: {err}")


openai_embedder = openai_embedder()