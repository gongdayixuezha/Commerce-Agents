"""Commerce Agent - FastAPI Backend"""
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


class ProductResponse(BaseModel):
    id: str
    name: str
    price: float
    # ... other fields returned as-is


@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    """聊天端点：接收用户消息，返回 Agent 回复"""
    reply = await chat(req.message, req.history)
    return ChatResponse(reply=reply)


@app.get("/api/health")
async def health():
    """健康检查"""
    return {
        "status": "ok",
        "products": vector_store.count(),
    }


@app.get("/api/products/{product_id}")
async def get_product(product_id: str):
    """查询单个商品详情"""
    product = hybrid_retriever.get_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@app.get("/api/products")
async def list_products(category: str = "", limit: int = 20):
    """列出商品"""
    if category:
        results = hybrid_retriever.retrieve("", {"category": category})
    else:
        # 返回前 N 个商品
        products = list(hybrid_retriever.products.values())[:limit]
        return products
    return results


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
