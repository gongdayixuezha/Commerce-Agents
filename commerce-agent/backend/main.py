"""Commerce Agent - FastAPI Backend"""
import traceback
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agent.agent import chat
from rag.vector_store import vector_store
from rag.retriever import hybrid_retriever
from payment.webhook import router as webhook_router

app = FastAPI(
    title="Commerce Agent API",
    description="AI 电商购物助手后端",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(webhook_router, prefix="/api/payment")


class ChatRequest(BaseModel):
    message: str
    history: list[dict] = []


class ChatResponse(BaseModel):
    reply: str


@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    """聊天端点"""
    try:
        print(f"[Chat] Received: {req.message[:80]}...")
        reply = await chat(req.message, req.history)
        return {"reply": reply}
    except Exception as e:
        traceback.print_exc()
        return {"reply": f"抱歉，处理您的请求时遇到了问题：{str(e)[:200]}"}


@app.get("/api/health")
async def health():
    return {"status": "ok", "products": vector_store.count()}


@app.get("/api/products/{product_id}")
async def get_product(product_id: str):
    product = hybrid_retriever.get_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@app.get("/api/products")
async def list_products(category: str = "", limit: int = 20):
    if category:
        results = hybrid_retriever.retrieve("", {"category": category})
        return results
    products = list(hybrid_retriever.products.values())[:limit]
    return products


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
