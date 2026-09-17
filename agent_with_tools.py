from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, START, END, MessagesState
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode, tools_condition

#tools
@tool
def get_current_temperature(city: str) -> str:
    """While passing city name as parameter, we will get the current temperature as string"""
    return f"current temperature in {city} is 27 degree celcious"

#nodes

llm = ChatOllama(model="qwen2.5:3b", temperature=0.5)
llm_with_tools = llm.bind_tools([get_current_temperature])
def chat_ai(state: MessagesState):
    response = llm_with_tools.invoke([SystemMessage(content="Respond friendly to the messages") ,*state["messages"]])
    return {"messages": response}

def print_message(state: MessagesState):
    print(f"AI: {state["messages"][-1].content}")

tool_node = ToolNode([get_current_temperature])

#edges
graph_builder = StateGraph(MessagesState)
graph_builder.add_node("chat", chat_ai)
graph_builder.add_node("print", print_message)
graph_builder.add_node("tools", tool_node)

graph_builder.add_edge(START, "chat")
graph_builder.add_conditional_edges("chat", tools_condition)
graph_builder.add_edge("tools","chat")
graph_builder.add_edge("tools","print")
graph_builder.add_edge("print", END)

#runtime
graph = graph_builder.compile()

messages = []

while True:
    userInput = input("User: ")
    if(userInput == "exit"):
        print("Bye!")
        break
    else:
        messages.append(HumanMessage(content=userInput))
        result = graph.invoke({"messages": messages})
        messages = result["messages"]