#Reducer POC
from typing import Annotated, TypedDict
import operator
from langgraph.graph import StateGraph, END, START

#State
class State(TypedDict):
    message: Annotated[list[str], operator.add]

#nodes
def agent_1(state: State):
    return {"message":["Temperature is 27 degree"]}

def agent_2(state: State):
    return {"message":["Signs for heavy thunder strome"]}

#edges
graph_builder = StateGraph(State)
graph_builder.add_node("A1", agent_1)
graph_builder.add_node("A2", agent_2)

graph_builder.add_edge(START, "A1")
graph_builder.add_edge(START, "A2")
graph_builder.add_edge("A1", END)
graph_builder.add_edge("A2", END)

graph = graph_builder.compile()

print(graph.invoke({})["message"])

