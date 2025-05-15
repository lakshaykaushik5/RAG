import uuid
import os
from dotenv import load_dotenv
from langgraph.store.memory import InMemoryStore
from langchain_openai import ChatOpenAI


from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START,StateGraph,END,MessagesState
from langgraph.store.base import BaseStore
from langchain_core.messages import HumanMessage,SystemMessage
from langchain_core.runnables import RunnableConfig

load_dotenv()


MODEL_SYSTEM_MESSAGE = '''
You are a helpful assistant with memory that provides information about the user. 
If you have memory for this user, use it to personalize your responses.
Here is the memory (it may be empty): {memory}
'''

CREATE_MEMORY_INSTRUCTION = '''
You are collecting information about the user to personalize your responses.

CURRENT USER INFORMATION:
{memory}

INSTRUCTIONS:
1. Review the chat history below carefully
2. Identify new information about the user, such as:
   - Personal details (name, location)
   - Preferences (likes, dislikes)
   - Interests and hobbies
   - Past experiences
   - Goals or future plans
3. Merge any new information with existing memory
4. Format the memory as a clear, bulleted list
5. If new information conflicts with existing memory, keep the most recent version

Remember: Only include factual information directly stated by the user. Do not make assumptions or inferences.

Based on the chat history below, please update the user information:
'''



# in_memory_store = InMemoryStore()


# user_id = "1"
# namespace_for_memory = (user_id,"memories")

# key = str(uuid.uuid4())

# value = {"food_prefrence":"I like pizza"}

# in_memory_store.put(namespace_for_memory,key,value)

# # memories = in_memory_store.search(namespace_for_memory)
# memories = in_memory_store.get(namespace_for_memory,key)

# print(type(memories))
# print(memories)
# # print(memories[0].dict())

llm = ChatOpenAI(model=os.getenv('CHAT_MODEL_NAME'))

def call_model(state:MessagesState,config:RunnableConfig,store:BaseStore):
    '''Load memory from the store and use it to personalize the chatbot's response'''
    
    user_id = config['configurable']['user_id']

    namespace = ('memory',user_id)
    key = "user_memory"
    existing_memory = store.get(namespace,key)

    if existing_memory:
        existing_memory_context = existing_memory.value.get('memory')
    else:
        existing_memory_context = "No existing memory found"
    

    system_msg = MODEL_SYSTEM_MESSAGE.format(memory = existing_memory_context)

    response = llm.invoke([SystemMessage(content = system_msg)] + state['messages'])


    return {"messages":response}


def write_memory(state:MessagesState,config:RunnableConfig,store:BaseStore):
    '''Reflect on the chat history and save a memory to the store'''

    user_id = config['configurable']['user_id']
    namespace = ("memory",user_id)

    existing_memory = store.get(namespace,'user_memory')

    if existing_memory:
        existing_memory_context = existing_memory.value.get('memory')
    else:
        existing_memory_context = "No existing memory found"

    system_msg = CREATE_MEMORY_INSTRUCTION.format(memory = existing_memory_context)

    raw_memory = llm.invoke([SystemMessage(content=system_msg)]+state['messages'])

    key = "user_memory"
    store.put(namespace,key,{'memory':raw_memory})



builder = StateGraph(MessagesState)
builder.add_node("call_model",call_model)
builder.add_node("write_memory",write_memory)

builder.add_edge(START,"call_model")
builder.add_edge("call_model","write_memory")
builder.add_edge('write_memory',END)


across_thread_memory = InMemoryStore()

within_thread_memory = MemorySaver()


graph = builder.compile(checkpointer=within_thread_memory,store=across_thread_memory)

config = {"configurable":{"thread_id":"1","user_id":'2'}}



def call_llm_true():
    while True:
        query = input(" > :::")
        input_message = [HumanMessage(content=query)]
        events = graph.stream({"messages":input_message},config,stream_mode='values')

        for chunks in events:
            chunks['messages'][-1].pretty_print()



call_llm_true()