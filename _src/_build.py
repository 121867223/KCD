# -*- coding: utf-8 -*-
"""生成单文件移动端汇报：图片以注册表形式内嵌一次，配合懒加载绑定。"""
import base64, json, re
from pathlib import Path
from PIL import Image

ROOT = Path(r"F:/KCD/13/2方案/修改/设计汇报")
HERE = Path(__file__).parent
ASSETS = HERE / "_assets"
OUT = ROOT / "KCD展厅设计汇报.html"

GALLERY = [
 ("street_counter","路灯展示区 · 品牌台"),
 ("street_smart",  "智慧路灯 · 功能图解墙"),
 ("street_facets", "折面光棚 · 灯杆阵列"),
 ("street_plinth", "台地展区 · 石景与灯杆"),
 ("flood_brand",   "投光灯 · 品牌主墙"),
 ("flood_series",  "投光灯 · 六款系列墙"),
 ("flood_panel",   "斜切展墙 · 木质与灯带"),
 ("flood_orange",  "橙色折面展墙"),
 ("flood_cliff",   "岩壁造景 · 一线天光"),
 ("flood_rock",    "岩石展台 · 洗墙陈列"),
 ("flood_niche",   "混凝土壁龛 · 暗藏洗墙"),
 ("office_ceo",    "总裁办公室 · 主视角"),
 ("office_ceo_b",  "总裁办公室 · 日景"),
 ("office_vp",     "副总办公室"),
 ("office_mr",     "大会议室"),
 ("office_mr_s",   "小会议室"),
 ("office_wc",     "洗手间 · 镜面洗墙"),
 ("cover_hall",    "形象墙 · 接待入口"),
]

html = (HERE / "_template.html").read_text(encoding="utf-8")

# 1) 画廊
cells = [
    f'<button class="cell" data-k="{k}" data-cap="{cap}">'
    f'<img data-k="{k}" alt="{cap}"></button>'
    for k, cap in GALLERY
]
html = html.replace("{{gallery}}", "\n      ".join(cells))

# 2) 收集用到的键
keys = set(re.findall(r'data-k="([A-Za-z0-9_]+)"', html))
missing = [k for k in keys if not (ASSETS / f"{k}.jpg").exists()]
if missing:
    raise SystemExit("缺少图片: " + ", ".join(sorted(missing)))

# 3) 图片注册表
registry, dims = {}, {}
for k in sorted(keys):
    p = ASSETS / f"{k}.jpg"
    registry[k] = "data:image/jpeg;base64," + base64.b64encode(p.read_bytes()).decode()
    with Image.open(p) as im:
        dims[k] = im.size

# 4) 给 <img> 补宽高，避免懒加载导致版式跳动
def add_dims(m):
    tag = m.group(0)
    k = re.search(r'data-k="([A-Za-z0-9_]+)"', tag).group(1)
    w, h = dims[k]
    return tag[:-1] + f' width="{w}" height="{h}">'

html = re.sub(r'<img\b[^>]*data-k="[A-Za-z0-9_]+"[^>]*>', add_dims, html)

# 5) 注入注册表
html = html.replace("__IMGDATA__", json.dumps(registry, ensure_ascii=False))

left = re.findall(r"\{\{[A-Za-z0-9_]+\}\}|__IMGDATA__", html)
if left:
    raise SystemExit("未替换: " + str(left[:5]))

OUT.write_text(html, encoding="utf-8")
print("OK ->", OUT.name, round(OUT.stat().st_size / 1024 / 1024, 2), "MB",
      "| 图片", len(keys), "张")
