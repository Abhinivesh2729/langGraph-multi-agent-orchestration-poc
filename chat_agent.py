from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END, MessagesState
from langchain_ollama import ChatOllama

#state
class State(MessagesState):
    pass

#nodes
llm = ChatOllama(model="qwen2.5:3b", temperature=0.5)

def chat_ai(state: State):
    response = llm.invoke([SystemMessage(content="Respond below 10 words")  , *state["messages"]])
    return {"messages":response}

def print_message(state: State):
    print(state["messages"][-1].content)

#edges
graph_builder = StateGraph(State)
graph_builder.add_node("chat", chat_ai)
graph_builder.add_node("print", print_message)

graph_builder.add_edge(START, "chat")
graph_builder.add_edge("chat", "print")
graph_builder.add_edge("print", END)

#runtime
graph = graph_builder.compile()

messages = []

while True :
    userInput = input("User: ")
    if(userInput == "exit"):
        break
    else:
        messages.append(HumanMessage(content=userInput))
        result = graph.invoke({"messages": messages})
        messages = result["messages"]
        print(f"AI: {messages[-1].content}")