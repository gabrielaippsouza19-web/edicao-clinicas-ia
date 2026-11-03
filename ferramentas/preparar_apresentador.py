"""Trata o apresentador e gera as camadas da edicao.

Uso: preparar_apresentador.py <video> <pasta_saida> [--modelo arq.onnx] [--ini s] [--dur s]
                              [--pele] [--fundo-desfocado]

Sempre gera:
  matte.mp4  recorte em cinza (Robust Video Matting), base da palavra atras da cabeca
  cor.mp4    o video em 1080x1920 30 fps com o fundo real
  enquadramento.json  altura dos olhos e centro do rosto, medidos no matte
Opcional:
  --pele             corrige manchas verdes nas altas luzes da pele (so na pessoa).
                     Use apenas se os quadros mostrarem o defeito.
  --fundo-desfocado  gera tambem fundo.jpg e base.mp4 (fundo limpo, desfocado e claro).
                     Use apenas se o cliente pedir: ha quem prefira mostrar o consultorio.

Se matte.mp4 ja existir, o recorte e pulado.
"""
import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

sys.path.insert(0, str(Path(__file__).resolve().parent))
from comum import FPS, H, MODELO_RVM, W, corrige_pele, filtro_video  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("video")
ap.add_argument("pasta")
ap.add_argument("--modelo", default=str(MODELO_RVM))
ap.add_argument("--ini", default="0")
ap.add_argument("--dur")
ap.add_argument("--pele", action="store_true")
ap.add_argument("--fundo-desfocado", action="store_true")
args = ap.parse_args()

video, pasta, ini, dur = args.video, args.pasta, args.ini, args.dur
os.makedirs(pasta, exist_ok=True)
AMOSTRA_CADA = 12
matte_mp4 = os.path.join(pasta, "matte.mp4")
filtro = filtro_video(video)


def leitor(arq, fmt="rgb24", usar_ini=True, vf=None):
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error"]
    if usar_ini:
        cmd += ["-ss", ini]
    cmd += ["-i", arq]
    if dur:
        cmd += ["-t", dur]
    cmd += ["-vf", vf or filtro, "-f", "rawvideo", "-pix_fmt", fmt, "-"]
    return subprocess.Popen(cmd, stdout=subprocess.PIPE)


def escritor(arq, fmt, crf):
    return subprocess.Popen(
        ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", fmt,
         "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium",
         "-crf", str(crf), "-pix_fmt", "yuv420p", "-g", "15", "-movflags", "+faststart", arq],
        stdin=subprocess.PIPE,
    )


# ------------------------------------------------------------------ recorte
if not os.path.exists(matte_mp4):
    import onnxruntime as ort

    sess = ort.InferenceSession(args.modelo, providers=["CPUExecutionProvider"])
    rec = [np.zeros((1, 1, 1, 1), dtype=np.float32) for _ in range(4)]
    ratio = np.array([0.25], dtype=np.float32)
    ent, sai = leitor(video), escritor(matte_mp4, "gray", 14)
    n, t0 = 0, time.time()
    while True:
        buf = ent.stdout.read(W * H * 3)
        if len(buf) < W * H * 3:
            break
        img = np.frombuffer(buf, dtype=np.uint8).reshape(H, W, 3).astype(np.float32) / 255.0
        _, pha, *rec = sess.run(
            None,
            {"src": img.transpose(2, 0, 1)[None], "r1i": rec[0], "r2i": rec[1], "r3i": rec[2],
             "r4i": rec[3], "downsample_ratio": ratio},
        )
        sai.stdin.write((np.clip(pha[0, 0], 0, 1) * 255).astype(np.uint8).tobytes())
        n += 1
        if n % 300 == 0:
            print(f"recorte: {n} quadros, {n / (time.time() - t0):.1f} fps", flush=True)
    sai.stdin.close()
    sai.wait()
    print(f"recorte pronto: {n} quadros", flush=True)

# ------------------------------------------------------------------ enquadramento medido no matte
em = leitor(matte_mp4, "gray", usar_ini=False, vf=f"scale={W}:{H},fps={FPS}")
soma, n_amostras, k = None, 0, 0
while True:
    bm = em.stdout.read(W * H)
    if len(bm) < W * H:
        break
    if k % AMOSTRA_CADA == 0:
        m = np.frombuffer(bm, dtype=np.uint8).reshape(H, W)[::4, ::4].astype(np.float32) / 255.0
        soma = m if soma is None else soma + m
        n_amostras += 1
    k += 1
em.kill()
media = soma / max(1, n_amostras)
pessoa = media > 0.5
larguras = pessoa.sum(axis=1)
linhas = np.nonzero(larguras > 0.03 * pessoa.shape[1])[0]
if len(linhas) == 0:
    enquadramento = {"olhosY": 960, "centroX": 540, "medido": False}
    print("AVISO: pessoa nao encontrada no matte; enquadramento padrao", flush=True)
