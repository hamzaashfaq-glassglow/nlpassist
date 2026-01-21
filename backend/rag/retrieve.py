import faiss
import pickle
from sentence_transformers import SentenceTransformer

embedder = SentenceTransformer("all-MiniLM-L6-v2")

index = faiss.read_index("data/faiss.index")

with open("data/chunks.pkl", "rb") as f:
    chunks = pickle.load(f)

print("=== DEBUG START ===")
print("Total chunks loaded:", len(chunks))

rag_chunks = [c for c in chunks if "Retrieval-Augmented Generation" in c or "RAG" in c]
print("RAG chunks found:", len(rag_chunks))

if rag_chunks:
    print("RAG chunk sample:\n", rag_chunks[0])

print("=== DEBUG END ===")


def retrieve(question, top_k=3):
    q_vec = embedder.encode([question])
    distances, indices = index.search(q_vec, top_k)
    return [chunks[i] for i in indices[0]], distances[0]
