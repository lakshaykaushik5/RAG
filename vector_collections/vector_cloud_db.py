import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient,models
from embedder import openai_embedder
from langchain_qdrant import QdrantVectorStore



load_dotenv()

qdrant_api_key = os.getenv('QUANDRANT_API_KEY')
qdrant_url = os.getenv('QUANDRANT_URL')

client = QdrantClient(
    url=qdrant_url,
    api_key=qdrant_api_key
)



def add(collection_name,chunk_data):
    try:
        check_collection_exists = client.collection_exists(collection_name=collection_name)


        if not check_collection_exists:
            client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=3072, distance=Distance.COSINE),
            )


        QdrantVectorStore.from_documents(
            documents=chunk_data,
            collection_name=collection_name,
            embedding = openai_embedder,
        )
      
    except Exception as err:
        print(f"Error adding to db :: {err}")



def get_data(collection_name,query):
    try:
        retriever = QdrantVectorStore.from_existing_collection(
            collection_name=collection_name,
            embedding=openai_embedder
        )
        search_result = retriever.similarity_search(query=query)
        return search_result
    except Exception as err:
        print(f"Error getting data from db :: {err}")

