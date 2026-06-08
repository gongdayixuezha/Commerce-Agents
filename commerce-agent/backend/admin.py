"""管理员 API：登录、统计、商品管理"""
import json, time, os
from pathlib import Path
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from rag.retriever import hybrid_retriever
from rag.vector_store import vector_store

router = APIRouter(prefix="/api/admin")
PRODUCTS_FILE = Path(__file__).parent / "data" / "products.json"
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

# ===== 登录 =====
class LoginRequest(BaseModel):
    password: str

@router.post("/login")
async def login(req: LoginRequest):
    if req.password == ADMIN_PASSWORD:
        return {"token": "admin_session_" + str(int(time.time())), "success": True}
    raise HTTPException(401, "密码错误")

# ===== 总览统计 =====
@router.get("/stats")
async def stats():
    products = hybrid_retriever.products
    total = len(products)
    categories = {}
    total_sales = 0
    total_value = 0
    for p in products.values():
        cat = p.get("category", "其他")
        categories[cat] = categories.get(cat, 0) + 1
        total_sales += p.get("sales_count", 0)
        total_value += p.get("price", 0) * p.get("sales_count", 0)

    return {
        "product_count": total,
        "vector_count": vector_store.count(),
        "categories": categories,
        "total_sales": total_sales,
        "total_value": round(total_value, 2),
        "avg_price": round(sum(p.get("price",0) for p in products.values()) / max(total, 1), 2),
        "avg_rating": round(sum(p.get("rating",0) for p in products.values()) / max(total, 1), 2),
    }

# ===== 商品管理 =====
class ProductUpdate(BaseModel):
    name: str | None = None
    price: float | None = None
    stock: int | None = None
    active: bool | None = None

@router.get("/products")
async def list_products(page: int = 1, size: int = 50, search: str = ""):
    products = list(hybrid_retriever.products.values())
    if search:
        products = [p for p in products if search.lower() in p.get("name","").lower()]
    total = len(products)
    start = (page - 1) * size
    return {"items": products[start:start+size], "total": total, "page": page}

@router.put("/products/{product_id}")
async def update_product(product_id: str, update: ProductUpdate):
    if not PRODUCTS_FILE.exists():
        raise HTTPException(404, "商品数据文件不存在")
    with open(PRODUCTS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    for p in data:
        if p["id"] == product_id:
            if update.name is not None: p["name"] = update.name
            if update.price is not None: p["price"] = update.price
            if update.stock is not None: p["stock"] = update.stock
            if "active" not in p: p["active"] = True
            if update.active is not None: p["active"] = update.active
            with open(PRODUCTS_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            hybrid_retriever.reload()
            return {"success": True}
    raise HTTPException(404, "商品不存在")

@router.post("/products/{product_id}/toggle")
async def toggle_product(product_id: str):
    if not PRODUCTS_FILE.exists():
        raise HTTPException(404, "商品数据文件不存在")
    with open(PRODUCTS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    for p in data:
        if p["id"] == product_id:
            p["active"] = not p.get("active", True)
            with open(PRODUCTS_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            hybrid_retriever.reload()
            return {"active": p["active"], "success": True}
    raise HTTPException(404, "商品不存在")

@router.delete("/products/{product_id}")
async def delete_product(product_id: str):
    if not PRODUCTS_FILE.exists():
        raise HTTPException(404, "商品数据文件不存在")
    with open(PRODUCTS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    new_data = [p for p in data if p["id"] != product_id]
    if len(new_data) == len(data):
        raise HTTPException(404, "商品不存在")
    with open(PRODUCTS_FILE, "w", encoding="utf-8") as f:
        json.dump(new_data, f, ensure_ascii=False, indent=2)
    hybrid_retriever.reload()
    return {"success": True}




# ===== ???? =====
@router.get("/stats/charts")
async def charts_data():
    from collections import defaultdict
    import json as _json
    from pathlib import Path
    products_file = Path(__file__).parent / "data" / "products.json"
    if not products_file.exists():
        return {"categories": [], "price_ranges": [], "top_brands": []}
    with open(products_file, "r", encoding="utf-8") as f:
        products = _json.load(f)

    cats = defaultdict(lambda: {"count": 0, "total_price": 0, "total_rating": 0, "total_sales": 0, "total_stock": 0})
    for p in products:
        c = p.get("category", "其他")
        cats[c]["count"] += 1
        cats[c]["total_price"] += p.get("price", 0)
        cats[c]["total_rating"] += p.get("rating", 0)
        cats[c]["total_sales"] += p.get("sales_count", 0)
        cats[c]["total_stock"] += p.get("stock", 0)

    categories = []
    for c, v in sorted(cats.items()):
        categories.append({
            "name": c, "count": v["count"],
            "avg_price": round(v["total_price"] / v["count"], 2),
            "avg_rating": round(v["total_rating"] / v["count"], 2),
            "total_sales": v["total_sales"], "total_stock": v["total_stock"],
        })

    ranges = [("0-100", 0, 100), ("100-300", 100, 300), ("300-500", 300, 500),
              ("500-1000", 500, 1000), ("1000-3000", 1000, 3000), ("3000+", 3000, 1e9)]
    price_ranges = []
    for label, lo, hi in ranges:
        count = sum(1 for p in products if lo <= p.get("price", 0) < hi)
        price_ranges.append({"label": label, "count": count})

    brands = defaultdict(int)
    for p in products:
        brands[p.get("brand", "未知")] += 1
    top_brands = sorted(brands.items(), key=lambda x: -x[1])[:10]

    return {"categories": categories, "price_ranges": price_ranges,
            "top_brands": [{"name": b, "count": c} for b, c in top_brands]}
# ===== Langfuse Observability =====
@router.get('/observe')
async def observe_data():
    from observability.langfuse_trace import get_langfuse
    langfuse = get_langfuse()
    if not langfuse:
        return {'available': False, 'message': 'Langfuse not configured'}

    try:
        resp = langfuse.api.trace.list(page=1, limit=20)
        traces = []
        total_latency = 0
        for t in resp.data:
            d = t.model_dump() if hasattr(t, 'model_dump') else {}
            traces.append({
                'id': t.id[:12] if t.id else '',
                'name': t.name or 'chat',
                'timestamp': str(d.get('timestamp', ''))[:19],
                'latency': round(t.latency or 0, 2),
            })
            total_latency += t.latency or 0

        return {
            'available': True,
            'trace_count': len(resp.data),
            'avg_latency': round(total_latency / max(len(resp.data), 1), 2),
            'traces': traces,
        }
    except Exception as e:
        return {'available': False, 'message': str(e)[:200]}
