import chromadb
import json
from chromadb.utils import embedding_functions

client = chromadb.PersistentClient(path="./clinic_db")
embedding_fn = embedding_functions.DefaultEmbeddingFunction()

collection = client.get_or_create_collection(
    name="clinic_faqs",
    embedding_function=embedding_fn
)

def load_faqs():
    with open("clinic_data.json", "r", encoding="utf-8") as f:
        clinic_faqs = json.load(f)

    existing = collection.get()["ids"]
    new_items = [f for f in clinic_faqs if f["id"] not in existing]
    if new_items:
        collection.add(
            documents=[f["text"] for f in new_items],
            ids=[f["id"] for f in new_items]
        )
        print(f"Loaded {len(new_items)} new FAQs into vector DB")
    else:
        print("FAQs already loaded")

def search_faqs(query, n_results=3):
    results = collection.query(query_texts=[query], n_results=n_results)
    return results["documents"][0]

if __name__ == "__main__":
    load_faqs()