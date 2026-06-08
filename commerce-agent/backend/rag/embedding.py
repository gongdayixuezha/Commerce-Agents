from openai import OpenAI
from config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL

_client = None

def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL, timeout=60.0)
    return _client

def get_embedding(text: str) -> list[float]:
    """获取单条文本的向量表示"""
    client = _get_client()
    response = client.embeddings.create(
        model="deepseek-v4-flash",
        input=text,
    )
    return response.data[0].embedding

def get_embeddings_batch(texts: list[str], batch_size: int = 20) -> list[list[float]]:
    """批量获取文本向量，每次最多 20 条，控制 API 调用频率"""
    client = _get_client()
    all_embeddings = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        response = client.embeddings.create(
            model="deepseek-v4-flash",
            input=batch,
        )
        all_embeddings.extend([d.embedding for d in response.data])
    return all_embeddings

