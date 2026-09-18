from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_core.tools import tool as tools
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.prebuilt.tool_node import tools_condition, ToolNode
from langgraph.graph import StateGraph, START, END, MessagesState
from langchain_qdrant import QdrantVectorStore
from langchain_core.documents import Document
from langgraph.checkpoint.memory import InMemorySaver

#Rag-Ingestion
docs = [
    Document(
        page_content="Employee Leave Policy: Full-time staff receive 12 paid casual leaves and 8 sick leaves annually. Leave requests must be submitted at least 3 days in advance, except in medical emergencies.",
        metadata={"category": "HR", "topic": "Leave Policy"}
    ),
    Document(
        page_content="Customer Refund Policy: Full refunds or replacements are issued if an order arrives damaged, incorrect, or spoiled. Requests must be submitted with a photo via the app within 2 hours of delivery.",
        metadata={"category": "Customer Support", "topic": "Refund Policy"}
    ),
    Document(
        page_content="Delivery Time Policy: The average delivery time is 30 to 40 minutes under normal conditions. During peak hours or severe weather, delivery times may extend up to 50 minutes.",
        metadata={"category": "Operations", "topic": "Delivery Time"}
    ),
    Document(
        page_content="Signature Pizza Recipes: Margherita uses San Marzano tomato sauce, fresh mozzarella, and basil. Pepperoni Feast uses spiced marinara, aged mozzarella, and sliced beef/pork pepperoni.",
        metadata={"category": "Kitchen", "topic": "Classic Recipes"}
    ),
    Document(
        page_content="Specialty Pizza Recipes: BBQ Chicken includes slow-cooked chicken chunks, smoky barbecue sauce, red onions, and cheddar. Veggie Delight features bell peppers, olives, mushrooms, and sweet corn.",
        metadata={"category": "Kitchen", "topic": "Specialty Recipes"}
    ),
]

embedding_model = OllamaEmbeddings(model="nomic-embed-text:latest")
store = QdrantVectorStore.from_documents(
    documents=docs,
    embedding=embedding_model,
    force_recreate=True,
    path="./agent-db",
    collection_name="my-pizza-store"
)


#Tools
@tools
def get_pizza_shop_info(query: str) -> list[str]:
    """While asking a question about the pizza shop as string as a parameter, this function the relevant information in list of strings"""
    return store.similarity_search(query, k=3)
@tools
def get_current_weather(city: str) -> str:
    """While passing the city name as string to this function as parameter, this function will return the current weather at the city as string"""
    return f"It is snowing in {city}"

#LLM
llm = ChatOllama(model="qwen2.5:3b",temperature=0.3)
llm_with_tools = llm.bind_tools([get_pizza_shop_info, get_current_weather])

#nodes
def chat_node(state: MessagesState):
    response = llm.invoke([SystemMessage("YOU ARE A SUPPORT AGENT EMPLOYEED IN A PIZZA SHOP, YOUR NAME IS GARRY ELISON - YOU HAVE A TOOL TO GET PIZZA SHOP INFO BUT DONT CALL THE TOOL EVERYTIME ONLY CALL THE TOOL IF THE CUSTOMER ASKED ABOUT THE PIZZA SHOP, MENU, POLICIES"), *state["messages"]])
    return {"messages":[response]}

tool_node = ToolNode([get_current_weather, get_pizza_shop_info])

memory = InMemorySaver()

#Edge
builder = StateGraph(MessagesState)
builder.add_node("tools", tool_node)
builder.add_node("chat",chat_node)

builder.add_edge(START, "chat"),
builder.add_conditional_edges("chat", tools_condition)
builder.add_edge("tools","chat")
builder.add_edge("chat", END)

#runtime
graph = builder.compile(checkpointer=memory)

while True:
    userInput = input("User: ")
    print("AI: ", end=" ")
    for message, meta in graph.stream({"messages":[HumanMessage(userInput)]},config={"configurable":{"thread_id":"27"}} , stream_mode="messages"):
        print(message.content, end="", flush=True)
    print()

