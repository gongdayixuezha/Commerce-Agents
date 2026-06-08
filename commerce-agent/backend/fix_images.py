import re
path = r"C:\Users\14188\Documents\Codex\2026-06-08\github\Commerce-Agents\commerce-agent\backend\static\index.html"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

css = """
.cat-img{width:100%;height:180px;display:flex;align-items:center;justify-content:center;font-size:56px;color:#fff}
.cat-Electronics{background:linear-gradient(135deg,#3b82f6,#1d4ed8)}
.cat-Home{background:linear-gradient(135deg,#f59e0b,#d97706)}
.cat-Fashion{background:linear-gradient(135deg,#ec4899,#be185d)}
.cat-Food{background:linear-gradient(135deg,#10b981,#059669)}
.cat-Books{background:linear-gradient(135deg,#8b5cf6,#6d28d9)}
.cat-Sports{background:linear-gradient(135deg,#06b6d4,#0891b2)}
.cat-Beauty{background:linear-gradient(135deg,#f43f5e,#e11d48)}
.product-card .cat-img{font-size:48px}
.product-modal .cat-img{width:100%;height:240px;font-size:72px;border-radius:8px;margin-bottom:12px}
"""
content = content.replace(".product-card img{", css + "\n.product-card img{")

emoji_js = "var catEmoji={'Electronics':'\\ud83d\\udcf1','Home':'\\ud83c\\udfe0','Fashion':'\\ud83d\\udc57','Food':'\\ud83c\\udf5c','Books':'\\ud83d\\udcda','Sports':'\\u26bd','Beauty':'\\ud83d\\udc84'};\n"
content = content.replace("var activeCat", emoji_js + "var activeCat")

# Also add a JS function to map Chinese category names to English CSS classes
cat_map_js = """function catClass(cat){var m={};
m['\u7535\u5b50\u4ea7\u54c1']='Electronics';
m['\u5bb6\u5c45\u7528\u54c1']='Home';
m['\u670d\u9970\u978b\u5305']='Fashion';
m['\u98df\u54c1\u996e\u6599']='Food';
m['\u56fe\u4e66\u6587\u5177']='Books';
m['\u8fd0\u52a8\u6237\u5916']='Sports';
m['\u7f8e\u5986\u4e2a\u62a4']='Beauty';
return m[cat]||'Electronics';}
"""
content = content.replace("var activeCat", cat_map_js + "\nvar activeCat")

# Replace img in renderProducts
old1 = '<img src="${p.image_url}" alt="${escHtml(p.name)}" loading="lazy">'
new1 = '<div class="cat-img cat-${catClass(p.category)}">${catEmoji[catClass(p.category)]||"\\ud83d\\udce6"}</div>'
content = content.replace(old1, new1)

# Replace img in showProduct
old2 = '<img src="${p.image_url}" alt="${escHtml(p.name)}">'
new2 = '<div class="cat-img cat-${catClass(p.category)}">${catEmoji[catClass(p.category)]||"\\ud83d\\udce6"}</div>'
content = content.replace(old2, new2)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

script = content.split("<script>")[1].split("</script>")[0]
o = script.count("{")
c = script.count("}")
print(f"Braces: {o}={c} {'OK' if o==c else 'FAIL'} | {len(content)} bytes")
