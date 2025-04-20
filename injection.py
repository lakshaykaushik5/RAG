from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
import os
from vector_db import add_data


load_dotenv()

openai_api_key = os.getenv('OPEN_AI_KEY')


file_path = "./cpython-internals-sample-chapters.pdf"

loader = PyPDFLoader(file_path)

docs = loader.load()




text_splitters = RecursiveCharacterTextSplitter(chunk_size = 1000,chunk_overlap=200)

chunks_docs = text_splitters.split_documents(docs)

add_data(chunks_docs,"genai_cohort_v01")


print(".....Injection-done............")



