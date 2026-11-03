"""Converte video de apoio em 1080x1920 30 fps sem audio, pronto para o motor.

Uso: preparar_midia.py <entrada> <saida.mp4> [--ini s] [--dur s] [--escuro] [--lento 0.68]

Video de WhatsApp (baixa resolucao) ganha reducao de ruido, ampliacao e nitidez.
--escuro  levanta um video escuro.
--lento   camera lenta com interpolacao (0.68 = 68% da velocidade). Fica suave, mas demora.

Nunca use em foto ou video de resultado de paciente: conselho profissional pode vedar
edicao e melhoramento dessas imagens (ver referencias/conformidade.md).
"""
import argparse
import subprocess

ap = argparse.ArgumentParser()
ap.add_argument("entrada")
ap.add_argument("saida")
ap.add_argument("--ini", default="0")
ap.add_argument("--dur")
ap.add_argument("--escuro", action="store_true")
ap.add_argument("--lento", type=float)
args = ap.parse_args()

filtros = []
if args.lento:
    filtros.append(f"setpts=PTS/{args.lento}")
    filtros.append("minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc:vsbmc=1")
if args.escuro:
    filtros.append("eq=gamma=1.6:saturation=1.2:contrast=1.2:brightness=-0.02")
filtros += [
    "hqdn3d=1.5:1.5:3:3",
    "scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos",
    "crop=1080:1920",
    "unsharp=5:5:0.75:5:5:0.0",
    "fps=30",
]
cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", args.ini, "-i", args.entrada]
if args.dur:
    cmd += ["-t", args.dur]
cmd += ["-vf", ",".join(filtros), "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "17",
        "-pix_fmt", "yuv420p", "-g", "15", "-movflags", "+faststart", args.saida]
subprocess.run(cmd, check=True)
print("pronto:", args.saida)
