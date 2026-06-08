"""ChromaDB 向量库封装 — 支持本地和远程模式"""
import os
from pathlib import Path
import chromadb
from config import CHROMA_HOST, CHROMA_PORT
from rag.embedding import get_embedding, get_embeddings_batch

# 本地持久化路径
CHROMA_DATA_DIR = str(Path(__file__).resolve().parent.parent.parent / "chroma_data")


class VectorStore:
    def __init__(self, collection_name: str = "products", use_remote: bool = False):
        if use_remote:
            self.client = chromadb.HttpClient(
                host=CHROMA_HOST, port=CHROMA_PORT,
                settings=chromadb.Settings(anonymized_telemetry=False)
            )
        else:
            os.makedirs(CHROMA_DATA_DIR, exist_ok=True)
            self.client = chromadb.PersistentClient(
                path=CHROMA_DATA_DIR,
                settings=chromadb.Settings(anonymized_telemetry=False)
            )

        try:
            self.collection = self.client.get_collection(name=collection_name)
        except Exception:
            self.collection = self.client.create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}
            )

    def add_products(self, products: list[dict]):
        if not products:
            return
        ids = [p["id"] for p in products]
        documents = [p["description"] for p in products]
        metadatas = [{
            "name": p["name"], "category": p["category"],
            "subcategory": p.get("subcategory", ""), "price": float(p["price"]),
            "brand": p["brand"], "rating": float(p["rating"]),
            "stock": int(p["stock"]), "sales_count": int(p.get("sales_count", 0))
        } for p in products]

        embeddings = get_embeddings_batch(documents, batch_size=20)

        self.collection.add(ids=ids, documents=documents, metadatas=metadatas, embeddings=embeddings)

    def query(self, query_text: str, n_results: int = 10, where: dict = None) -> dict:
        query_embedding = get_embedding(query_text)
        return self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where,
            include=["documents", "metadatas", "distances"]
        )

    def count(self) -> int:
        return self.collection.count()

    def reset(self):
        try:
            self.client.delete_collection("products")
        except Exception:
            pass
        self.collection = self.client.create_collection(
            name="products", metadata={"hnsw:space": "cosine"}
        )


vector_store = VectorStore()
