from pathlib import Path
import chromadb

DB_PATH = Path(__file__).resolve().parent.parent / "db" / "chroma"

print("DB Path:", DB_PATH)
print("Exists:", DB_PATH.exists())

client = chromadb.PersistentClient(path=str(DB_PATH))
collection = client.get_collection("langchain")
print("Collections:", client.list_collections())
results = collection.get(
    where={"uploaded_by": "admin"},
    include=["documents", "metadatas"]
)

for doc, meta in zip(results["documents"], results["metadatas"]):
    print(meta)
    print(doc)
    print("-" * 50)