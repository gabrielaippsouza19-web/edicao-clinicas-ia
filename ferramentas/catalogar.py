"""Gera miniaturas numeradas e folhas de contato de uma pasta de assets.

Uso: catalogar.py <pasta_origem> <pasta_saida> <prefixo>
Cria <saida>/<prefixo>_folha_NN.jpg (grade 6x3) e <saida>/<prefixo>_indice.tsv.
Aceita HEIC do iPhone. As folhas podem mostrar pacientes: nao saem da pasta do cliente.
"""
import io
import os
import subprocess
import sys

import pillow_heif
from PIL import Image, ImageDraw, ImageFont, ImageOps

pillow_heif.register_heif_opener()

origem, saida, prefixo = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(saida, exist_ok=True)
IMG = {".jpg", ".jpeg", ".png", ".heic", ".webp"}
VID = {".mov", ".mp4", ".m4v", ".webm"}
W, H = 240, 300
fonte = ImageFont.load_default(18)

arquivos = sorted(f for f in os.listdir(origem) if os.path.splitext(f)[1].lower() in IMG | VID)
indice, miniaturas = [], []
for n, nome in enumerate(arquivos, 1):
    caminho = os.path.join(origem, nome)
    ext = os.path.splitext(nome)[1].lower()
    rotulo = f"{prefixo}{n:03d}" + (" VIDEO" if ext in VID else "")
    dur, estado = "", "ok"
    try:
        if ext in VID:
            dur = subprocess.run(
                ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", caminho],
                capture_output=True, text=True,
            ).stdout.strip()
            png = subprocess.run(
                ["ffmpeg", "-hide_banner", "-loglevel", "error", "-ss", "1", "-i", caminho, "-frames:v", "1",
                 "-f", "image2pipe", "-vcodec", "png", "-"],
                capture_output=True, check=True,
            ).stdout
            im = Image.open(io.BytesIO(png))
        else:
            im = ImageOps.exif_transpose(Image.open(caminho))
        im = ImageOps.pad(im.convert("RGB"), (W, H), color="gray")
        d = ImageDraw.Draw(im)
        d.rectangle([0, 0, 8 + 10 * len(rotulo), 24], fill="black")
        d.text((4, 2), rotulo, fill="yellow", font=fonte)
        miniaturas.append(im)
    except Exception as e:  # noqa: BLE001
        estado = f"ERRO {e}"
    indice.append(f"{prefixo}{n:03d}\t{nome}\t{estado}\t{dur}")

with open(os.path.join(saida, f"{prefixo}_indice.tsv"), "w", encoding="utf-8") as f:
    f.write("\n".join(indice))

for folha, inicio in enumerate(range(0, len(miniaturas), 18), 1):
    grade = Image.new("RGB", (W * 6, H * 3), "black")
    for k, im in enumerate(miniaturas[inicio:inicio + 18]):
        grade.paste(im, ((k % 6) * W, (k // 6) * H))
    grade.save(os.path.join(saida, f"{prefixo}_folha_{folha:02d}.jpg"), quality=85)
print(f"{prefixo}: {len(arquivos)} arquivos, {len(miniaturas)} miniaturas")
