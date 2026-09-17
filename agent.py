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

def verbose(state: State):
    return {"message": f"The result for {state["operation"]} is {state["result"]}"}

def print_result(state: State):
    print(state["message"])

#Edges
graph = StateGraph(State)

graph.add_node("add",add_nums)
graph.add_node("verbose", verbose)
graph.add_node("print", print_result)

graph.add_edge(START, "add")
graph.add_edge("add", "verbose")
graph.add_edge("verbose","print")
graph.add_edge("print", END)


agent = graph.compile()

result = agent.invoke({'a':10,'b':17})
