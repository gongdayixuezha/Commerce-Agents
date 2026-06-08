"""Agent Tools: 搜索、对比、支付"""
from langchain_core.tools import tool
from rag.retriever import hybrid_retriever
from langfuse.decorators import observe

@tool
@observe(name="search_products")
def search_products(query: str, category: str = "", min_price: float = 0, max_price: float = 0) -> str:
    """搜索商品。根据用户需求检索最相关的商品，每次返回4个。
    
    Args:
        query: 用户搜索查询（如"降噪耳机"、"适合跑步的运动鞋"）
        category: 可选品类过滤，可选值：电子产品、家居用品、服饰鞋包、食品饮料、图书文具、运动户外、美妆个护
        min_price: 最低价格（元），0 表示不限
        max_price: 最高价格（元），0 表示不限
    """
    filters = {}
    if category:
        filters["category"] = category
    if min_price > 0:
        filters["price_min"] = min_price
    if max_price > 0:
        filters["price_max"] = max_price

    results = hybrid_retriever.retrieve(query, filters)

    if not results:
        return "未找到匹配的商品。建议尝试更宽泛的搜索词或调整筛选条件。"

    lines = []
    for i, p in enumerate(results, 1):
        name = p.get("name", "未知商品")
        pid = p.get("id", "")
        price = p.get("price", 0)
        brand = p.get("brand", "未知品牌")
        rating = p.get("rating", 0)
        sales = p.get("sales_count", 0)
        stock = p.get("stock", 0)
        desc = p.get("description", "")[:80]
        attrs = p.get("attributes", {})
        color = attrs.get("颜色", [])
        specs = attrs.get("规格", "")

        line = f"{i}. [{pid}] **{name}**\n"
        line += f"   价格: ¥{price:.2f} | 品牌: {brand} | 评分: {rating}⭐\n"
        line += f"   销量: {sales} | 库存: {stock}"
        if color:
            line += f" | 颜色: {', '.join(color[:3])}"
        line += f"\n   {desc}..."
        lines.append(line)

    return "\n\n".join(lines)


@tool
@observe(name="compare_products")
def compare_products(product_ids: str) -> str:
    """对比多个商品，展示详细属性对比表格。

    Args:
        product_ids: 逗号分隔的商品 ID（如 "prod_0001,prod_0002,prod_0003"）
    """
    ids = [pid.strip() for pid in product_ids.split(",")]
    products = hybrid_retriever.get_by_ids(ids)

    valid = [p for p in products if p]
    if not valid:
        return "未找到指定商品，请检查商品 ID 是否正确。"

    # Markdown 对比表格
    header = "| 属性 |"
    sep = "|------|"
    for p in valid:
        header += f" {p['name'][:15]} |"
        sep += "------|"

    lines = [header, sep]
    attrs = [
        ("price", "价格", lambda v: f"¥{v:.2f}"),
        ("brand", "品牌", str),
        ("subcategory", "子类", str),
        ("rating", "评分", lambda v: f"{v}⭐"),
        ("sales_count", "销量", str),
        ("stock", "库存", str),
        ("description", "描述", lambda v: v[:50] + "..."),
    ]
    for key, label, fmt in attrs:
        row = f"| {label} |"
        for p in valid:
            val = p.get(key, "")
            row += f" {fmt(val)} |"
        lines.append(row)

    return "\n".join(lines)


@tool
@observe(name="create_payment")
def create_payment(product_id: str, quantity: int = 1) -> str:
    """为指定商品创建 Stripe 支付链接。

    Args:
        product_id: 商品 ID（如 prod_0001）
        quantity: 购买数量，默认 1
    """
    product = hybrid_retriever.get_by_id(product_id)
    if not product:
        return "未找到该商品，请确认商品 ID。"

    from payment.stripe_service import create_checkout_session
    url = create_checkout_session(product, quantity)

    return (
        f"已为 **{product['name']}** 创建支付链接（Stripe 测试模式）：\n\n"
        f"[点击支付]({url})\n\n"
        f"测试卡号: `4242 4242 4242 4242`\n"
        f"有效期: 任意未来日期（如 12/28）\n"
        f"CVC: 任意3位数字（如 123）\n\n"
        f"数量: {quantity} | 金额: ¥{product['price'] * quantity:.2f}"
    )


ALL_TOOLS = [search_products, compare_products, create_payment]
