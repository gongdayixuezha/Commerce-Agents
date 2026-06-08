"""评估数据集构建"""
import json
from pathlib import Path


def load_test_queries() -> list[dict]:
    path = Path(__file__).resolve().parent.parent.parent / "evaluation" / "test_queries.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def create_langfuse_dataset():
    """将测试查询上传到 Langfuse Dataset"""
    from observability.langfuse_trace import get_langfuse

    langfuse = get_langfuse()
    if not langfuse:
        print("Langfuse not configured, skipping dataset upload")
        return

    queries = load_test_queries()
    dataset_name = "commerce-agent-eval"

    for q in queries:
        langfuse.create_dataset_item(
            dataset_name=dataset_name,
            input=q["query"],
            expected_output=q.get("expected_category", ""),
            metadata={
                "keywords": q.get("keywords", []),
            },
        )

    print(f"Uploaded {len(queries)} items to Langfuse dataset '{dataset_name}'")
