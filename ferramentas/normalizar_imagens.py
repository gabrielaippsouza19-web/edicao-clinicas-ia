"""Converte imagens (inclusive HEIC do iPhone) para JPG com orientacao corrigida.

Uso: normalizar_imagens.py <pasta_origem> <pasta_destino> [lado_max]
Mantem o nome-base do arquivo. Nao altera a origem.
"""
import os
import sys

import pillow_heif
from PIL import Image, ImageOps

pillow_heif.register_heif_opener()

origem, destino = sys.argv[1], sys.argv[2]
lado_max = int(sys.argv[3]) if len(sys.argv) > 3 else 2160
os.makedirs(destino, exist_ok=True)

ok = falhas = 0
for nome in sorted(os.listdir(origem)):
    base, ext = os.path.splitext(nome)
    if ext.lower() not in {".jpg", ".jpeg", ".png", ".heic"}:
        continue
    saida = os.path.join(destino, base + ".jpg")
    if os.path.exists(saida):
        saida = os.path.join(destino, f"{base}_{ext.lower().strip('.')}.jpg")
    try:
        with Image.open(os.path.join(origem, nome)) as im:
            im = ImageOps.exif_transpose(im).convert("RGB")
            im.thumbnail((lado_max, lado_max))
            im.save(saida, "JPEG", quality=92)
        ok += 1
    except Exception as e:  # noqa: BLE001
        falhas += 1
        print(f"FALHA {nome}: {e}")
print(f"{origem}: {ok} convertidas, {falhas} falhas")
