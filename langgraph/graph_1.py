from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph , START,END
from dotenv import load_dotenv
from langgraph.graph.message import add_messages
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import tool
from langchain_core.messages import ToolMessage
from langgraph.prebuilt import ToolNode
import json
import os

load_dotenv()




class State(TypedDict):
    messages:Annotated[list,add_messages]


llm = ChatGoogleGenerativeAI(model=os.getenv('CHAT_MODEL_NAME'),google_api_key = os.getenv('GEMINI_API_KEY'))

@tool
def make_payments():
    """
    redirect to payment gateway when user ask to payment or plans opetions
    """

    return "redirecting to payment gateway"


tools = [make_payments]
llm_with_tools = llm.bind_tools(tools)


class BasicToolNode:
    """A node that runs the tools requested in the laste AIMessage"""
    def __init__(self,tools:list)->None:
        self.tool_by_name={tool.name:tool for tool in tools}
    
    def __call__(self,inputs:dict):
        if messages := inputs.get('messages',[]):
            message = messages[-1]
        else:
            raise ValueError('No message found in input')
        outputs = []

        for tool_call in message.tool_call:
            tool_result = self.tools_by_name[tool_call['name']].invoke(tool_call['args'])
            outputs.append(
                ToolMessage(
                    content=json.dumps(tool_result),
                    name=tool_call['name'],
                    tool_call_id=tool_call['id']
                )
            )
        
        return {'messages':outputs}


tool_node = ToolNode(tools=tools)


def route_tools(state:State):
    """
    Use in the conditional_edge to route to the ToolNode if the last message has tool calls .Otherwise ,route to the end
    """
    print('----------------------state------------------------------')
    print(state)
    print('\n\n\n')

    if isinstance(state,list):
        ai_message = state[-1]
    elif messages := state.get('messages',[]):
        ai_message = messages[-1]
    else:
        raise ValueError(f"No message found in input state to tool_edge :::: {state}")
    
    if hasattr(ai_message,'tool_calls') and len(ai_message.tool_calls)>0:
        print('---------using-tools----------')
        return 'tools'
    
    return END


def chatbot(state:State):
    return {'messages':[llm_with_tools.invoke(state['messages'])]}



graph_builder = StateGraph(State)

graph_builder.add_node('chatbot',chatbot)
graph_builder.add_node('tool',tool_node)

graph_builder.add_edge(START,'chatbot')
graph_builder.add_conditional_edges('chatbot',route_tools)
graph_builder.add_edge('chatbot',END)


graph = graph_builder.compile()


def call_llm():
    while True:
        query = input(' > ')
        user_input = {'messages':[{'role':'user','content':query}]}
        for event in graph.stream(user_input):
            # print('*'*100)
            # print(event)
            # print('*'*100)
            for value in event.values():
                # print(value)
                print('*'*100)
                print('Assistant :',value['messages'][-1].content)


call_llm()