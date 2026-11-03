"""Baixa videos do Pexels (CDN publico) e gera proxies 1080x1920 H.264 30 fps sem audio.

Uso: baixar_stock.py <lista.txt> <pasta_originais> <pasta_proxy> [max_segundos]
lista.txt: um caminho por linha, relativo a https://videos.pexels.com/video-files/
"""
import concurrent.futures as cf
import os
import subprocess
import sys
import urllib.request

lista, orig, prox = sys.argv[1], sys.argv[2], sys.argv[3]
max_s = sys.argv[4] if len(sys.argv) > 4 else "14"
os.makedirs(orig, exist_ok=True)
os.makedirs(prox, exist_ok=True)
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0"


def baixar(rel):
    vid = rel.split("/")[0]
    destino = os.path.join(orig, f"{vid}.mp4")
    if os.path.exists(destino) and os.path.getsize(destino) > 0:
        return vid, "ja existe"
    req = urllib.request.Request(
        "https://videos.pexels.com/video-files/" + rel, headers={"User-Agent": UA}
    )
    with urllib.request.urlopen(req, timeout=300) as r, open(destino, "wb") as f:
        while True:
            bloco = r.read(1 << 20)
            if not bloco:
                break
            f.write(bloco)
    return vid, f"{os.path.getsize(destino) / 1e6:.1f} MB"


def proxy(vid):
    entrada = os.path.join(orig, f"{vid}.mp4")
    saida = os.path.join(prox, f"{vid}.mp4")
    if os.path.exists(saida):
        return
    subprocess.run(
        ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", entrada, "-t", max_s,
         "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=30",
         "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p",
         "-g", "15", "-an", "-movflags", "+faststart", saida],
        check=True,
    )


itens = [l.strip() for l in open(lista, encoding="utf-8") if l.strip()]
with cf.ThreadPoolExecutor(6) as ex:
    for vid, info in ex.map(baixar, itens):
        print(vid, info, flush=True)
with cf.ThreadPoolExecutor(3) as ex:
    list(ex.map(proxy, [i.split("/")[0] for i in itens]))
print("proxies prontos")
