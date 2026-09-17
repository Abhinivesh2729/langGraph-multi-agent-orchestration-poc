from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END

#Define State
class State(TypedDict):
    a: int
    b: int
    result: int
    operation: str
    message: str

# Nodes
def add_nums(state: State):
    return {"result":state["a"] + state["b"], "operation": "Addition"}

def check_result(state: State):
    if(state["result"] > 100):
        return "large"
    else:
        return "small"

def large_result(state: State):
    return {"message": "Result is large"}

def small_result(state: State):
    return {}

def verbose(state: State):
    return {"message": f"The result for {state["operation"]} is {state["result"]}"}

def print_result(state: State):
    print(state["message"])

#Edges
graph = StateGraph(State)

graph.add_node("add",add_nums)
graph.add_node("verbose", verbose)
graph.add_node("print", print_result)
graph.add_node("large", large_result)
graph.add_node("small", small_result)

graph.add_edge(START, "add")
graph.add_conditional_edges("add", check_result, {"large":"large","small":"small"})
graph.add_edge("large","print")
graph.add_edge("small","verbose")
graph.add_edge("verbose", "print")
graph.add_edge("print",END)

agent = graph.compile()

result = agent.invoke({'a':10,'b':97})
