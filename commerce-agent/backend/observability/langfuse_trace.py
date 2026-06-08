"""Langfuse 可观测性集成 (v3.x API)"""
from config import LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY, LANGFUSE_HOST

_langfuse = None


def _init():
    global _langfuse
    if LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY:
        try:
            from langfuse import Langfuse
            _langfuse = Langfuse(
                public_key=LANGFUSE_PUBLIC_KEY,
                secret_key=LANGFUSE_SECRET_KEY,
                host=LANGFUSE_HOST,
            )
            print("[Langfuse] Connected")
        except Exception as e:
            print(f"[Langfuse] Connection failed: {e}")
    else:
        print("[Langfuse] Keys not configured, tracing disabled")


def get_langfuse_handler():
    """Return Langfuse callback handler. Returns None if not configured."""
    if _langfuse:
        try:
            from langfuse.langchain import CallbackHandler
            return CallbackHandler()
        except ImportError:
            pass
    return None


def get_langfuse():
    return _langfuse


_init()