else:
    topo = int(linhas[0])
    # a cabeca termina onde a largura volta a cair (pescoco) ou no limite de 35% da altura
    maximo, fim = 0, topo
    for y in range(topo, min(pessoa.shape[0], topo + int(0.35 * pessoa.shape[0]))):
        if larguras[y] > maximo:
            maximo, fim = int(larguras[y]), y
        elif larguras[y] < 0.85 * maximo:
            break
    centros = [np.nonzero(pessoa[y])[0].mean() for y in range(topo, fim + 1) if pessoa[y].any()]
    altura_cabeca = 1.35 * maximo
    enquadramento = {
        "olhosY": round((topo + 0.46 * altura_cabeca) * 4),
        "centroX": round(float(np.mean(centros)) * 4),
        "topoCabeca": topo * 4,
        "larguraCabeca": maximo * 4,
        "medido": True,
    }
with open(os.path.join(pasta, "enquadramento.json"), "w", encoding="utf-8") as f:
    json.dump(enquadramento, f, indent=1)
print("enquadramento:", enquadramento, flush=True)

# ------------------------------------------------------------------ sem --pele nem fundo: so converte
placa_final = None
if not args.pele and not args.fundo_desfocado:
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", ini, "-i", video]
    if dur:
        cmd += ["-t", dur]
    cmd += ["-vf", filtro, "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "16",
            "-pix_fmt", "yuv420p", "-g", "15", "-movflags", "+faststart", os.path.join(pasta, "cor.mp4")]
    subprocess.run(cmd, check=True)
    print("pronto: cor.mp4", flush=True)
    sys.exit(0)

# ------------------------------------------------------------------ fundo limpo (opcional)
if args.fundo_desfocado:
    fundo_jpg = os.path.join(pasta, "fundo.jpg")
    ec, em = leitor(video), leitor(matte_mp4, "gray", usar_ini=False, vf=f"scale={W}:{H},fps={FPS}")
    pilha, mascaras, k = [], [], 0
    while True:
        bc = ec.stdout.read(W * H * 3)
        bm = em.stdout.read(W * H)
        if len(bc) < W * H * 3 or len(bm) < W * H:
            break
        if k % AMOSTRA_CADA == 0:
            pilha.append(
                np.asarray(Image.frombytes("RGB", (W, H), bc).resize((270, 480), Image.BILINEAR),
                           dtype=np.float32)
            )
            m = Image.frombytes("L", (W, H), bm).filter(ImageFilter.MaxFilter(9))
            mascaras.append(np.asarray(m.resize((270, 480), Image.BILINEAR), dtype=np.float32) / 255.0)
        k += 1
    ec.kill()
    em.kill()
    pilha = np.stack(pilha)
    livre = np.stack(mascaras)[..., None] < 0.05
    pilha[~np.repeat(livre, 3, axis=3)] = np.nan
    limpo = np.nanmedian(pilha, axis=0)
    # preenche o que ficou sempre atras da pessoa com desfoque progressivo
    buraco = np.isnan(limpo[..., 0])
    if buraco.any():
        cor_media = np.nanmean(limpo, axis=(0, 1))
        preench = np.where(np.isnan(limpo), cor_media, limpo)
        for raio in (40, 20, 10):
            borrado = np.asarray(
                Image.fromarray(preench.astype(np.uint8)).filter(ImageFilter.GaussianBlur(raio)),
                dtype=np.float32,
            )
            preench[buraco] = borrado[buraco]
        limpo = preench
    placa = Image.fromarray(limpo.astype(np.uint8)).resize((W, H), Image.BICUBIC)
    placa = placa.filter(ImageFilter.GaussianBlur(30))
    p = np.asarray(placa, dtype=np.float32) / 255.0
    # clareia e aquece (fundo cremoso, como lente clara): gama + mistura com creme
    p = np.power(p, 0.72)
    cinza = p.mean(axis=2, keepdims=True)
    p = cinza + (p - cinza) * 0.8
    creme = np.array([0.97, 0.93, 0.87], dtype=np.float32)
    p = p * 0.68 + creme * 0.32
    placa_final = np.clip(p, 0, 1)
    Image.fromarray((placa_final * 255).astype(np.uint8)).save(fundo_jpg, quality=95)
    print("fundo pronto", flush=True)

# ------------------------------------------------------------------ pele + composicao
ec, em = leitor(video), leitor(matte_mp4, "gray", usar_ini=False, vf=f"scale={W}:{H},fps={FPS}")
sc = escritor(os.path.join(pasta, "cor.mp4"), "rgb24", 16)
sb = escritor(os.path.join(pasta, "base.mp4"), "rgb24", 16) if placa_final is not None else None
n, t0 = 0, time.time()
while True:
    bc = ec.stdout.read(W * H * 3)
    bm = em.stdout.read(W * H)
    if len(bc) < W * H * 3 or len(bm) < W * H:
        break
    rgb = np.frombuffer(bc, dtype=np.uint8).reshape(H, W, 3).astype(np.float32) / 255.0
    alfa = np.frombuffer(bm, dtype=np.uint8).reshape(H, W).astype(np.float32) / 255.0
    cor = corrige_pele(rgb, alfa) if args.pele else rgb
    if sb is not None:
        base = cor * alfa[..., None] + placa_final * (1 - alfa[..., None])
        sb.stdin.write((base * 255).astype(np.uint8).tobytes())
    sc.stdin.write((cor * 255).astype(np.uint8).tobytes())
    n += 1
    if n % 300 == 0:
        print(f"composicao: {n} quadros, {n / (time.time() - t0):.1f} fps", flush=True)
sc.stdin.close()
sc.wait()
if sb is not None:
    sb.stdin.close()
    sb.wait()
print(f"pronto: {n} quadros", flush=True)
