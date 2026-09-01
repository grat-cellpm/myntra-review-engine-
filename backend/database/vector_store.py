import os
import pickle
import numpy as np
from fastembed import TextEmbedding

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "myntra_vector_db.pkl")

class SimpleVectorStore:
    def __init__(self):
        # BGE-small is extremely fast, highly accurate, and lightweight for local usage
        self.embedding_model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
        self.documents = []
        self.embeddings = []
        self.metadatas = []
        self.ids = []
        self._load()

    def _load(self):
        if os.path.exists(DB_PATH):
            with open(DB_PATH, "rb") as f:
                data = pickle.load(f)
                self.documents = data["documents"]
                self.embeddings = data["embeddings"]
                self.metadatas = data["metadatas"]
                self.ids = data["ids"]

    def save(self):
        with open(DB_PATH, "wb") as f:
            pickle.dump({
                "documents": self.documents,
                "embeddings": self.embeddings,
                "metadatas": self.metadatas,
                "ids": self.ids
            }, f)

    def upsert(self, documents, metadatas, ids):
        print(f"Generating embeddings for {len(documents)} documents...")
        vectors = list(self.embedding_model.embed(documents))
        
        for doc, meta, doc_id, vec in zip(documents, metadatas, ids, vectors):
            if doc_id in self.ids:
                idx = self.ids.index(doc_id)
                self.documents[idx] = doc
                self.metadatas[idx] = meta
                self.embeddings[idx] = vec
            else:
                self.ids.append(doc_id)
                self.documents.append(doc)
                self.metadatas.append(meta)
                self.embeddings.append(vec)
                
        self.save()

    def search(self, query: str, limit: int = 5):
        if not self.embeddings:
            return []
            
        query_vector = list(self.embedding_model.embed([query]))[0]
        
        q = np.array(query_vector)
        matrix = np.array(self.embeddings)
        
        # FastEmbed vectors are L2 normalized, so dot product == cosine similarity
        similarities = np.dot(matrix, q)
        
        top_indices = np.argsort(similarities)[::-1][:limit]
        
        results = []
        for idx in top_indices:
            results.append({
                "id": self.ids[idx],
                "document": self.documents[idx],
                "metadata": self.metadatas[idx],
                "score": float(similarities[idx])
            })
            
        return results

# Singleton
vector_store = SimpleVectorStore()
