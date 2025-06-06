import os 
from dotenv import load_dotenv
from openai import OpenAI
import json
from prompts import parallel_query_retrival_system_prompt
from vector_db import get_data


load_dotenv()

gemini_api_key = os.getenv('GEMINI_API_KEY')
model_name = os.getenv('CHAT_MODEL_NAME')
base_url = os.getenv('BASE_URL') or "https://generativelanguage.googleapis.com/v1beta/openai/"

client = OpenAI(
    api_key=gemini_api_key,
    base_url=base_url
)

    

def parallel_query(query,max_queries =10):
    try:

        #   QUERY GENERATION
        messages = []
        messages.append({'role':'system','content':parallel_query_retrival_system_prompt})
        messages.append({'role':'user','content':query})

        response = client.chat.completions.create(
            model = model_name,
            response_format={'type':'json_object'},
            messages=messages
        )
        
        parsed_output = json.loads(response.choices[0].message.content)
        parsed_output.append(query)

        final_output = []

        for q in parsed_output:
            if len(parsed_output) == len(final_output):
                break
            elif max_queries > 0:
                final_output.append(q)
                max_queries = max_queries - 1 
            else:
                break

        #   VECTOR DATABASE RETRIVAL


        db_data =  get_data('genai_cohort_v01',final_output[0])
        
        data_prompt_set = set()

        for sub_query in final_output:
            db_data = get_data('genai_cohort_v01',sub_query)
            for data in db_data:
                data_prompt_set.add(data.page_content)


        return data_prompt_set

    except Exception as err:
        print(f"Error in paralle query generating :: {err}")


def reciprocate_rank_fusion(query,max_queries = 10):

    try:
        messages = []
        messages.append({'role':'system','content':parallel_query_retrival_system_prompt})
        
        messages.append({'role':'user','content':query})

        response = client.chat.completions.create(
            model=model_name,
            response_format={'type':'json_object'},
            messages=messages
        )

        


        parsed_output = json.loads(response.choices[0].message.content)
        parsed_output.append(query)

        final_output = []
        for q in parsed_output:
            if len(parsed_output) == len(final_output):
                break
            elif max_queries > 0:
                final_output.append(q)
                max_queries = max_queries - 1 
            else:
                break

        # print(final_output)

        scores = {}
        data_chunks = {}
        k = 60
        for sub_query in final_output:
            db_data = get_data('genai_cohort_v01',sub_query)
            # print(db_data,'\n\n\n')
            for rank,chunk in enumerate(db_data):
                # print(chunk,'\n')
                doc_id = chunk.metadata['_id']
                # print(doc_id,"\n\n\n\n")
                scores[doc_id] = scores.get(doc_id,0) + 1/(k+rank+1)
                data_chunks[doc_id] = chunk.page_content

        sorted(scores.items(),key=lambda x:x[1],reverse=True)

        n = len(data_chunks)/2 + 1

        ranked_data = []

        for i,score in enumerate(scores):
            if i<=n:
                ranked_data.append(data_chunks[score])


        return ranked_data

        
    except Exception as err:
        print(f"Error Reciprocate Rank Fusion :: {err}")


def query_decomposition(query,max_queries=10):
    try:
        messages = []
        messages.append({'role':'system','content':parallel_query_retrival_system_prompt})

        messages.append({'role':'user','content':query})

        response = client.chat.completions.create(
            model=model_name,
            response_format={'type':'json_object'},
            messages=messages
        )

        parsed_output = json.loads(response.choices[0].message.content)

        parsed_output.append(query)

        final_output = []
        for q in parsed_output:
            if len(parsed_output) == len(final_output):
                break
            elif max_queries > 0:
                final_output.append(q)
                max_queries = max_queries - 1 
            else:
                break

        
        return final_output

    except Exception as err:
        print(f"Error in query decomposition  :: {err}")


