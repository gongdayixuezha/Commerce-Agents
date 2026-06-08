"""Embedding 模块 — 使用 ChromaDB 内置 ONNX 模型 + DeepSeek API 备选"""
from chromadb.utils import embedding_functions
import os

# ChromaDB 内置 ONNX 模型 (all-MiniLM-L6-v2, 384维)，本地运行免API
_default_ef = embedding_functions.DefaultEmbeddingFunction()

# DeepSeek 备选 (via OpenAI SDK)
_openai_client = None


def get_embedding(text: str) -> list[float]:
    """获取单条文本向量（优先使用本地模型）"""
    return _default_ef([text])[0]


def get_embeddings_batch(texts: list[str], batch_size: int = 50) -> list[list[float]]:
    """批量获取文本向量"""
    return _default_ef(texts)
