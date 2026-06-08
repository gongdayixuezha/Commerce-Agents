"""商品数据生成器 - 增量保存版"""
import json, os, random, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from openai import OpenAI
from config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL

client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL, timeout=90.0)
OUTPUT = Path(__file__).parent / "products.json"

# 目标约 350 个商品（在 300-500 范围内）
CATEGORIES = [
    ("电子产品", 70, 50, 8000),
    ("家居用品", 55, 20, 3000),
    ("服饰鞋包", 55, 30, 2000),
    ("食品饮料", 50, 5, 500),
    ("图书文具", 40, 10, 200),
    ("运动户外", 40, 50, 5000),
    ("美妆个护", 40, 20, 1000),
]

SUBS = {
    "电子产品": "智能手机,笔记本,平板,耳机,智能手表,相机,音箱,移动电源,键盘鼠标",
    "家居用品": "床上用品,厨房用具,收纳,灯具,家具,清洁工具,浴室用品,装饰",
    "服饰鞋包": "T恤,连衣裙,牛仔裤,外套,运动鞋,双肩包,手提包,帽子,围巾",
    "食品饮料": "零食,坚果,茶叶,咖啡,方便食品,调味品,饮料,糕点,糖果",
    "图书文具": "小说,教材,笔记本,钢笔,马克笔,绘画工具,字帖,贴纸",
    "运动户外": "跑步鞋,瑜伽垫,篮球,羽毛球拍,帐篷,骑行装备,泳镜,运动服",
    "美妆个护": "洗面奶,面膜,口红,粉底液,洗发水,沐浴露,护手霜,防晒霜,香水",
}


def generate_batch(category, count, min_p, max_p):
    prompt = (
        f'生成{count}个"{category}"品类的模拟电商商品。'
        f'子类别参考: {SUBS[category]}。'
        f'价格区间: 元{min_p}-{max_p}。'
        f'品牌多样化，描述50-100字。'
        f'\n直接输出JSON数组:\n'
        f'[{{"name":"商品名","category":"{category}","subcategory":"子类","price":99,'
        f'"brand":"品牌","attributes":{{"颜色":["黑"],"规格":"","特点":""}},'
        f'"description":"50-100字商品描述"}}]'
    )
    for attempt in range(3):
        try:
            r = client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.9,
                max_tokens=2048,
            )
            text = r.choices[0].message.content.strip()
            text = re.sub(r'^```(?:json)?\s*\n?', '', text)
            text = re.sub(r'\n?\s*```$', '', text)
            data = json.loads(text)
            if isinstance(data, list) and len(data) > 0:
                return data
        except Exception as e:
            print(f"  retry{attempt+1}: {str(e)[:80]}")
    return []


def save(products):
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(products, f, ensure_ascii=False, indent=2)


def main():
    random.seed(42)
    # Load existing if any
    if OUTPUT.exists():
        with open(OUTPUT, "r", encoding="utf-8") as f:
            products = json.load(f)
        seen = {p["name"] for p in products}
        idx = len(products) + 1
        print(f"Resuming: {len(products)} products loaded")
    else:
        products, seen, idx = [], set(), 1

    target = sum(c[1] for c in CATEGORIES)
    print(f"Target: {target} products")

    for cat, total, lo, hi in CATEGORIES:
        current = sum(1 for p in products if p["category"] == cat)
        print(f"\n[{cat}] need {total}, have {current}")
        while current < total:
            n = min(10, total - current)
            print(f"  generating {n}...", end=" ", flush=True)
            batch = generate_batch(cat, n, lo, hi)
            added = 0
            for p in batch:
                nm = p.get("name", "")
                if nm and nm not in seen:
                    seen.add(nm)
                    p["id"] = f"prod_{idx:04d}"
                    p["image_url"] = f"https://picsum.photos/seed/prod_{idx:04d}/400/400"
                    p["price"] = round(max(lo, min(hi, float(p.get("price", 100)))), 2)
                    p["rating"] = round(random.uniform(3.0, 5.0), 1)
                    p["stock"] = random.randint(10, 500)
                    p["sales_count"] = random.randint(0, 10000)
                    products.append(p)
                    idx += 1
                    added += 1
            current = sum(1 for p in products if p["category"] == cat)
            save(products)
            print(f"+{added} total={len(products)} (cat:{current}/{total})")

    save(products)
    print(f"\n{'='*40}")
    print(f"DONE: {len(products)} products -> {OUTPUT}")
    from collections import Counter
    for c, n in Counter(p["category"] for p in products).most_common():
        avg = sum(p["price"] for p in products if p["category"] == c) / n
        print(f"  {c}: {n} 均价元{avg:.0f}")
    print(f"{'='*40}")


if __name__ == "__main__":
    main()

