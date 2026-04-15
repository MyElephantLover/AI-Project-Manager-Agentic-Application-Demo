import os
from langchain_text_splitters import CharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from openai import OpenAI


KB_PATH = "kb"
CHROMA_PATH = "data/chroma"


def load_docs():
    docs = []
    for filename in os.listdir(KB_PATH):
        if filename.endswith(".md"):
            path = os.path.join(KB_PATH, filename)
            with open(path, "r", encoding="utf-8") as f:
                docs.append({
                    "source": filename,
                    "content": f.read()
                })
    return docs


def build_vector_store():
    docs = load_docs()
    splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)

    texts = []
    metadatas = []

    for doc in docs:
        chunks = splitter.split_text(doc["content"])
        for chunk in chunks:
            texts.append(chunk)
            metadatas.append({"source": doc["source"]})

    embeddings = OpenAIEmbeddings()

    db = Chroma.from_texts(
        texts=texts,
        embedding=embeddings,
        metadatas=metadatas,
        persist_directory=CHROMA_PATH,
    )
    return db


def load_vector_store():
    embeddings = OpenAIEmbeddings()
    return Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=embeddings,
    )

def query_kb(query: str, k: int = 3) -> str:
    db = load_vector_store()
    results = db.similarity_search(query, k=k)

    if not results:
        return "No relevant knowledge found."

    context = "\n\n".join([doc.page_content for doc in results])
    return context


client = OpenAI()

def generate_triage_response(task_text: str, context_docs):
    context_text = "\n\n".join(
        [
            f"Source: {doc.metadata.get('source', 'unknown')}\n{doc.page_content}"
            for doc in context_docs
        ]
    )

    prompt = f"""
You are an engineering project intake assistant.

A new ClickUp task needs triage.

Task:
{task_text}

Relevant internal docs:
{context_text}

Return a concise recommendation in this format:

Category: <Bug / Feature Request / Enhancement / Technical Debt / Support / Operations>
Priority: <P0 / P1 / P2 / P3>
Owner: <Frontend Team / Backend Team / Data Team / Platform Team>
Next Action: <Fix immediately / Move to backlog / Request more information / Move to In Progress>
Reasoning: <2-3 short sentences>

Only use the information provided.
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )

    return response.choices[0].message.content