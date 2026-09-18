from langgraph.graph import StateGraph, MessagesState, START, END
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.prebuilt.tool_node import ToolNode, tools_condition
from langchain_ollama import ChatOllama
import sqlite3

#state
class State(MessagesState):
    userId: int

#tools
@tool
def get_age(userId: int) -> str:
    """While passing the user id as int this function returns the age of the user as string """
    if(userId > 5):
        return f"The age of the user-{userId} is 81"
    else:
        return f"The user-{userId} age is 27"

#LLM
llm = ChatOllama(model="qwen2.5:3b",temperature=0.3)
llm_with_tools = llm.bind_tools([get_age])

#Memory
connection = sqlite3.connect("agent.db",check_same_thread=False)
memory = SqliteSaver(conn=connection)

#Nodes
def chat_node(state: State):
    response = llm_with_tools.invoke([SystemMessage(f"You are a Ai Assistent, your name is Jeff, current userId is {state["userId"]}"),*state["messages"]])
    return {"messages": [response]}

def print_message(state: State):
    print("")
    #print(f"AI: {state['messages'][-1].content}")

tool_node = ToolNode([get_age])

#Router
def custom_router(state: State) -> str:
    if(state["messages"][-1].tool_calls):
        return "tools"
    else:
        return "print"
    
#Edge
builder = StateGraph(State)
builder.add_node("chat", chat_node)
builder.add_node("print", print_message)
builder.add_node("tools", tool_node)

builder.add_edge(START, "chat")
builder.add_conditional_edges("chat",custom_router,{"tools":"tools","print":"print"})
builder.add_edge("tools","chat")
builder.add_edge("print",END)

#runtime
graph = builder.compile(checkpointer=memory)
userId = int(input("User ID: "))

while True:
    userInput = input(f"User-{userId}: ")
    if(userInput == "exit"):
        break
    elif(userInput == "/user"):
        userId = int(input("User ID: "))
    else:
        for chunks, metadata in graph.stream({"messages":[HumanMessage(content=userInput)], "userId": userId}, config={"configurable":{"thread_id": userId}}, stream_mode="messages"):
            print(chunks.content, end="", flush=True)