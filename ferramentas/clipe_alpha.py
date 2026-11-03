"""Gera o trecho do apresentador com transparencia, para a palavra atras da cabeca.

Uso: clipe_alpha.py <pasta_camadas> <ini_s> <fim_s> <saida.webm>
Tempos do bruto. O trecho nao pode atravessar um corte (o motor valida isso).
"""
import os
import subprocess
import sys

pasta, ini, fim, saida = sys.argv[1:5]
dur = f"{float(fim) - float(ini):.3f}"
subprocess.run(
    ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
     "-ss", ini, "-t", dur, "-i", os.path.join(pasta, "cor.mp4"),
     "-ss", ini, "-t", dur, "-i", os.path.join(pasta, "matte.mp4"),
     "-filter_complex", "[0:v]format=yuva420p[c];[1:v]format=gray[m];[c][m]alphamerge,format=yuva420p[s]",
     "-map", "[s]", "-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p", "-b:v", "8M",
     "-deadline", "good", "-cpu-used", "4", "-auto-alt-ref", "0", "-r", "30", saida],
    check=True,
)
print("pronto:", saida)
