"""Recorte do apresentador em video (Robust Video Matting, ONNX, local).

Uso: recortar_rvm.py <video> <saida_matte.mp4> <modelo.onnx> [inicio_s] [dur_s]
Saida: matte em tons de cinza (branco = pessoa), mesmo tamanho e fps do video.
Mantem o estado recorrente entre quadros (contorno estavel, sem tremer).
"""
import subprocess
import sys
import time

import numpy as np
import onnxruntime as ort

video, saida, modelo = sys.argv[1], sys.argv[2], sys.argv[3]
inicio = sys.argv[4] if len(sys.argv) > 4 else "0"
dur = sys.argv[5] if len(sys.argv) > 5 else None
W, H, FPS = 1080, 1920, 30

leitura = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-ss", inicio, "-i", video]
if dur:
    leitura += ["-t", dur]
leitura += ["-vf", f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
entrada = subprocess.Popen(leitura, stdout=subprocess.PIPE)
escrita = subprocess.Popen(
    ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "gray",
     "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "fast",
     "-crf", "14", "-pix_fmt", "yuv420p", saida],
    stdin=subprocess.PIPE,
)

sess = ort.InferenceSession(modelo, providers=ort.get_available_providers())
rec = [np.zeros((1, 1, 1, 1), dtype=np.float32) for _ in range(4)]
ratio = np.array([0.25], dtype=np.float32)
n, t0 = 0, time.time()
while True:
    buf = entrada.stdout.read(W * H * 3)
    if len(buf) < W * H * 3:
        break
    img = np.frombuffer(buf, dtype=np.uint8).reshape(H, W, 3).astype(np.float32) / 255.0
    src = img.transpose(2, 0, 1)[None]
    fgr, pha, *rec = sess.run(
        None,
        {"src": src, "r1i": rec[0], "r2i": rec[1], "r3i": rec[2], "r4i": rec[3],
         "downsample_ratio": ratio},
    )
    alfa = (np.clip(pha[0, 0], 0, 1) * 255).astype(np.uint8)
    escrita.stdin.write(alfa.tobytes())
    n += 1
    if n % 150 == 0:
        print(f"{n} quadros, {n / (time.time() - t0):.1f} fps", flush=True)
escrita.stdin.close()
escrita.wait()
print(f"fim: {n} quadros em {time.time() - t0:.0f}s")
