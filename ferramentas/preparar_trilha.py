"""Deixa uma trilha em -12 LUFS, o nivel que o motor espera, cobrindo a duracao do video.

Uso: preparar_trilha.py <saida.wav> <duracao_s> [--arquivo musica.mp3] [--ini s]
Sem --arquivo, sintetiza uma trilha ambiente original (trilha_ambiente.py).
Trilha curta e repetida em laco. O motor abaixa para 0,085 sob a voz e sobe para 0,24 no cartao final.
"""
import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from comum import duracao, medir_audio  # noqa: E402

ALVO = -12.0

ap = argparse.ArgumentParser()
ap.add_argument("saida")
ap.add_argument("duracao", type=float)
ap.add_argument("--arquivo")
ap.add_argument("--ini", default="0")
args = ap.parse_args()

with tempfile.TemporaryDirectory() as pasta:
    origem = args.arquivo
    if not origem:
        origem = str(Path(pasta) / "sintetica.wav")
        subprocess.run(
            [sys.executable, str(Path(__file__).with_name("trilha_ambiente.py")), origem, str(args.duracao + 3)],
            check=True,
        )
    intermediario = str(Path(pasta) / "cortada.wav")
    laco = ["-stream_loop", "-1"] if duracao(origem) - float(args.ini) < args.duracao else []
    subprocess.run(
        ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *laco, "-ss", args.ini, "-i", origem,
         "-t", str(args.duracao), "-vn", "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le", intermediario],
        check=True,
    )
    lufs, _ = medir_audio(intermediario)
    subprocess.run(
        ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", intermediario, "-af",
         f"volume={ALVO - lufs:.2f}dB,alimiter=limit=0.95:level=disabled", "-c:a", "pcm_s16le", args.saida],
        check=True,
    )
final, pico = medir_audio(args.saida)
print(f"trilha: {final:.1f} LUFS, pico {pico:.1f} dBFS, {args.duracao:.1f} s -> {args.saida}")
