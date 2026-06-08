"""混合检索管道：向量语义 + 关键词加权 + RRF 融合排序"""
import json
import re
from pathlib import Path
from rag.vector_store import vector_store

class HybridRetriever:
    def __init__(self, k: int = 4):
        self.k = k
        self._products = None

    @property
    def products(self) -> dict:
        if self._products is None:
            path = Path(__file__).resolve().parent.parent / "data" / "products.json"
            if path.exists():
                with open(path, "r", encoding="utf-8") as f:
                    items = json.load(f)
                self._products = {p["id"]: p for p in items}
            else:
                self._products = {}
        return self._products

    def reload(self):
        self._products = None

    def retrieve(self, query: str, filters: dict = None) -> list[dict]:
        """混合检索主方法"""
        chroma_filter = self._build_chroma_filter(filters)
        results = vector_store.query(query, n_results=20, where=chroma_filter)

        ids = results["ids"][0] if results["ids"] else []
        distances = results.get("distances", [[]])[0] if results.get("distances") else []

        # 关键词加权
        keyword_scores = self._keyword_boost(query, ids)

        # RRF 融合排序
        final_scores = {}
        for rank, pid in enumerate(ids):
            rrf = 1.0 / (60 + rank + 1)
            final_scores[pid] = rrf + keyword_scores.get(pid, 0)

        sorted_ids = sorted(final_scores, key=final_scores.get, reverse=True)

        # 返回 top-K
        results = []
        for pid in sorted_ids[:self.k]:
            product = self.products.get(pid, {})
            if product:
                product_copy = dict(product)
                product_copy["_relevance"] = round(final_scores[pid], 4)
                results.append(product_copy)

        return results

    def _build_chroma_filter(self, filters: dict) -> dict | None:
        if not filters:
            return None
        conditions = []
        if "category" in filters and filters["category"]:
            conditions.append({"category": filters["category"]})
        if "price_min" in filters or "price_max" in filters:
            price_cond = {}
            if "price_min" in filters:
                price_cond["gte"] = float(filters["price_min"])
            if "price_max" in filters:
                price_cond["lte"] = float(filters["price_max"])
            if price_cond:
                conditions.append({"price": price_cond})
        if "brand" in filters and filters["brand"]:
            conditions.append({"brand": filters["brand"]})
        if len(conditions) == 1:
            return conditions[0]
        elif len(conditions) > 1:
            return {"AND": conditions}
        return None

    def _keyword_boost(self, query: str, ids: list[str]) -> dict:
        scores = {}
        query_lower = query.lower()
        for pid in ids:
            product = self.products.get(pid)
            if not product:
                continue
            boost = 0.0
            brand = product.get("brand", "").lower()
            category = product.get("category", "").lower()
            name = product.get("name", "").lower()
            subcategory = product.get("subcategory", "").lower()

            if brand and brand in query_lower:
                boost += 0.3
            if subcategory and subcategory in query_lower:
                boost += 0.2
            if category and category in query_lower:
                boost += 0.1
            # 商品名关键词命中
            keywords = re.split(r'[\s,，]+', query_lower)
            for kw in keywords:
                kw = kw.strip()
                if len(kw) >= 2 and kw in name:
                    boost += 0.05

            if boost > 0:
                scores[pid] = boost
        return scores

    def get_by_id(self, product_id: str) -> dict | None:
        return self.products.get(product_id)

    def get_by_ids(self, product_ids: list[str]) -> list[dict]:
        return [self.products[pid] for pid in product_ids if pid in self.products]


hybrid_retriever = HybridRetriever(k=4)

