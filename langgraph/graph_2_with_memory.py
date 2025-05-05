from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph,START,END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode , tools_condition
from langchain_google_genai import ChatGoogleGenerativeAI

from dotenv import load_dotenv
import os


load_dotenv()

class State(TypedDict):
    messages:Annotated[list,add_messages]


memory = MemorySaver()


llm = ChatGoogleGenerativeAI(model=os.getenv('CHAT_MODEL_NAME'),google_api_key=os.getenv('GEMINI_API_KEY'))

def chatbot(state:State):
    return {'messages':[llm.invoke(state['messages'])]}


graph_builder = StateGraph(State)

graph_builder.add_node('chatbot',chatbot)

graph_builder.add_edge(START,'chatbot')
graph_builder.add_edge('chatbot',END)

config = {'configurable':{"thread_id":"1"}}

graph = graph_builder.compile(checkpointer = memory)



def call_llm():
    while True:
        query = input(' > ')
        user_input = {'messages':[{'role':'user','content':query}]}

        events =  graph.stream(user_input,config,stream_mode='values')
        for value in events:
            value['messages'][-1].pretty_print()

call_llm()