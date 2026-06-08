"""Langfuse 可观测性集成"""
from langfuse import Langfuse
from langfuse.callback import CallbackHandler
from config import LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY, LANGFUSE_HOST

_langfuse = None
_langfuse_handler = None


def _init():
    global _langfuse, _langfuse_handler
    if LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY:
        try:
            _langfuse = Langfuse(
                public_key=LANGFUSE_PUBLIC_KEY,
                secret_key=LANGFUSE_SECRET_KEY,
                host=LANGFUSE_HOST,
            )
            _langfuse_handler = CallbackHandler(
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
    return _langfuse_handler


def get_langfuse():
    return _langfuse


_init()
