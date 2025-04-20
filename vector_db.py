import os
from dotenv import load_dotenv
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient, models
from embedder import openai_embedder

clieent = QdrantClient()

load_dotenv()


vectordb_url = os.getenv('QUANDRANT_URL')

def add_data(chunk_data,collection_name):
    try:
        check_collection_exists= clieent.collection_exists(collection_name=collection_name)

        if not check_collection_exists:
            vector_store = QdrantVectorStore.from_documents(
                documents=chunk_data,
                url=vectordb_url,
                collection_name=collection_name,
                embedding=openai_embedder
            )
        else:
            vector_store = QdrantVectorStore.from_existing_collection(
                url=vectordb_url,
                collection_name=collection_name,
                embedding=openai_embedder,
                score_threshold=0.75
            )

        print("...Data Added to Collection Successfully...")
    except Exception as err:
        print(f"Error adding to db :: {err}")


def get_data(collection_name,query):
    try:

        retriever = QdrantVectorStore.from_existing_collection(
                url=vectordb_url,
                collection_name=collection_name,
                embedding=openai_embedder
            )
        
        search_result = retriever.similarity_search(query=query)
        return search_result
    except Exception as err:
        print(f"Error getting data from db :: {err}")
        
