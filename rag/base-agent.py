from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter

docs = [
    Document(
        page_content="Mr Abhi is a great scientiest and a wonderfull visionary who has great contributions on AI and Cyber Security",
        metadata={"source":"Trust me bro"}
    ),
    Document(
            page_content="Thinai is an offline android llm app which uses custom built llama.cpp to run offline llms in the android",
            metadata={"source":"Trust me bro"}
        ),
]

splitter = RecursiveCharacterTextSplitter(
    chunk_size = 30,
    chunk_overlap = 10
)

chunks = splitter.split_documents(documents=docs)

embedding_model = OllamaEmbeddings(model="nomic-embed-text:latest")

store = QdrantVectorStore.from_documents(
    documents=chunks,
    embedding=embedding_model,
    collection_name = "my-vector-store",
    path="./agent-db",
    force_recreate=True
)


result = store.similarity_search("who is Abhi", k=1)

for chunk in result:
    print(chunk.page_content)
