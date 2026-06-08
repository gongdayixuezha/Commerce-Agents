path = r"C:\Users\14188\Documents\Codex\2026-06-08\github\Commerce-Agents\commerce-agent\backend\static\index.html"
with open(path, "r", encoding="utf-8") as f:
    c = f.read()

# 1. Update cat-img CSS for better look with text overlay
old_css = ".cat-img{width:100%;height:180px;display:flex;align-items:center;justify-content:center;font-size:56px;color:#fff}"
new_css = ".cat-img{width:100%;height:180px;display:flex;flex-direction:column;align-items:center;justify-content:center;color:#fff;position:relative;overflow:hidden}.cat-img .emoji{font-size:42px;margin-bottom:4px}.cat-img .pname{font-size:12px;font-weight:600;text-align:center;padding:0 8px;line-height:1.3;max-height:34px;overflow:hidden;text-shadow:0 1px 2px rgba(0,0,0,.3)}.cat-img .pprice{font-size:16px;font-weight:700;margin-top:4px;text-shadow:0 1px 2px rgba(0,0,0,.3)}"
c = c.replace(old_css, new_css)

# 2. Update product-card cat-img size
c = c.replace(".product-card .cat-img{font-size:48px}", ".product-card .cat-img{height:160px}.product-card .cat-img .emoji{font-size:36px}.product-card .cat-img .pname{font-size:11px}")

# 3. Update modal cat-img
c = c.replace(".product-modal .cat-img{width:100%;height:240px;font-size:72px;border-radius:8px;margin-bottom:12px}", ".product-modal .cat-img{width:100%;height:240px;border-radius:8px;margin-bottom:12px}.product-modal .cat-img .emoji{font-size:64px}")

# 4. Update JS - renderProducts to show name+price in image block
old_card_img = '<div class="cat-img cat-${catClass(p.category)}">${catEmoji[catClass(p.category)]||"\\ud83d\\udce6"}</div>'
new_card_img = '<div class="cat-img cat-${catClass(p.category)}"><span class="emoji">${catEmoji[catClass(p.category)]||"\\ud83d\\udce6"}</span><span class="pname">${escHtml(p.name)}</span><span class="pprice">\\uffe5${p.price.toFixed(0)}</span></div>'
c = c.replace(old_card_img, new_card_img)

# 5. Update modal image
old_modal_img = '<div class="cat-img cat-${catClass(p.category)}">${catEmoji[catClass(p.category)]||"\\ud83d\\udce6"}</div>'
new_modal_img = '<div class="cat-img cat-${catClass(p.category)}"><span class="emoji">${catEmoji[catClass(p.category)]||"\\ud83d\\udce6"}</span><span class="pname">${escHtml(p.name)}</span></div>'
c = c.replace(old_modal_img, new_modal_img)

with open(path, "w", encoding="utf-8") as f:
    f.write(c)

script = c.split("<script>")[1].split("</script>")[0]
o = script.count("{")
cl = script.count("}")
print(f"Braces: {o}={cl} {'OK' if o==cl else 'MISMATCH'} | {len(c)} bytes")
