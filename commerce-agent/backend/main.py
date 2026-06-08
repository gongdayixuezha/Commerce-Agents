"""Commerce Agent - FastAPI Backend"""
import traceback
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, Response
from pydantic import BaseModel
from agent.agent import chat
from rag.vector_store import vector_store
from rag.retriever import hybrid_retriever
from payment.webhook import router as webhook_router
from admin import router as admin_router
from auth import init_db, create_user, verify_user

app = FastAPI(title="Commerce Agent API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(webhook_router, prefix="/api/payment")
app.include_router(admin_router)

init_db()

STATIC_DIR = Path(__file__).parent / "static"
INDEX_HTML = (STATIC_DIR / "index.html").read_text(encoding="utf-8")
ADMIN_HTML = (STATIC_DIR / "admin.html").read_text(encoding="utf-8")
LOGIN_HTML = (STATIC_DIR / "login.html").read_text(encoding="utf-8")

NO_CACHE = {"Cache-Control": "no-cache, no-store, must-revalidate", "Pragma": "no-cache", "Expires": "0"}


class ChatRequest(BaseModel):
    message: str
    history: list[dict] = []


@app.get("/", response_class=HTMLResponse)
async def login_page():
    return Response(content=LOGIN_HTML, media_type="text/html", headers=NO_CACHE)


@app.get("/chat", response_class=HTMLResponse)
async def chat_page():
    return Response(content=INDEX_HTML, media_type="text/html", headers=NO_CACHE)


@app.get("/admin", response_class=HTMLResponse)
async def admin():
    return Response(content=ADMIN_HTML, media_type="text/html", headers=NO_CACHE)


@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    try:
        reply = await chat(req.message, req.history)
        return {"reply": reply}
    except Exception as e:
        traceback.print_exc()
        return {"reply": f"Error: {str(e)[:200]}"}


@app.get("/api/health")
async def health():
    return {"status": "ok", "products": vector_store.count()}


@app.get("/api/products")
async def list_products(category: str = "", limit: int = 100):
    products = list(hybrid_retriever.products.values())
    if category:
        products = [p for p in products if p.get("category") == category]
    return products[:limit]


@app.get("/api/products/id/{product_id}")
async def get_product(product_id: str):
    product = hybrid_retriever.get_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


# ===== 用户认证 =====
class RegisterRequest(BaseModel):
    username: str
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str

@app.post("/api/register")
async def register(req: RegisterRequest):
    if len(req.username.strip()) < 2:
        raise HTTPException(400, "用户名至少2个字符")
    if len(req.password) < 4:
        raise HTTPException(400, "密码至少4个字符")
    try:
        user = create_user(req.username.strip(), req.password)
        return {"success": True, "user": user}
    except ValueError as e:
        raise HTTPException(409, str(e))

@app.post("/api/login")
async def api_login(req: LoginRequest):
    user = verify_user(req.username.strip(), req.password)
    if not user:
        raise HTTPException(401, "用户名或密码错误")
    return {"success": True, "user": user}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
