from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph,START,END
from langgraph.graph.message import add_messages
from langchain_core.messages import ToolMessage
from langchain_core.tools import InjectedToolCallId,tool
from langgraph.types import Command, interrupt
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_tavily import TavilySearch
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode,tools_condition
from dotenv import load_dotenv
import os

load_dotenv()


class state(TypedDict):
    messages:Annotated[list,add_messages]
    name:str
    birthday:str


@tool
def human_assistance(name:str,birthday:str,tool_call_id:Annotated[str,InjectedToolCallId]):
    """Request assistance from a human"""
    human_response = interrupt(
        {
            'question':'Is this correct',
            'name':name,
            'birthday':birthday
        }
    )

    if human_response.get('correct','').lower().startswith('y'):
        verified_name = name
        verified_birthday = birthday
        response = "Correct"
    else:
        verified_name = human_response.get('name',name)
        verified_birthday = human_response.get('birthday',birthday)
        response = f"Made a correction :  {human_response}"
    
    state_update = {
        'name':verified_name,
        'birthday':verified_birthday,
        'response':[ToolMessage(response,tool_call_id=tool_call_id)]
    }

    return Command(update=state_update)


tool = TavilySearch(max_results=2)
tools = [tool,human_assistance]

llm = ChatGoogleGenerativeAI(model=os.getenv('CHAT_MODEL_NAME'),google_api_key = os.getenv('GEMINI_API_KEY'))

llm_with_tools=llm.bind_tools(tools)


def chatbot(state:state):
    message = llm_with_tools.invoke(state['messages'])
    assert len(message.tool_calls) <=1
    return {"messages":[message]}


tool_node = ToolNode(tools)

graph_builder = StateGraph(state)

graph_builder.add_node('chatbot',chatbot)
graph_builder.add_node('tools',tool_node)

graph_builder.add_edge(START,'chatbot')
graph_builder.add_conditional_edges('chatbot',tools_condition)
graph_builder.add_edge('tools','chatbot')

memory = MemorySaver()

graph = graph_builder.compile(checkpointer = memory)


config = {"configurable":{'thread_id':"4"}}

user_input = (
    "Can you look up when LangGraph was released? "
    "When you have the answer, use the human_assistance tool for review."
)
config = {"configurable": {"thread_id": "4"}}

events = graph.stream(
    {"messages": [{"role": "user", "content": user_input}]},
    config,
    stream_mode="values",
)
for event in events:
    if "messages" in event:
        event["messages"][-1].pretty_print()

print('=*='*200)

human_command = Command(
    resume={
        "name": "LangGraph",
        "birthday": "Jan 17, 2024",
    },
)

events = graph.stream(human_command, config, stream_mode="values")
for event in events:
    if "messages" in event:
        event["messages"][-1].pretty_print()



