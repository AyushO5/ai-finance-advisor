import chromadb
from sentence_transformers import SentenceTransformer

print("🔥 Loading RAG model...")

model = SentenceTransformer('all-MiniLM-L6-v2')
print("✅ Model loaded successfully")

client = chromadb.Client()
collection = client.get_or_create_collection("finance")


def detect_intent(query):
    query = query.lower()

    if "rent" in query:
        return "rent"
    elif "save" in query or "saving" in query:
        return "saving"
    elif "investment" in query:
        return "investment"
    else:
        return "general"


def load_data():
    with open("data/finance.txt", "r") as f:
        docs = f.readlines()

    for i, doc in enumerate(docs):
        embedding = model.encode(doc).tolist()

        collection.add(
            documents=[doc],
            embeddings=[embedding],
            ids=[str(i)]
        )


def query_rag(query):
    intent = detect_intent(query)

    query_embedding = model.encode(query).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=4
    )

    docs = results["documents"][0]

    if intent == "rent":
        docs = [d for d in docs if "rent" in d.lower()] + docs

    return "\n".join(docs[:2])