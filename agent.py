from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END

class State(TypedDict):
    a: int
    b: int
    result: int

def add_nums(state: State) -> State:
    return {"result":state["a"] + state["b"]}

graph = StateGraph(State)

graph.add_node("add",add_nums)
graph.add_edge(START, "add")
graph.add_edge("add", END)

agent = graph.compile()

result = agent.invoke({'a':10,'b':20})
print(result["result"])