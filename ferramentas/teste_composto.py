"""Compoe um quadro do video + matte sobre fundo claro e escuro, para revisar o contorno.

Uso: teste_composto.py <video> <matte> <t_video> <t_matte> <saida.jpg>
"""
import subprocess
import sys

from PIL import Image

video, matte, tv, tm, saida = sys.argv[1:6]


def quadro(arq, t, nome):
    subprocess.run(
        ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", t, "-i", arq,
         "-frames:v", "1", "-vf", "scale=1080:1920", nome],
        check=True,
    )
    return Image.open(nome)


c = quadro(video, tv, saida + ".c.png").convert("RGB")
m = quadro(matte, tm, saida + ".m.png").convert("L")
claro = Image.composite(c, Image.new("RGB", c.size, (233, 226, 214)), m)
escuro = Image.composite(c, Image.new("RGB", c.size, (20, 20, 22)), m)
caixa = (0, 620, 1080, 1920)
folha = Image.new("RGB", (2160, 1300))
folha.paste(claro.crop(caixa), (0, 0))
folha.paste(escuro.crop(caixa), (1080, 0))
folha.thumbnail((1800, 1100))
folha.save(saida, quality=90)
