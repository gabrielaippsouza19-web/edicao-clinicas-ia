"""Gera o material ficticio do video de demonstracao do kit. Nenhuma pessoa real.

Uso: gerar_demo.py
Escreve em template/public e template/src/videos/demo. Passa pelas mesmas ferramentas
de um video real, menos a transcricao e o recorte: aqui o matte vem do proprio desenho.
"""
import shutil
import subprocess
import sys
import tempfile
import wave
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
from comum import TEMPLATE  # noqa: E402

AQUI = Path(__file__).resolve().parent
publico = TEMPLATE / "public"
demo = publico / "demo"
banco = publico / "banco"
fonte_ts = TEMPLATE / "src/videos/demo"
for p in (demo, banco, publico / "audio/sfx"):
    p.mkdir(parents=True, exist_ok=True)

DUR, FPS, SR = 18.0, 30, 48000
BLOCOS = [(0.5, 4.5), (5.5, 9.0), (10.0, 13.0), (14.0, 17.3)]  # trechos de "fala"


def ferramenta(nome, *resto):
    subprocess.run([sys.executable, str(AQUI / nome), *[str(x) for x in resto]], check=True)


def desenhar(dx):
    """Devolve (cena, mascara) em 270x480: sala clara e uma figura esquematica."""
    alt = np.linspace(0, 1, 480)[:, None, None]
    fundo = (np.array([214, 200, 182]) * (1 - alt) + np.array([150, 132, 114]) * alt).astype(np.uint8)
    cena = Image.fromarray(np.repeat(fundo, 270, axis=1))
    d = ImageDraw.Draw(cena)
    d.rectangle([18, 60, 78, 300], fill=(190, 170, 146))
    d.rectangle([196, 90, 256, 330], fill=(172, 152, 130))
    d.rectangle([0, 400, 270, 480], fill=(128, 108, 92))
    mascara = Image.new("L", (270, 480), 0)
    m = ImageDraw.Draw(mascara)
    cx = 135 + dx
    for alvo, pele, roupa in ((d, (226, 186, 158), (58, 62, 74)), (m, 255, 255)):
        alvo.rounded_rectangle([cx - 78, 250, cx + 78, 480], radius=40, fill=roupa)
        alvo.rectangle([cx - 16, 222, cx + 16, 262], fill=pele)
        alvo.ellipse([cx - 42, 130, cx + 42, 234], fill=pele)
    d.ellipse([cx - 22, 178, cx - 12, 186], fill=(40, 30, 28))
    d.ellipse([cx + 12, 178, cx + 22, 186], fill=(40, 30, 28))
    d.arc([cx - 14, 202, cx + 14, 220], 20, 160, fill=(150, 80, 80), width=2)
    return cena, mascara.filter(ImageFilter.GaussianBlur(0.6))


with tempfile.TemporaryDirectory() as pasta:
    pasta = Path(pasta)
    camadas = pasta / "camadas"
    camadas.mkdir()

    # ---- "voz": zumbido com silabas, so para os cortes terem o que medir
    n = int(DUR * SR)
    t = np.arange(n) / SR
    onda = sum(np.sin(2 * np.pi * 150 * h * t) / h for h in range(1, 6))
    onda = onda * (0.55 + 0.45 * np.sin(2 * np.pi * 4.3 * t))
    ganho = np.zeros(n)
    for a, b in BLOCOS:
        ganho[int(a * SR):int(b * SR)] = 0.12
    rng = np.random.default_rng(3)
    x = np.clip(onda * ganho + rng.standard_normal(n) * 0.0002, -1, 1)
    voz_bruta = pasta / "voz.wav"
    with wave.open(str(voz_bruta), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((x * 32767).astype(np.int16).tobytes())

    # ---- bruto e matte
    bruto = pasta / "bruto.mp4"
    comum_saida = ["-c:v", "libx264", "-preset", "veryfast", "-crf", "16", "-pix_fmt", "yuv420p", "-g", "15"]
    v = subprocess.Popen(
        ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
         "-s", "270x480", "-r", str(FPS), "-i", "-", "-i", str(voz_bruta), "-vf", "scale=1080:1920:flags=bicubic",
         *comum_saida, "-c:a", "aac", "-shortest", str(bruto)],
        stdin=subprocess.PIPE,
    )
    m = subprocess.Popen(
        ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "gray",
         "-s", "270x480", "-r", str(FPS), "-i", "-", "-vf", "scale=1080:1920:flags=bicubic",
         *comum_saida, str(camadas / "matte.mp4")],
        stdin=subprocess.PIPE,
    )
    for k in range(int(DUR * FPS)):
        cena, mascara = desenhar(round(4 * np.sin(k / 22)))
        v.stdin.write(cena.tobytes())
        m.stdin.write(mascara.tobytes())
    v.stdin.close()
    m.stdin.close()
    v.wait()
    m.wait()

    # ---- mesmas ferramentas de um video real
    transcricao = pasta / "transcricao.json"
    transcricao.write_text('{"segmentos": []}', encoding="utf-8")
    ferramenta("montar_edl.py", bruto, transcricao, fonte_ts / "edl.json")
    ferramenta("preparar_apresentador.py", bruto, camadas)
    shutil.copy2(camadas / "cor.mp4", demo / "apresentador.mp4")
    shutil.copy2(camadas / "enquadramento.json", fonte_ts / "enquadramento.json")
    ferramenta("preparar_voz.py", bruto, demo / "voz.wav")
    ferramenta("preparar_trilha.py", demo / "trilha.wav", 24)
    ferramenta("efeitos_sonoros.py", publico / "audio/sfx")
    ferramenta("clipe_alpha.py", camadas, 0.6, 2.7, demo / "fg-a.webm")
    ferramenta("capa_quadro.py", bruto, 2, demo / "capa.png")

# ---- fotos e videos de apoio ficticios
fonte = ImageFont.load_default(64)
for nome, c1, c2 in (("caso-a", (120, 150, 170), (60, 80, 110)), ("caso-b", (176, 140, 120), (110, 70, 60)),
                     ("caso-c", (140, 170, 130), (70, 100, 70))):
    alt = np.linspace(0, 1, 900)[:, None, None]
    grad = (np.array(c1) * (1 - alt) + np.array(c2) * alt).astype(np.uint8)
    im = Image.fromarray(np.repeat(grad, 900, axis=1))
    ImageDraw.Draw(im).text((450, 450), "Imagem\nde exemplo", fill="white", font=fonte, anchor="mm", align="center")
    im.save(demo / f"{nome}.jpg", quality=90)
for arq, c0, c1 in ((demo / "ambiente-a.mp4", "0x8a7a66", "0x3e3a44"), (banco / "demo-ambiente-b.mp4", "0x46657f", "0x223344")):
    subprocess.run(
        ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "lavfi", "-i",
         f"gradients=s=1080x1920:c0={c0}:c1={c1}:x0=0:y0=0:x1=1080:y1=1920:speed=0.03:rate=30",
         "-t", "6", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", "-g", "15", str(arq)],
        check=True,
    )
print("demonstracao pronta")
