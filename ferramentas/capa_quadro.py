"""Extrai um quadro do bruto para capa.

Uso: capa_quadro.py <video> <tempo_s> <saida.png> [--pele]
--pele aplica a mesma correcao da edicao. Use se o video tambem foi tratado com --pele.
"""
import argparse
import io
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent))
from comum import corrige_pele, filtro_video  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("video")
ap.add_argument("tempo")
ap.add_argument("saida")
ap.add_argument("--pele", action="store_true")
args = ap.parse_args()

png = subprocess.run(
    ["ffmpeg", "-hide_banner", "-loglevel", "error", "-ss", args.tempo, "-i", args.video, "-frames:v", "1",
     "-vf", filtro_video(args.video).replace(",fps=30", ""), "-f", "image2pipe", "-vcodec", "png", "-"],
    capture_output=True, check=True,
).stdout
im = Image.open(io.BytesIO(png)).convert("RGB")
if args.pele:
    rgb = np.asarray(im, dtype=np.float32) / 255.0
    im = Image.fromarray((corrige_pele(rgb) * 255).astype(np.uint8))
final = im.filter(ImageFilter.UnsharpMask(radius=2, percent=70, threshold=2))
final.save(args.saida)
print("quadro salvo:", args.saida, final.size)
