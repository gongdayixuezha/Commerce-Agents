"""
商品数据生成器
使用 DeepSeek API 批量生成 300-500 个模拟商品，覆盖 7 大品类
"""
import json
import os
import time
import random
import re
from pathlib import Path
from openai import OpenAI
from config import DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL

client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL, timeout=120.0)

CATEGORIES = [
    ("电子产品", 90, 50, 8000),
    ("家居用品", 70, 20, 3000),
    ("服饰鞋包", 70, 30, 2000),
    ("食品饮料", 60, 5, 500),
    ("图书文具", 50, 10, 200),
    ("运动户外", 50, 50, 5000),
    ("美妆个护", 50, 20, 1000),
]

PROMPT_TEMPLATE = """你是一个电商商品数据生成器。请生成 {count} 个"{category}"品类的模拟商品。

品类子类别建议: {subcategories}

价格区间: ¥{min_price} - ¥{max_price}
品牌要求: 使用多样化的品牌名（不同商品用不同品牌）

每个商品严格按以下 JSON 格式输出，只输出一个 JSON 数组，不要任何其他文字:
[
  {{
    "name": "商品名称",
    "category": "{category}",
    "subcategory": "子类别",
    "price": 299.00,
    "brand": "品牌名",
    "attributes": {{"颜色": ["黑色"], "规格": "规格参数", "特点": "核心卖点"}},
    "description": "50-150字的详细商品描述，包含产品特点、使用场景、优势等，用于语义检索。描述要自然流畅，贴近真实电商风格。",
    "stock": 100,
    "rating": 4.5,
    "sales_count": 500
  }}
]

要求:
- 商品名称多样化且有吸引力，贴近真实电商
- description 字数 50-150 字，内容充实
- 价格在指定区间内合理分布
- 不同品类使用对应的真实品牌名
- 子类别要细分"""

SUBCATEGORIES = {
    "电子产品": "智能手机、笔记本电脑、平板电脑、耳机、智能手表、相机、音箱、移动电源、数据线、键盘鼠标",
    "家居用品": "床上用品、厨房用具、收纳用品、灯具、家具、清洁工具、浴室用品、装饰品、窗帘、地毯",
    "服饰鞋包": "T恤、连衣裙、牛仔裤、外套、运动鞋、休闲鞋、双肩包、手提包、帽子、围巾",
    "食品饮料": "零食、坚果、茶叶、咖啡、方便食品、调味品、饮料、冲饮品、糕点、糖果",
    "图书文具": "小说、教材、笔记本、钢笔、马克笔、便签、文件夹、绘画工具、字帖、贴纸",
    "运动户外": "跑步鞋、瑜伽垫、篮球、羽毛球拍、帐篷、睡袋、骑行装备、泳镜、运动服、护具",
    "美妆个护": "洗面奶、面膜、口红、粉底液、眼影、洗发水、沐浴露、护手霜、防晒霜、香水",
}


def generate_batch(category: str, count: int, min_price: int, max_price: int) -> list[dict]:
    """调用 DeepSeek API 生成一批商品"""
    subs = SUBCATEGORIES.get(category, "")
    prompt = PROMPT_TEMPLATE.format(
        count=count, category=category,
        subcategories=subs, min_price=min_price, max_price=max_price
    )

    for attempt in range(3):
        try:
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.8,
                max_tokens=4096,
            )
            content = response.choices[0].message.content.strip()

            # 清理 markdown 代码块
            content = re.sub(r'^```(?:json)?\s*', '', content)
            content = re.sub(r'\s*```$', '', content)

            products = json.loads(content)
            if isinstance(products, list) and len(products) > 0:
                return products
        except json.JSONDecodeError as e:
            print(f"  JSON parse error (attempt {attempt + 1}): {e}")
            time.sleep(2)
        except Exception as e:
            print(f"  API error (attempt {attempt + 1}): {e}")
            time.sleep(3)

    print(f"  Failed to generate batch after 3 attempts")
    return []


def main():
    random.seed(42)
    all_products = []
    product_index = 1
    seen_names = set()

    print("=" * 50)
    print("Commerce Agent - 商品数据生成器")
    print("=" * 50)

    total_target = sum(c[1] for c in CATEGORIES)
    print(f"目标: {total_target} 个商品，覆盖 {len(CATEGORIES)} 个品类\n")

    for category, total, min_price, max_price in CATEGORIES:
        print(f"[{category}] 目标 {total} 个，价格 ¥{min_price}-¥{max_price}")

        generated = 0
        while generated < total:
            batch_size = min(30, total - generated)
            print(f"  生成 {batch_size} 个...", end=" ")

            batch = generate_batch(category, batch_size, min_price, max_price)

            for product in batch:
                name = product.get("name", "")
                # 去重
                if name and name not in seen_names:
                    seen_names.add(name)
                    product["id"] = f"prod_{product_index:04d}"
                    product["image_url"] = f"https://picsum.photos/seed/prod_{product_index:04d}/400/400"
                    product["price"] = round(max(min_price, min(max_price, float(product.get("price", 100)))), 2)
                    product["rating"] = round(random.uniform(3.0, 5.0), 1)
                    product["stock"] = random.randint(10, 500)
                    product["sales_count"] = random.randint(0, 10000)
                    all_products.append(product)
                    product_index += 1

            generated = sum(1 for p in all_products if p.get("category") == category)
            print(f"累计 {generated}/{total}")

            time.sleep(1.5)  # API rate limit

    # 保存到 products.json
    output_path = Path(__file__).parent / "products.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_products, f, ensure_ascii=False, indent=2)

    print(f"\n{'=' * 50}")
    print(f"已生成 {len(all_products)} 个商品")
    print(f"保存至: {output_path}")

    # 统计
    from collections import Counter
    cat_count = Counter(p["category"] for p in all_products)
    for cat, cnt in cat_count.most_common():
        avg_price = sum(p["price"] for p in all_products if p["category"] == cat) / cnt
        print(f"  {cat}: {cnt} 个, 均价 ¥{avg_price:.2f}")

    print(f"{'=' * 50}")


if __name__ == "__main__":
    main()
