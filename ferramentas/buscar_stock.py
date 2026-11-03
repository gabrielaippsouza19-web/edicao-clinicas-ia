"""Lista videos gratuitos do Mixkit para termos de busca (titulo + URL do mp4 de previa).

Uso: buscar_stock.py <saida.json> termo1 termo2 ...
So le as paginas publicas de busca; nao baixa os videos.
"""
import json
import re
import sys
import urllib.request

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126.0 Safari/537.36"
saida = sys.argv[1]
resultado = {}
for termo in sys.argv[2:]:
    url = f"https://mixkit.co/free-stock-video/{termo}/"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "ignore")
    except Exception as e:  # noqa: BLE001
        print(termo, "ERRO", e)
        continue
    itens = re.findall(
        r'<a[^>]+href="(/free-stock-video/[a-z0-9-]+-\d+/)"[^>]*>(.*?)</a>', html, flags=re.S
    )
    vistos = {}
    for href, conteudo in itens:
        m = re.search(r"-(\d+)/$", href)
        vid = m.group(1)
        titulo = re.sub(r"<[^>]+>", " ", conteudo)
        titulo = re.sub(r"\s+", " ", titulo).strip()
        if vid not in vistos or (titulo and not vistos[vid]["titulo"]):
            vistos[vid] = {"id": vid, "href": href, "titulo": titulo or href}
    resultado[termo] = list(vistos.values())
    print(termo, len(vistos))
    for v in list(vistos.values())[:40]:
        print("  ", v["id"], v["href"].split("/")[2])
json.dump(resultado, open(saida, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
