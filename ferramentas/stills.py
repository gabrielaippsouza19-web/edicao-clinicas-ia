"""Renderiza quadros de checagem de uma composicao e monta uma folha.

Uso: stills.py <pasta_projeto> <composicao> <saida.jpg> <colunas> <t1,t2,...> [--escala 0.3]
Tempos em segundos da EDICAO. Olhe a folha antes de renderizar o video inteiro.
"""
import argparse
import math
import shutil
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ap = argparse.ArgumentParser()
ap.add_argument("projeto")
ap.add_argument("composicao")
ap.add_argument("saida")
ap.add_argument("colunas", type=int)
ap.add_argument("tempos")
ap.add_argument("--escala", type=float, default=0.3)
args = ap.parse_args()

npx = shutil.which("npx")
tempos = [float(t) for t in args.tempos.split(",")]
quadros = []
fonte = ImageFont.load_default(22)
with tempfile.TemporaryDirectory() as pasta:
    for t in tempos:
        f = round(t * 30)
        arq = Path(pasta) / f"q{f}.jpg"
        r = subprocess.run(
            [npx, "remotion", "still", args.composicao, str(arq), f"--frame={f}",
             f"--scale={args.escala}", "--log=error"],
            cwd=args.projeto, capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        if r.returncode != 0:
            raise SystemExit(f"erro no quadro {t}s:\n{r.stdout}\n{r.stderr}")
        im = Image.open(arq).convert("RGB")
        im.load()
        d = ImageDraw.Draw(im)
        d.rectangle([0, 0, 92, 28], fill="black")
        d.text((4, 2), f"{t:.2f}s", fill="yellow", font=fonte)
        quadros.append(im)

largura, altura = quadros[0].size
linhas = math.ceil(len(quadros) / args.colunas)
folha = Image.new("RGB", (largura * args.colunas, altura * linhas), "black")
for k, im in enumerate(quadros):
    folha.paste(im, ((k % args.colunas) * largura, (k // args.colunas) * altura))
folha.save(args.saida, quality=88)
print("folha:", args.saida)
