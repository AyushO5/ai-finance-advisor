import chromadb
from sentence_transformers import SentenceTransformer

print("🔥 Loading RAG model...")
# all-MiniLM-L6-v2 is a lightweight but effective model for semantic similarity tasks
model = SentenceTransformer('all-MiniLM-L6-v2')
print("✅ Model loaded successfully")

client = chromadb.Client(
    settings=chromadb.config.Settings(
        persist_directory="data/chroma"
    )
)
collection = client.get_or_create_collection("finance")

def load_data():
    # 🔥 check if data already exists
    if collection.count() > 0:
        print("⚡ Data already loaded, skipping...")
        return

    print("📄 Loading finance data...")

    with open("data/finance.txt", "r") as f:
        docs = f.readlines()

    for i, doc in enumerate(docs):
        embedding = model.encode(doc).tolist()

        collection.add(
            documents=[doc],
            embeddings=[embedding],
            ids=[str(i)]
        )
    print("✅ Data loaded and persisted")



def detect_intent(query):
    query = query.lower()

    if "rent" in query:
        return "rent"
    elif "tax" in query:
        return "tax"
    elif any(word in query for word in ["save", "saving"]):
        return "saving"
    elif any(word in query for word in ["invest", "investment", "mutual", "sip"]):
        return "investment"
    else:
        return "general"


def query_rag(query):
    intent = detect_intent(query)

    query_embedding = model.encode(query).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=4
    )

    docs = results.get("documents", [[]])[0]

    if not docs:
        return ""

    if intent == "rent":
        docs = [d for d in docs if "rent" in d.lower()] + docs
    elif intent == "tax":
        docs = [d for d in docs if "tax" in d.lower()] + docs

    return "\n".join(docs[:2])

load_data()
