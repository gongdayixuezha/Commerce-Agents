"""评估管道：批量评估检索效果和回答质量

指标：
- Recall@4: 前4个返回结果中相关商品比例
- MRR: 平均倒数排名
- Answer Relevancy: 回复相关性（Ragas）
- Faithfulness: 回复忠实度（Ragas）
"""
import json
import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from rag.retriever import hybrid_retriever
from rag.vector_store import vector_store


def load_test_queries() -> list[dict]:
    path = Path(__file__).parent / "test_queries.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def evaluate_recall_at_k(queries: list[dict], k: int = 4) -> dict:
    """计算 Recall@K 和 MRR"""
    recalls = []
    mrrs = []

    for q in queries:
        results = hybrid_retriever.retrieve(q["query"], {})
        result_categories = [p.get("category", "") for p in results[:k]]
        expected_cat = q.get("expected_category", "")

        # Simplified recall: check if any result category matches expected
        hit = any(c == expected_cat for c in result_categories)
        recalls.append(1.0 if hit else 0.0)

        # MRR: first match position
        for rank, cat in enumerate(result_categories, 1):
            if cat == expected_cat:
                mrrs.append(1.0 / rank)
                break
        else:
            mrrs.append(0.0)

    avg_recall = sum(recalls) / len(recalls) if recalls else 0
    avg_mrr = sum(mrrs) / len(mrrs) if mrrs else 0

    return {
        "recall@4": round(avg_recall, 4),
        "mrr": round(avg_mrr, 4),
        "total_queries": len(queries),
        "product_count": vector_store.count(),
    }


def main():
    print("=" * 50)
    print("Commerce Agent - Evaluation Pipeline")
    print("=" * 50)

    # Check vector store
    count = vector_store.count()
    if count == 0:
        print("  Vector store is empty! Run vector indexing first.")
        return

    print(f"  Products in vector store: {count}")

    # Load test queries
    queries = load_test_queries()
    print(f"  Test queries loaded: {len(queries)}")

    # Run evaluation
    print("\n--- Recall@4 + MRR ---")
    metrics = evaluate_recall_at_k(queries, k=4)
    for key, value in metrics.items():
        print(f"  {key}: {value}")

    # Summary
    print("\n--- Summary ---")
    print(f"  Recall@4: {metrics['recall@4']:.2%}")
    print(f"  MRR: {metrics['mrr']:.4f}")
    print(f"  Products: {metrics['product_count']}")

    # Save results
    output = {
        "metrics": metrics,
        "config": {"k": 4, "retrieval": "hybrid"},
    }
    out_path = Path(__file__).parent / "evaluation_results.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n  Results saved to: {out_path}")
    print("=" * 50)


if __name__ == "__main__":
    main()
