from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph,START,END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode , tools_condition
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.types import Command, interrupt
from dotenv import load_dotenv
from langchain_core.tools import tool
import os


load_dotenv()

class State(TypedDict):
    messages:Annotated[list,add_messages]


memory = MemorySaver()


llm = ChatGoogleGenerativeAI(model=os.getenv('CHAT_MODEL_NAME'),google_api_key=os.getenv('GEMINI_API_KEY'))




@tool
def human_assistance(query:str)->str:
    """Request assistance from human ."""
    human_response = interrupt({'query':query})
    return human_response['data']


tools = [human_assistance]


llm_with_tools = llm.bind_tools(tools)
tool_node = ToolNode(tools=tools)

def chatbot(state:State):
    return {'messages':[llm_with_tools.invoke(state['messages'])]}


graph_builder = StateGraph(State)

graph_builder.add_node('chatbot',chatbot)

graph_builder.add_node('tools',tool_node)



graph_builder.add_edge(START,'chatbot')
graph_builder.add_conditional_edges(
    'chatbot',
    tools_condition
)
# graph_builder.add_edge('chatbot',END)

config = {'configurable':{"thread_id":"2"}}

graph = graph_builder.compile(checkpointer = memory)



def call_llm():
    while True:
        query = input(' > ')
        user_input = {'messages':[{'role':'user','content':query}]}

        events =  graph.stream(user_input,config,stream_mode='values')
        for value in events:
            if 'messages' in value:
                value['messages'][-1].pretty_print()
            else:
                snapshot = graph.get_state(config)
                print(snapshot.next)
                human_response=(
                    "No one can meet admin directly, only few people can meet to admin"
                )

                # call_llm()
                human_command = Command(resume={'data':human_response})
                events = graph.stream(human_command,config,stream_mode='values')
                for event in events:
                    if 'messages' in event:
                        event['messages'][-1].pretty_print()



call_llm()
    
    


