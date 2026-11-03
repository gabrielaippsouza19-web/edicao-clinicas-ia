"""Monta uma folha com quadros do apresentador para escolher a foto da capa.

Uso: folha_rostos.py <video> <saida.jpg> <colunas> t1 t2 t3 ...
Cada quadro e recortado na regiao do rosto e do tronco e leva o tempo escrito.
"""
import io
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

video, saida, colunas = sys.argv[1], sys.argv[2], int(sys.argv[3])
tempos = sys.argv[4:]
W, H = 250, 340
fonte = ImageFont.load_default(20)
linhas = (len(tempos) + colunas - 1) // colunas
folha = Image.new("RGB", (W * colunas, H * linhas), "black")
for k, t in enumerate(tempos):
    png = subprocess.run(
        ["ffmpeg", "-hide_banner", "-loglevel", "error", "-ss", t, "-i", video, "-frames:v", "1",
         "-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
                "crop=1000:1360:40:300,scale=250:340",
         "-f", "image2pipe", "-vcodec", "png", "-"],
        capture_output=True,
    ).stdout
    im = Image.open(io.BytesIO(png)).convert("RGB")
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 70, 24], fill="black")
    d.text((3, 1), t, fill="yellow", font=fonte)
    folha.paste(im, ((k % colunas) * W, (k // colunas) * H))
folha.save(saida, quality=88)
print("ok", saida)
