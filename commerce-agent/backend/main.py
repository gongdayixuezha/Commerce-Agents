"""Commerce Agent - FastAPI Backend（含前端页面）"""
import traceback
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from agent.agent import chat
from rag.vector_store import vector_store
from rag.retriever import hybrid_retriever
from payment.webhook import router as webhook_router
from admin import router as admin_router

app = FastAPI(title="Commerce Agent API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

app.include_router(webhook_router, prefix="/api/payment")
app.include_router(admin_router)


@app.get("/admin", response_class=HTMLResponse)
async def admin():
    return Response(content=ADMIN_HTML, media_type="text/html", headers={"Cache-Control": "no-cache, no-store, must-revalidate"})
app.include_router(admin_router)


@app.get("/admin", response_class=HTMLResponse)
async def admin():
    return Response(content=ADMIN_HTML, media_type="text/html", headers={"Cache-Control": "no-cache, no-store, must-revalidate"})

# 读取前端 HTML
STATIC_DIR = Path(__file__).parent / "static"
INDEX_HTML = (STATIC_DIR / "index.html").read_text(encoding="utf-8")
ADMIN_HTML = (STATIC_DIR / "admin.html").read_text(encoding="utf-8")


class ChatRequest(BaseModel):
    message: str
    history: list[dict] = []


@app.get("/", response_class=HTMLResponse)
async def index():
    """前端聊天页面"""
    from fastapi.responses import Response
    return Response(
        content=INDEX_HTML,
        media_type="text/html",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
        }
    )


@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    try:
        reply = await chat(req.message, req.history)
        return {"reply": reply}
    except Exception as e:
        traceback.print_exc()
        return {"reply": f"抱歉，处理出错：{str(e)[:200]}"}


@app.get("/api/health")

@app.get("/api/products")
async def list_products(category: str = "", limit: int = 100):
    """列出所有商品，支持按品类过滤"""
    products = list(hybrid_retriever.products.values())
    if category:
        products = [p for p in products if p.get("category") == category]
    return products[:limit]
async def health():
    return {"status": "ok", "products": vector_store.count()}


@app.get("/api/products/id/{product_id}")
async def get_product(product_id: str):
    product = hybrid_retriever.get_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
