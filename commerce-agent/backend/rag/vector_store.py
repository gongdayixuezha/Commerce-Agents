import chromadb
from chromadb.config import Settings
from config import CHROMA_HOST, CHROMA_PORT
from rag.embedding import get_embedding, get_embeddings_batch

class VectorStore:
    def __init__(self, collection_name: str = "products"):
        self.client = chromadb.HttpClient(
            host=CHROMA_HOST,
            port=CHROMA_PORT,
            settings=Settings(anonymized_telemetry=False)
        )
        try:
            self.collection = self.client.get_collection(name=collection_name)
        except Exception:
            self.collection = self.client.create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}
            )

    def add_products(self, products: list[dict]):
        """批量添加商品到向量库"""
        if not products:
            return
        ids = [p["id"] for p in products]
        documents = [p["description"] for p in products]
        metadatas = [{
            "name": p["name"],
            "category": p["category"],
            "subcategory": p.get("subcategory", ""),
            "price": p["price"],
            "brand": p["brand"],
            "rating": p["rating"],
            "stock": p["stock"],
            "sales_count": p.get("sales_count", 0)
        } for p in products]

        # 分批获取向量
        embeddings = get_embeddings_batch(documents, batch_size=20)

        self.collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings
        )

    def query(self, query_text: str, n_results: int = 10, where: dict = None) -> dict:
        """向量语义检索"""
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
        """重建 collection（用于重新索引）"""
        try:
            self.client.delete_collection("products")
        except Exception:
            pass
        self.collection = self.client.create_collection(
            name="products",
            metadata={"hnsw:space": "cosine"}
        )


# 全局单例
vector_store = VectorStore()
