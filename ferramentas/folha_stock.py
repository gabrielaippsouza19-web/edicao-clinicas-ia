"""Baixa as miniaturas de candidatos do Pexels e monta folhas de contato com o ID.

Uso: folha_stock.py <candidatos.json> <pasta_saida>
Ordem por categoria. Grade 10x3 por folha. Imprime qual categoria esta em cada folha.
"""
import concurrent.futures as cf
import json
import os
import sys
import urllib.request

from PIL import Image, ImageDraw, ImageFont

candidatos = json.load(open(sys.argv[1], encoding="utf-8"))
saida = sys.argv[2]
os.makedirs(saida, exist_ok=True)
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0"
fonte = ImageFont.load_default(18)
W, H = 180, 320


def baixar(item):
    vid = item.split("/")[0]
    destino = os.path.join(saida, f"{vid}.jpg")
    if not os.path.exists(destino):
        url = f"https://images.pexels.com/videos/{item}?auto=compress&cs=tinysrgb&w=320"
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=30) as r, open(destino, "wb") as f:
            f.write(r.read())
    return vid


lista = [(cat, it) for cat, itens in candidatos.items() for it in itens]
with cf.ThreadPoolExecutor(8) as ex:
    list(ex.map(lambda x: baixar(x[1]), lista))

POR_FOLHA = 30
for f, ini in enumerate(range(0, len(lista), POR_FOLHA), 1):
    grupo = lista[ini:ini + POR_FOLHA]
    folha = Image.new("RGB", (W * 10, H * 3), "black")
    for k, (cat, it) in enumerate(grupo):
        vid = it.split("/")[0]
        try:
            im = Image.open(os.path.join(saida, f"{vid}.jpg")).convert("RGB")
        except Exception:  # noqa: BLE001
            continue
        im.thumbnail((W, H))
        x, y = (k % 10) * W, (k // 10) * H
        folha.paste(im, (x + (W - im.width) // 2, y + (H - im.height) // 2))
        d = ImageDraw.Draw(folha)
        d.rectangle([x, y, x + W, y + 22], fill="black")
        d.text((x + 3, y + 1), vid, fill="yellow", font=fonte)
    caminho = os.path.join(saida, f"folha_{f:02d}.jpg")
    folha.save(caminho, quality=85)
    cats = []
    for c, _ in grupo:
        if c not in cats:
            cats.append(c)
    print(f"folha_{f:02d}: {', '.join(cats)}")
