"""Limpa a voz do bruto e deixa em -16 LUFS, com ganho fixo e limitador.

Uso: preparar_voz.py <video> <saida.wav> [--ini s] [--dur s]
Ganho fixo, nao loudnorm: o loudnorm entra em modo dinamico e sobe o que nao deve.
"""
import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from comum import medir_audio  # noqa: E402

ALVO = -16.0
CADEIA = (
    "aresample=async=1:first_pts=0,highpass=f=90,afftdn=nr=12:nf=-42,"
    "equalizer=f=230:t=q:w=1.2:g=-1.5,equalizer=f=3400:t=q:w=1.6:g=2.2,"
    "equalizer=f=9000:t=q:w=1.5:g=1.2,"
    "acompressor=threshold=-24dB:ratio=2.6:attack=8:release=140:makeup=4dB"
)

ap = argparse.ArgumentParser()
ap.add_argument("video")
ap.add_argument("saida")
ap.add_argument("--ini", default="0")
ap.add_argument("--dur")
args = ap.parse_args()

entrada = ["-ss", args.ini, "-i", args.video] + (["-t", args.dur] if args.dur else [])
intermediario = args.saida + ".tmp.wav"
subprocess.run(
    ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *entrada, "-vn", "-af", CADEIA,
     "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le", intermediario],
    check=True,
)
lufs, _ = medir_audio(intermediario)
ganho = ALVO - lufs
subprocess.run(
    ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", intermediario, "-af",
     f"volume={ganho:.2f}dB,alimiter=limit=0.9:level=disabled", "-c:a", "pcm_s16le", args.saida],
    check=True,
)
Path(intermediario).unlink()
final, pico = medir_audio(args.saida)
print(f"voz: {final:.1f} LUFS, pico {pico:.1f} dBFS -> {args.saida}")
